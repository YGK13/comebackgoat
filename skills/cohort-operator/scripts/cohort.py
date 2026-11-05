#!/usr/bin/env python3
"""Comeback GOAT cohort operator: the coach-side state machine.

Everything the coach's Claude needs to run a cohort with no memory between
sessions lives in one ops folder:

  ops/cohort.yaml   settings (booking link, WhatsApp, payment links, Day 1)
  ops/roster.csv    one row per applicant or participant
  ops/reports.csv   one row per daily report a participant sent
  ops/drafted.csv   every email Claude drafted, so nothing is drafted twice

Commands (all print JSON with --json, readable text otherwise):
  init     OPS [--day1 YYYY-MM-DD]          create the ops folder
  ingest   OPS FILE.json                    add new applications (list of dicts)
  screen   OPS                              score unscreened applicants
  set      OPS EMAIL key=value ...          update one roster row
  reports  OPS FILE.json                    add daily reports [{email,date,body}]
  today    OPS [--date D]                   health, drafts due, cohort board
  render   OPS TEMPLATE EMAIL [--date D]    fill one email (S1, Day 4, T2, G1...)
  mark     OPS EMAIL TEMPLATE [--date D]    record that a draft was created

The script never sends anything. It decides what is due and fills templates;
Claude creates Gmail drafts and the coach presses Send.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML ships with the skill runtime
    sys.exit("PyYAML is required: pip install pyyaml")

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATES_MD = SKILL / "references" / "email-sequence.md"
CONFIG_TEMPLATE = SKILL / "references" / "cohort.yaml"

ROSTER_COLS = [
    "email", "name", "first_name", "linkedin", "situation", "role", "goal",
    "applied_at", "screen_score", "screen_flags", "recommendation", "status",
    "payment_plan", "paid_at", "second_paid", "kickoff_booked", "ready",
    "day1", "days_off", "tracker_url", "tracker_shared", "notes",
]
REPORT_COLS = [
    "email", "date", "day", "streak", "sent_today", "total_sent", "replies",
    "calls", "offers", "money", "stuck", "tracker", "feedback",
]
DRAFT_COLS = ["email", "template", "date"]
STATUSES = ["applied", "accepted", "declined", "paid", "ready", "active",
            "completed", "withdrawn"]
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Cumulative "sent" the protocol expects by the end of each sprint day.
CUMULATIVE_TARGET = {4: 5, 5: 12, 6: 12, 7: 12, 8: 17, 9: 19, 10: 20,
                     11: 22, 12: 24, 13: 25, 14: 25}
SPRINT_LEN = 14


# ---------------------------------------------------------------- storage

def read_csv(path: Path, cols: list[str]) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return [{c: (row.get(c) or "") for c in cols} for row in csv.DictReader(fh)]


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def load_config(ops: Path) -> dict:
    path = ops / "cohort.yaml"
    if not path.exists():
        sys.exit(f"{path} not found: run `cohort.py init {ops}` first")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


# ---------------------------------------------------------------- calendar

def working_days(cfg: dict, person: dict | None = None) -> set[int]:
    names = (cfg.get("cohort") or {}).get("working_days") or DAY_NAMES[:5]
    days = {DAY_NAMES.index(n[:3].title()) for n in names if n[:3].title() in DAY_NAMES}
    if person and person.get("days_off"):
        for n in re.split(r"[;, ]+", person["days_off"]):
            if n[:3].title() in DAY_NAMES:
                days.discard(DAY_NAMES.index(n[:3].title()))
    return days or {0, 1, 2, 3, 4}


def coach_days(cfg: dict) -> set[int]:
    names = (cfg.get("coach") or {}).get("working_days") or ["Sun", "Mon", "Tue", "Wed", "Thu"]
    return {DAY_NAMES.index(n[:3].title()) for n in names if n[:3].title() in DAY_NAMES}


def day1_of(cfg: dict, person: dict) -> date | None:
    return parse_date(person.get("day1")) or parse_date((cfg.get("cohort") or {}).get("day1"))


def sprint_day(cfg: dict, person: dict, on: date) -> int | None:
    """Sprint day number on a date: 1 on Day 1, counting only working days.

    Returns None before Day 1 or on a day off; numbers past 14 mean the
    sprint is over (15 is the first working day after Day 14)."""
    start = day1_of(cfg, person)
    wd = working_days(cfg, person)
    if not start or on < start or on.weekday() not in wd:
        return None
    n, d = 0, start
    while d <= on:
        if d.weekday() in wd:
            n += 1
        d += timedelta(days=1)
    return n


def date_of_day(cfg: dict, person: dict, n: int) -> date | None:
    start = day1_of(cfg, person)
    if not start:
        return None
    wd = working_days(cfg, person)
    d, count = start, 0
    while True:
        if d.weekday() in wd:
            count += 1
            if count == n:
                return d
        d += timedelta(days=1)


def previous_working_days(cfg: dict, person: dict, on: date, k: int) -> list[date]:
    wd, out, d = working_days(cfg, person), [], on - timedelta(days=1)
    start = day1_of(cfg, person)
    while len(out) < k and start and d >= start:
        if d.weekday() in wd:
            out.append(d)
        d -= timedelta(days=1)
    return out


# ---------------------------------------------------------------- screening

SENIOR_RE = re.compile(
    r"\b(chief|c[a-z]o|cxo|vp|svp|evp|vice president|head|director|partner|"
    r"founder|co-founder|general manager|gm|managing director|principal|president)\b", re.I)
RED_FLAG_RE = re.compile(
    r"(guarantee|done for me|do it for me|do everything for me|lawsuit|suing|"
    r"no outreach|won't contact|hate ai|don't trust ai)", re.I)
GOOD_SITUATIONS = {
    "laid off in the last 6 months": 25, "laid off 6 to 18 months ago": 25,
    "left by choice": 25, "still employed, planning my exit": 20,
    "already solo, need pipeline": 20,
}


def screen_one(row: dict) -> tuple[int, list[str], str]:
    score, flags = 0, []
    score += GOOD_SITUATIONS.get(row.get("situation", "").strip().lower(), 10)
    if SENIOR_RE.search(row.get("role", "")):
        score += 30
    else:
        flags.append("seniority unclear")
    goal = row.get("goal", "").strip()
    if len(goal) >= 40:
        score += 25
    elif goal:
        score += 10
        flags.append("goal is thin")
    else:
        flags.append("no 90-day goal")
    if "linkedin.com/in/" in row.get("linkedin", "").lower():
        score += 20
    else:
        flags.append("no LinkedIn URL")
    text = " ".join(row.get(k, "") for k in ("goal", "role", "situation"))
    if RED_FLAG_RE.search(text):
        flags.append("red flag wording: read in full")
        score = min(score, 40)
    rec = "accept" if score >= 70 else "clarify" if score >= 45 else "decline"
    return score, flags, rec


# ---------------------------------------------------------------- reports

FIELD_RES = {
    "day": r"Day\s+(\d+)\s+of\s+14",
    "streak": r"Streak\W{0,3}(\d+)",
    "sent_today": r"Sent today:\s*(\d+)",
    "total_sent": r"Total sent:\s*(\d+)",
    "replies": r"Replies(?: received)?:\s*(\d+)",
    "calls": r"Calls booked:\s*(\d+)",
    "offers": r"Offers sent:\s*(\d+)",
    "money": r"Money found or collected:\s*([^\n]*)",
    "stuck": r"Stuck on:\s*([^\n]*)",
    "tracker": r"Tracker:\s*(\S+)",
    "feedback": r"Feedback please:\s*([^\n]*)",
}


def parse_report(body: str) -> dict:
    out = {}
    for key, rx in FIELD_RES.items():
        m = re.search(rx, body, re.I)
        out[key] = m.group(1).strip() if m else ""
    for key in ("stuck", "money", "feedback"):
        if out[key].lower().strip(" .\"'") in {"nothing", "none", "n/a", "-", ""}:
            out[key] = ""
    if out["tracker"].lower().strip(" .\"'") in {"not", "not shared", "none"}:
        out["tracker"] = ""
    return out


def as_int(v: str) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------- templates

def load_templates() -> dict[str, dict]:
    """Parse email-sequence.md into {id: {subject, body, kind}}."""
    text = TEMPLATES_MD.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    for m in re.finditer(r"^### (.+?)\n(.*?)(?=^### |^---\s*$|^## |\Z)", text, re.S | re.M):
        head, block = m.group(1).strip(), m.group(2)
        hm = re.match(r"(Day \d+|[A-Z]\d+)\.", head)
        if not hm:
            continue
        tid = hm.group(1)
        subj = re.search(r"^\*\*Subject:\*\*\s*(.+)$", block, re.M)
        lines = [ln for ln in block.splitlines()
                 if not ln.startswith("**Subject:**") and not ln.strip().startswith("*(")]
        body = "\n".join(lines).strip()
        kind = "whatsapp" if tid.startswith("G") else "email"
        if kind == "whatsapp":
            body = "\n".join(ln[2:] if ln.startswith("> ") else ln.lstrip(">")
                             for ln in body.splitlines()).strip()
        out[tid] = {"subject": subj.group(1).strip() if subj else "", "body": body, "kind": kind}
    return out


def links(cfg: dict) -> dict[str, str]:
    coach = cfg.get("coach") or {}
    pay = cfg.get("payment") or {}
    num = re.sub(r"\D", "", str(coach.get("whatsapp_dm_number", "")))
    return {
        "BOOKING_URL": str(coach.get("booking_url", "SET_ME")),
        "WHATSAPP_GROUP_LINK": str(coach.get("whatsapp_group_invite", "SET_ME")),
        "WHATSAPP_DM_LINK": f"https://wa.me/{num}" if num else "SET_ME",
        "PAY_FULL_LINK": str(pay.get("full_link", "SET_ME")),
        "PAY_PLAN_LINK": str(pay.get("plan_link", "SET_ME")),
        "KIT_LINK": str((cfg.get("kit") or {}).get("link", "SET_ME")),
    }


def render(cfg: dict, tid: str, person: dict | None, on: date) -> dict:
    tpl = load_templates().get(tid)
    if not tpl:
        raise SystemExit(f"unknown template {tid!r}; known: {', '.join(load_templates())}")
    person = person or {}
    first = person.get("first_name") or (person.get("name", "").split() or ["there"])[0]
    d1 = day1_of(cfg, person) if person else parse_date((cfg.get("cohort") or {}).get("day1"))
    values = dict(links(cfg))
    values["FIRST_NAME"] = first
    values["DAY1_DATE"] = f"{d1:%A, %B} {d1.day}" if d1 else "SET_ME"
    body = tpl["body"]
    subject = tpl["subject"]
    if tid.startswith("Day "):
        body = (f"Hi {first},\n\n{body}\n\nQuestions: the group ({values['WHATSAPP_GROUP_LINK']}). "
                f"Private: WhatsApp me ({values['WHATSAPP_DM_LINK']}).\nYuri")
    if tid in ("T1",) and person:
        n = sprint_day(cfg, person, on) or ""
        subject = subject.replace("[n]", str(n))
    if tpl["kind"] == "email":
        body = body.replace("**", "")  # plain-text email: markdown bold would show as asterisks
    raw = subject + "\n" + body
    unset = sorted(k for k, v in values.items() if v == "SET_ME" and "{{" + k + "}}" in raw)
    for k, v in values.items():
        body = body.replace("{{" + k + "}}", v)
        subject = subject.replace("{{" + k + "}}", v)
    unset += sorted(set(re.findall(r"\{\{([A-Z_0-9]+)\}\}", body)))
    return {"template": tid, "kind": tpl["kind"], "to": person.get("email", ""),
            "subject": subject, "body": body, "unset": unset,
            # S2 carries a bracketed sentence only the coach can write.
            "needs_edit": bool(re.search(r"\[(one honest|Optional)", body))}


# ---------------------------------------------------------------- today

def health(cfg: dict, person: dict, reports: list[dict], on: date) -> tuple[str, list[str]]:
    mine = {r["date"]: r for r in reports if r["email"].lower() == person["email"].lower()}
    day = sprint_day(cfg, person, on)
    if not day or day < 2:
        return "green", []
    prev = previous_working_days(cfg, person, on, 2)
    reasons: list[str] = []
    last = mine.get(prev[0].isoformat()) if prev else None
    before = mine.get(prev[1].isoformat()) if len(prev) > 1 else None
    if not last and not before and len(prev) >= 2:
        return "red", ["no report for 2 working days"]
    status = "green"
    if not last:
        status, reasons = "yellow", ["no report yesterday"]
    recent = [r for r in (last, before) if r]
    if len(recent) == 2 and all(r["stuck"] for r in recent):
        return "red", ["stuck two days running: " + recent[0]["stuck"]]
    if (len(recent) == 2 and all(as_int(r["day"]) >= 4 for r in recent)
            and all(as_int(r["sent_today"]) == 0 for r in recent)):
        return "red", ["no money move for 2 working days"]
    latest = max(mine.values(), key=lambda r: r["date"], default=None)
    if latest and as_int(latest["total_sent"]) >= 15 and as_int(latest["replies"]) == 0:
        return "red", ["0 replies after 15+ sends: check message and targets"]
    if last:
        target = CUMULATIVE_TARGET.get(as_int(last["day"]))
        if target and as_int(last["total_sent"]) < target:
            status = "yellow"
            reasons.append(f"behind: {last['total_sent'] or 0} sent vs {target} by Day {last['day']}")
    return status, reasons


def mission_dates(cfg: dict, person: dict, on: date) -> list[tuple[int, date]]:
    """Sprint days whose morning email should be drafted on this run.

    Today if it is a sprint day, plus following sprint days that land on the
    coach's days off (drafted early for Gmail Schedule send)."""
    out = []
    cd = coach_days(cfg)
    d = on
    for i in range(7):
        n = sprint_day(cfg, person, d)
        if i > 0 and d.weekday() in cd:
            break
        if n and 1 <= n <= SPRINT_LEN:
            out.append((n, d))
        d += timedelta(days=1)
    return out


