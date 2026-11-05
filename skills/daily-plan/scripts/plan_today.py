#!/usr/bin/env python3
"""Today planner: rank every open item by distance to revenue and split it into
what Claude does now and what only the user can do.

Usage:
    python3 plan_today.py plan  <workspace> [--date YYYY-MM-DD] [--focus|--no-focus] [--json] [--save]
    python3 plan_today.py learn <workspace> [--date YYYY-MM-DD]

plan   reads trackers/*.csv, context/lanes.yaml (today block), context/constraints.yaml (days off)
       and trackers/calibration.json, then prints the plan. --save writes runs/<date>-today.json,
       which the next run uses to spot carried-over items.
learn  recomputes per-stage and per-engine win rates from tracker history (Bayesian blend with the
       default priors) and writes trackers/calibration.json. The planner uses those rates next time.

Standard library only (PyYAML used when present). Never sends, submits or edits trackers.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

# The revenue ladder: R1 is money already earned, R8 is work that only pays indirectly.
# prior = default chance the item turns into cash; days = typical days until cash arrives.
LADDER = {
    "cash":         {"r": 1, "label": "cash",         "prior": 0.80,  "days": 14},
    "close":        {"r": 2, "label": "close",        "prior": 0.35,  "days": 21},
    "conversation": {"r": 3, "label": "conversation", "prior": 0.15,  "days": 45},
    "warm":         {"r": 4, "label": "warm path",    "prior": 0.05,  "days": 60},
    "apply":        {"r": 5, "label": "application",  "prior": 0.04,  "days": 75},
    "cold":         {"r": 6, "label": "cold",         "prior": 0.01,  "days": 75},
    "asset":        {"r": 7, "label": "asset",        "prior": 0.005, "days": 120},
    "admin":        {"r": 8, "label": "admin",        "prior": 0.001, "days": 180},
}
# Engine-specific priors for applications (grants and jobs convert very differently).
ENGINE_PRIOR = {("apply", "G"): 0.08, ("apply", "J"): 0.03}

ENGINES = {"M": "money-sweep", "G": "grant-hunter", "P": "project-hunter", "J": "job-insurance",
           "N": "network-engine", "T": "task"}
OPEN = {"found", "prepared", "needs_you", "sent", "submitted"}
CLOSED_WIN = {"won"}
CLOSED_LOSS = {"lost", "expired", "skipped"}

# Order matters: the first matching rule wins.
KEYWORDS = [
    ("cash", r"\b(invoice|payout|refund|reimburs|unpaid|owed|receivable|unclaimed|claim (form|link)|deposit|chargeback|collect)\w*"),
    ("close", r"\b(proposal|sow|statement of work|contract|msa|sign|offer letter|offer stage|pricing|quote|retainer|renewal)\w*"),
    ("conversation", r"\b(reply|replied|call(?! for)|meeting|interview|intro call|discovery|follow[- ]?up after|booked|calendly)\w*"),
    ("warm", r"\b(warm|reconnect|reactivat|intro(duction)? request|referral|former (client|boss|colleague))\w*"),
    ("asset", r"\b(website|landing page|linkedin (headline|about|rewrite)|bio|case study|content|post draft|newsletter|deck)\b"),
    ("admin", r"\b(setup|set up|install|export|organi[sz]e|learn|course|read)\b"),
]
DECIDE_RE = re.compile(r"^\s*(decide|choose|pick|approve|confirm price|set price)\b", re.I)
LIVE_RE = re.compile(r"\b(call|meeting|interview|session)\b", re.I)

DEFAULTS = {
    "enabled": True,
    "focus_mode": False,
    "human_minutes_per_day": 45,
    "max_items": 7,
    "default_deal_usd": 0,
    "follow_up_days": 5,
}
FOCUS_MAX = 3
STARTER_MAX_MIN = 10


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        try:
            data = yaml.safe_load(text) or {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def parse_date(s: str):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %b %Y", "%b %d %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def money(s: str) -> float:
    s = re.sub(r"[^\d.]", "", s or "")
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def engine_of(row: dict) -> str:
    pid = (row.get("id") or "").strip()
    if "-" in pid and pid.split("-")[0].upper() in ENGINES:
        return pid.split("-")[0].upper()
    eng = (row.get("engine") or "").lower()
    for k, v in ENGINES.items():
        if eng.startswith(v.split("-")[0]):
            return k
    return "T"


def infer_stage(row: dict, eng: str) -> str:
    explicit = (row.get("stage") or "").strip().lower()
    if explicit in LADDER:
        return explicit
    text = " ".join(row.get(k, "") or "" for k in ("title", "next_action", "notes", "prepared")).lower()
    for stage, rx in KEYWORDS:
        if re.search(rx, text):
            # A job or grant mentioning "call" is still an application unless it is an interview.
            if stage == "conversation" and eng in {"G", "J"} and "interview" not in text:
                continue
            return stage
    return {"M": "cash", "G": "apply", "J": "apply", "N": "warm", "P": "cold"}.get(eng, "admin")


def load_rows(ws: Path) -> list[dict]:
    rows = []
    tdir = ws / "trackers"
    for p in sorted(tdir.glob("*.csv")):
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if not (r.get("id") or "").strip():
                    continue
                r["_file"] = p.name
                rows.append(r)
    return rows


def calibration(ws: Path) -> dict:
    p = ws / "trackers" / "calibration.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def win_rate(stage: str, eng: str, cal: dict) -> float:
    key = f"{stage}|{eng}"
    if key in cal.get("stage_engine", {}):
        return cal["stage_engine"][key]["rate"]
    if stage in cal.get("stage", {}):
        return cal["stage"][stage]["rate"]
    return ENGINE_PRIOR.get((stage, eng), LADDER[stage]["prior"])


def deal_value(row: dict, cfg: dict, lanes: dict) -> tuple[float, bool]:
    v = money(row.get("value_usd", ""))
    if v > 0:
        return v, True
    if cfg.get("default_deal_usd"):
        return float(cfg["default_deal_usd"]), False
    ph = lanes.get("project_hunter") or {}
    if ph.get("project_minimum_usd"):
        return float(ph["project_minimum_usd"]), False
    if ph.get("day_rate_usd"):
        return float(ph["day_rate_usd"]) * 3, False
    return 1000.0, False


def classify(row: dict, today: date, cfg: dict) -> tuple[str, str, int]:
    """Return (executor, action, human_minutes). executor: claude | you_press | you_decide | you_live | wait."""
    status = (row.get("status") or "").strip().lower()
    nxt = (row.get("next_action") or "").strip()
    minutes = row.get("minutes", "")
    m = int(minutes) if str(minutes).strip().isdigit() else None
    if status == "found":
        return "claude", f"Prepare: {nxt or row.get('title', '')}", 0
    if status in {"prepared", "needs_you"}:
        if DECIDE_RE.search(nxt):
            return "you_decide", nxt, m or 5
        if LIVE_RE.search(nxt) and not re.search(r"\b(send|submit|press)\b", nxt, re.I):
            return "you_live", nxt, m or 30
        return "you_press", nxt or "Press Send or Submit", m or 3
    if status in {"sent", "submitted"}:
        last = parse_date(row.get("updated", "")) or parse_date(row.get("date_found", ""))
        age = (today - last).days if last else 0
        if age >= int(cfg.get("follow_up_days", 5)):
            return "claude", f"Draft a follow-up ({age} days since sent)", 0
        return "wait", "", 0
    return "wait", "", 0


def score(row: dict, stage: str, eng: str, cfg: dict, lanes: dict, cal: dict, today: date) -> dict:
    value, sourced = deal_value(row, cfg, lanes)
    p = win_rate(stage, eng, cal)
    days = LADDER[stage]["days"]
    ev = value * p
    speed = 30 / (30 + days)                    # money sooner is worth more to a new solo business
    due = parse_date(row.get("deadline", ""))
    urgency, due_in = 1.0, None
    if due:
        due_in = (due - today).days
        if due_in < 0:
            urgency = 0.0                       # past deadline: shown as expired, never ranked
        elif due_in <= 2:
            urgency = 2.0
        elif due_in <= 7:
            urgency = 1.4
    return {"ev_usd": round(ev, 2), "value_usd": value, "value_sourced": sourced, "p": p,
            "priority": round(ev * speed * urgency, 2), "due_in": due_in}


def previous_plan(ws: Path, today: date) -> dict:
    runs = ws / "runs"
    if not runs.is_dir():
        return {}
    files = sorted(p for p in runs.glob("*-today.json") if p.name[:10] < today.isoformat())
    if not files:
        return {}
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_plan(ws: Path, today: date, focus: bool | None = None) -> dict:
    lanes = load_yaml(ws / "context" / "lanes.yaml")
    constraints = load_yaml(ws / "context" / "constraints.yaml")
    cfg = {**DEFAULTS, **(lanes.get("today") or {})}
    if focus is not None:
        cfg["focus_mode"] = focus
    days_off = [str(d).lower()[:3] for d in ((constraints.get("schedule") or {}).get("days_off") or [])]
    plan = {"date": today.isoformat(), "focus_mode": bool(cfg["focus_mode"]), "day_off": False,
            "claude": [], "you": [], "parked": [], "expired": [], "waiting": 0, "suggestions": []}
    if today.strftime("%a").lower()[:3] in days_off:
        plan["day_off"] = True
        return plan

    cal = calibration(ws)
    prev = previous_plan(ws, today)
    prev_you = {i["id"]: i for i in prev.get("you", [])}
    items = []
    for row in load_rows(ws):
        status = (row.get("status") or "").strip().lower()
        if status not in OPEN:
            continue
        eng = engine_of(row)
        stage = infer_stage(row, eng)
        executor, action, minutes = classify(row, today, cfg)
        s = score(row, stage, eng, cfg, lanes, cal, today)
        item = {"id": row["id"].strip(), "title": (row.get("title") or "").strip(), "engine": ENGINES.get(eng, "task"),
                "stage": stage, "r": LADDER[stage]["r"], "executor": executor, "action": action,
                "minutes": minutes, "deadline": row.get("deadline", ""), "link": row.get("link", ""), **s}
        if s["due_in"] is not None and s["due_in"] < 0:
            plan["expired"].append(item)
            continue
        if executor == "wait":
            plan["waiting"] += 1
            continue
        if item["id"] in prev_you and executor != "claude":
            item["carried_days"] = int(prev_you[item["id"]].get("carried_days", 0)) + 1
        items.append(item)

    # Ordering: anything due within 48 hours first, then R1 to R3 (closest to cash), then the rest;
    # inside each bucket by priority (expected dollars, discounted for time to cash, boosted by deadline).
    def bucket(i):
        if i["due_in"] is not None and i["due_in"] <= 2 and i["r"] <= 5:
            return 0
        return 1 if i["r"] <= 3 else 2

    items.sort(key=lambda i: (bucket(i), -i["priority"], i["r"]))
    plan["claude"] = [i for i in items if i["executor"] == "claude"]
    human = [i for i in items if i["executor"] != "claude"]

    cap = FOCUS_MAX if cfg["focus_mode"] else int(cfg.get("max_items", 7))
    budget = int(cfg.get("human_minutes_per_day", 45))
    if cfg["focus_mode"] and human:
        # Lead with a starter: the best item that takes 10 minutes or less, so the day starts with a win.
        starters = [i for i in human if i["minutes"] <= STARTER_MAX_MIN]
        if starters and starters[0] is not human[0]:
            human.remove(starters[0])
            human.insert(0, starters[0])
        if human:
            human[0]["starter"] = True
    chosen, used = [], 0
    for i in human:
        fits = used + i["minutes"] <= budget or not chosen
        if len(chosen) < cap and fits:
            chosen.append(i)
            used += i["minutes"]
        else:
            plan["parked"].append(i)
    for i in chosen:
        if cfg["focus_mode"] and i.get("carried_days", 0) >= 2:
            i["decide"] = "Carried over twice: do it today, defer to a date, or drop it."
    plan["you"] = chosen
    plan["you_minutes"] = used
    plan["suggestions"] = suggest(items, plan, lanes)
    return plan


def suggest(items: list[dict], plan: dict, lanes: dict) -> list[str]:
    """Rule-based gaps in the pipeline, closest to cash first. At most 3."""
    out = []
    rs = [i["r"] for i in items]
    if not any(r == 1 for r in rs) and (lanes.get("money_sweep") or {}).get("enabled", True):
        out.append("No cash items open: Claude runs a receivables and payouts check (money-sweep, receivables only).")
    if sum(1 for r in rs if r in (2, 3)) < 3:
        out.append("Fewer than 3 live conversations or proposals: Claude drafts 5 warm reactivations to past clients and bosses (network-engine).")
    if plan["expired"]:
        out.append(f"{len(plan['expired'])} item(s) passed their deadline: Claude marks them expired so they stop counting.")
    return out[:3]


def learn(ws: Path, today: date) -> dict:
    """Bayesian blend of observed outcomes with the ladder priors (prior weight = 10 observations)."""
    k = 10
    counts: dict[str, list[int]] = {}
    counts_se: dict[str, list[int]] = {}
    for row in load_rows(ws):
        status = (row.get("status") or "").strip().lower()
        eng = engine_of(row)
        stage = infer_stage(row, eng)
        last = parse_date(row.get("updated", "")) or parse_date(row.get("date_found", ""))
        stale = status in {"sent", "submitted"} and last is not None and (today - last).days > 45
        if status in CLOSED_WIN:
            win = 1
        elif status in CLOSED_LOSS - {"skipped"} or stale:
            win = 0
        else:
            continue                              # still open, or skipped by the user (not an outcome)
        for d, key in ((counts, stage), (counts_se, f"{stage}|{eng}")):
            n_w = d.setdefault(key, [0, 0])
            n_w[0] += 1
            n_w[1] += win

    def blend(key: str, n: int, w: int, prior: float) -> dict:
        rate = (w + prior * k) / (n + k)
        return {"n": n, "wins": w, "rate": round(min(max(rate, 0.001), 0.95), 4)}

    cal = {"updated": today.isoformat(), "prior_weight": k, "stage": {}, "stage_engine": {}}
    for st, (n, w) in counts.items():
        cal["stage"][st] = blend(st, n, w, LADDER[st]["prior"])
    for key, (n, w) in counts_se.items():
        st, eng = key.split("|")
        cal["stage_engine"][key] = blend(key, n, w, ENGINE_PRIOR.get((st, eng), LADDER[st]["prior"]))
    out = ws / "trackers" / "calibration.json"
    out.write_text(json.dumps(cal, indent=2), encoding="utf-8")
    return cal


def fmt_item(n: int, i: dict) -> str:
    val = f"${i['value_usd']:,.0f}" if i["value_sourced"] else "no amount stated"
    due = f", due in {i['due_in']}d" if i["due_in"] is not None else ""
    tag = " STARTER" if i.get("starter") else ""
    carried = f" (carried {i['carried_days']}d)" if i.get("carried_days") else ""
    line = f"{n}. [R{i['r']} {LADDER[i['stage']]['label']}]{tag} {i['id']} {i['title']} - {i['action']} ({i['minutes']} min; {val}{due}){carried}"
    if i.get("decide"):
        line += f"\n   {i['decide']}"
    return line


def render(plan: dict) -> str:
    d = datetime.strptime(plan["date"], "%Y-%m-%d").strftime("%a %b %d")
    if plan["day_off"]:
        return f"Today, {d}: day off. Nothing scheduled, nothing nagging."
    mode = " | focus mode" if plan["focus_mode"] else ""
    out = [f"Today, {d}{mode}: {len(plan['you'])} for you (about {plan.get('you_minutes', 0)} min), {len(plan['claude'])} for Claude"]
    out.append("")
    out.append("CLAUDE DOES NOW (no input needed)")
    out += [f"- [R{i['r']}] {i['id']} {i['title']}: {i['action']}" for i in plan["claude"][:12]] or ["- nothing"]
    if len(plan["claude"]) > 12:
        out.append(f"- + {len(plan['claude']) - 12} more")
    out.append("")
    out.append("YOU, IN THIS ORDER")
    out += [fmt_item(n, i) for n, i in enumerate(plan["you"], 1)] or ["- nothing needs you today"]
    if plan["parked"]:
        out.append("")
        word = "held until the list above is done" if plan["focus_mode"] else "over today's time budget"
        out.append(f"PARKED: {len(plan['parked'])} item(s) {word}.")
    if plan["suggestions"]:
        out.append("")
        out.append("SUGGESTED")
        out += [f"- {s}" for s in plan["suggestions"]]
    out.append("")
    out.append(f"Waiting on others: {plan['waiting']}. Reply 'go' and Claude does its list; then work yours top to bottom.")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in {"plan", "learn"}:
        print(__doc__)
        return 2
    ws = Path(argv[2])
    today = date.today()
    if "--date" in argv:
        today = datetime.strptime(argv[argv.index("--date") + 1], "%Y-%m-%d").date()
    if not (ws / "trackers").is_dir():
        print(f"ERROR: {ws}/trackers not found")
        return 1
    if argv[1] == "learn":
        cal = learn(ws, today)
        print(json.dumps(cal, indent=2))
        return 0
    focus = True if "--focus" in argv else False if "--no-focus" in argv else None
    plan = build_plan(ws, today, focus)
    if "--save" in argv:
        (ws / "runs").mkdir(exist_ok=True)
        (ws / "runs" / f"{today.isoformat()}-today.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(json.dumps(plan, indent=2) if "--json" in argv else render(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