def today(ops: Path, on: date) -> dict:
    cfg = load_config(ops)
    roster = read_csv(ops / "roster.csv", ROSTER_COLS)
    reports = read_csv(ops / "reports.csv", REPORT_COLS)
    drafted = {(r["email"].lower(), r["template"]) for r in read_csv(ops / "drafted.csv", DRAFT_COLS)}
    is_coach_day = on.weekday() in coach_days(cfg)
    due: list[dict] = []
    people: list[dict] = []
    pipeline = {s: 0 for s in STATUSES}

    def want(person: dict, tid: str, when: date | None = None, why: str = "") -> None:
        if (person["email"].lower(), tid) in drafted:
            return
        item = {"email": person["email"], "name": person["name"], "template": tid, "why": why}
        if when and when != on:
            item["schedule_send"] = when.isoformat() + " 07:00 participant time"
        due.append(item)

    for p in roster:
        st = p["status"] or "applied"
        pipeline[st] = pipeline.get(st, 0) + 1
        if st == "applied" and p["recommendation"]:
            tid = {"accept": "S1", "decline": "S2"}.get(p["recommendation"])
            if tid:
                want(p, tid, why=f"screened {p['screen_score']}: {p['recommendation']} (coach confirms)")
        if st == "paid":
            want(p, "S3", why="payment received")
            d1 = day1_of(cfg, p)
            if d1 and p["ready"] != "yes" and (d1 - on).days in (1, 2, 3) and on < d1:
                want(p, "S4", why="no 'ready' yet and Day 1 is close")
        if st in ("paid", "ready", "active"):
            day = sprint_day(cfg, p, on)
            if day and st != "active":
                p["status"] = st = "active"
            if st == "active":
                if day and day > SPRINT_LEN:
                    want(p, "D15", why="sprint finished; send after the review call")
                    d14 = date_of_day(cfg, p, SPRINT_LEN)
                    if d14 and on >= d14 + timedelta(days=30):
                        want(p, "D30", why="30 days after Day 14")
                for n, d in mission_dates(cfg, p, on):
                    want(p, f"Day {n}", d, why=f"sprint Day {n} mission")
                status, reasons = (health(cfg, p, reports, on) if not day or day <= SPRINT_LEN
                                   else ("done", []))
                if status == "yellow":
                    want(p, "T1", why="; ".join(reasons))
                elif status == "red":
                    want(p, "T2", why="; ".join(reasons))
                if day == 7 and p["payment_plan"] == "yes" and p["second_paid"] != "yes":
                    want(p, "T3", why="second installment due")
                mine = sorted((r for r in reports if r["email"].lower() == p["email"].lower()),
                              key=lambda r: r["date"])
                last = mine[-1] if mine else {}
                people.append({
                    "name": p["name"], "email": p["email"], "day": day, "status": status,
                    "reasons": reasons, "total_sent": last.get("total_sent", ""),
                    "replies": last.get("replies", ""), "calls": last.get("calls", ""),
                    "offers": last.get("offers", ""), "streak": last.get("streak", ""),
                    "stuck": last.get("stuck", ""), "feedback": last.get("feedback", ""),
                    "tracker": last.get("tracker", "") or p["tracker_url"],
                })
    write_csv(ops / "roster.csv", ROSTER_COLS, roster)

    group_posts = []
    any_active = [x for x in people if x["day"]]
    if any_active:
        days = {x["day"] for x in any_active}
        if on.weekday() == 0:
            group_posts.append("G1")
        if on.weekday() == 3:
            group_posts.append("G2")
        for n, g in ((7, "G3"), (13, "G4"), (14, "G5")):
            if n in days:
                group_posts.append(g)
    wins = [f"{x['name']}: {x['offers']} offer(s) sent" for x in people if as_int(x["offers"]) > 0]
    wins += [f"{x['name']}: {x['calls']} call(s) booked" for x in people if as_int(x["calls"]) > 0]
    return {"date": on.isoformat(), "coach_day": is_coach_day, "pipeline": pipeline,
            "people": people, "drafts_due": due, "group_posts": group_posts, "wins": wins,
            "feedback_requests": [x for x in people if x["feedback"]]}


def board_text(t: dict) -> str:
    lines = [f"COHORT BOARD · {t['date']}" + ("" if t["coach_day"] else " (your day off: nothing needs you)")]
    lines.append("Pipeline: " + ", ".join(f"{k} {v}" for k, v in t["pipeline"].items() if v))
    if t["people"]:
        lines.append("")
        lines.append("| Who | Day | Status | Sent | Replies | Calls | Offers | Streak | Stuck |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for x in t["people"]:
            lines.append(f"| {x['name']} | {x['day'] or '-'} | {x['status']} | {x['total_sent']} | "
                         f"{x['replies']} | {x['calls']} | {x['offers']} | {x['streak']} | {x['stuck'] or '-'} |")
    if t["wins"]:
        lines += ["", "Wins to celebrate in the group: " + "; ".join(t["wins"])]
    for x in t["feedback_requests"]:
        lines.append(f"Feedback asked: {x['name']}: {x['feedback']} ({x['tracker'] or 'no tracker link'})")
    if t["drafts_due"]:
        lines += ["", "Drafts to create:"]
        for d in t["drafts_due"]:
            extra = f" [schedule send {d['schedule_send']}]" if d.get("schedule_send") else ""
            lines.append(f"- {d['template']} to {d['name']} <{d['email']}>: {d['why']}{extra}")
    if t["group_posts"]:
        lines.append("WhatsApp group posts to paste today: " + ", ".join(t["group_posts"]))
    return "\n".join(lines)


# ---------------------------------------------------------------- commands

def find(roster: list[dict], email: str) -> dict:
    for r in roster:
        if r["email"].lower() == email.lower():
            return r
    raise SystemExit(f"{email} is not on the roster")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["init", "ingest", "screen", "set", "reports", "today", "render", "mark"])
    ap.add_argument("ops", type=Path)
    ap.add_argument("args", nargs="*")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--day1", help="Day 1 for init")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    on = parse_date(a.date) or date.today()
    ops: Path = a.ops

    if a.command == "init":
        ops.mkdir(parents=True, exist_ok=True)
        cfg_path = ops / "cohort.yaml"
        if not cfg_path.exists():
            text = CONFIG_TEMPLATE.read_text(encoding="utf-8")
            if a.day1:
                text = re.sub(r'day1: "[^"]*"', f'day1: "{a.day1}"', text)
            cfg_path.write_text(text, encoding="utf-8")
        for name, cols in (("roster.csv", ROSTER_COLS), ("reports.csv", REPORT_COLS), ("drafted.csv", DRAFT_COLS)):
            if not (ops / name).exists():
                write_csv(ops / name, cols, [])
        print(f"ops folder ready: {ops}")
        return 0

    roster = read_csv(ops / "roster.csv", ROSTER_COLS)
    cfg = load_config(ops)

    if a.command == "ingest":
        items = json.loads(Path(a.args[0]).read_text(encoding="utf-8"))
        known = {r["email"].lower() for r in roster}
        added = []
        for it in items if isinstance(items, list) else [items]:
            email = str(it.get("email", "")).strip()
            if not email or email.lower() in known:
                continue
            row = {c: str(it.get(c, "")).strip() for c in ROSTER_COLS}
            row["email"], row["status"] = email, "applied"
            row["applied_at"] = str(it.get("received_at", it.get("applied_at", "")))[:10]
            row["first_name"] = row["first_name"] or (row["name"].split() or [""])[0]
            roster.append(row)
            known.add(email.lower())
            added.append(email)
        write_csv(ops / "roster.csv", ROSTER_COLS, roster)
        print(json.dumps({"added": added}, indent=2))
        return 0

    if a.command == "screen":
        out = []
        for r in roster:
            if r["status"] == "applied" and not r["screen_score"]:
                s, flags, rec = screen_one(r)
                r["screen_score"], r["screen_flags"], r["recommendation"] = str(s), "; ".join(flags), rec
                out.append({"name": r["name"], "email": r["email"], "score": s, "flags": flags, "recommendation": rec})
        write_csv(ops / "roster.csv", ROSTER_COLS, roster)
        print(json.dumps(out, indent=2) if a.json else "\n".join(
            f"{o['score']:>3}  {o['recommendation']:<8} {o['name']} <{o['email']}>  {'; '.join(o['flags'])}" for o in out)
            or "nothing new to screen")
        return 0

    if a.command == "set":
        row = find(roster, a.args[0])
        for kv in a.args[1:]:
            k, _, v = kv.partition("=")
            if k not in ROSTER_COLS:
                raise SystemExit(f"unknown field {k}")
            if k == "status" and v not in STATUSES:
                raise SystemExit(f"status must be one of {STATUSES}")
            row[k] = v
        write_csv(ops / "roster.csv", ROSTER_COLS, roster)
        print(json.dumps(row, indent=2))
        return 0

    if a.command == "reports":
        items = json.loads(Path(a.args[0]).read_text(encoding="utf-8"))
        existing = read_csv(ops / "reports.csv", REPORT_COLS)
        seen = {(r["email"].lower(), r["day"]) for r in existing}
        added = []
        for it in items:
            parsed = parse_report(it.get("body", ""))
            email = str(it.get("email", "")).strip()
            if not parsed["day"] or (email.lower(), parsed["day"]) in seen:
                continue
            row = {"email": email, "date": str(it.get("date", ""))[:10], **parsed}
            existing.append(row)
            seen.add((email.lower(), parsed["day"]))
            added.append(f"{email} Day {parsed['day']}")
            try:
                p = find(roster, email)
                if parsed["tracker"] and not p["tracker_url"]:
                    p["tracker_url"], p["tracker_shared"] = parsed["tracker"], "yes"
            except SystemExit:
                pass
        write_csv(ops / "reports.csv", REPORT_COLS, existing)
        write_csv(ops / "roster.csv", ROSTER_COLS, roster)
        print(json.dumps({"added": added}, indent=2))
        return 0

    if a.command == "today":
        t = today(ops, on)
        print(json.dumps(t, indent=2) if a.json else board_text(t))
        return 0

    if a.command == "render":
        tid, email = a.args[0], (a.args[1] if len(a.args) > 1 else "")
        person = find(roster, email) if email else None
        print(json.dumps(render(cfg, tid, person, on), indent=2, ensure_ascii=False))
        return 0

    if a.command == "mark":
        rows = read_csv(ops / "drafted.csv", DRAFT_COLS)
        rows.append({"email": a.args[0], "template": a.args[1], "date": on.isoformat()})
        write_csv(ops / "drafted.csv", DRAFT_COLS, rows)
        print(f"marked {a.args[1]} for {a.args[0]}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
