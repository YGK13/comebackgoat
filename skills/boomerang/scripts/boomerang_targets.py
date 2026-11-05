#!/usr/bin/env python3
"""Boomerang roster: which former employers the user may approach now, and through whom.

Usage:
    python3 boomerang_targets.py <workspace> [--index private/network.json] [--date YYYY-MM-DD]
                                 [--top 3] [--min-warmth 25] [--json] [--write]

Reads the boomerang block of context/lanes.yaml and, when given, the warmth-scored network index
built by network-engine. For each former employer it reports:
  - status: eligible | blocked (a non-solicit or non-compete date has not passed) | ask (the user
    marked the exit as difficult) | stale (left more than 10 years ago)
  - the warmest current insiders (people whose current company matches the employer)
--write appends one found row per eligible employer's best insider to trackers/boomerang.csv
(B- ids, shared tracker columns), skipping employer and contact pairs already there.

Standard library only (PyYAML when present). Never contacts anyone.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

COLUMNS = ["id", "date_found", "engine", "title", "link", "value_usd", "status", "deadline", "score",
           "prepared", "next_action", "notes", "updated", "minutes", "stage"]
TERMS = {"good", "neutral", "difficult"}
STALE_YEARS = 10


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(inc|llc|ltd|corp|corporation|co|company|plc|gmbh|group|the)\b\.?", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def word_match(needle: str, hay: str) -> bool:
    n = norm(needle)
    return bool(n) and re.search(rf"(?:^| ){re.escape(n)}(?: |$)", norm(hay)) is not None


def parse_date(s) -> date | None:
    if isinstance(s, date):
        return s
    s = str(s or "").strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def load_block(ws: Path) -> dict:
    p = ws / "context" / "lanes.yaml"
    if not p.exists() or yaml is None:
        return {}
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data.get("boomerang") or {}


def insiders(index: dict, employer: str, top: int, min_warmth: int) -> list[dict]:
    hits = [p for p in index.get("people", []) if word_match(employer, p.get("company", ""))
            and int(p.get("warmth", 0)) >= min_warmth]
    hits.sort(key=lambda p: (-int(p.get("warmth", 0)), p.get("name", "")))
    return [{k: p.get(k, "") for k in ("name", "title", "warmth", "msg_last", "linkedin")} for p in hits[:top]]


def roster(ws: Path, today: date, index: dict | None, top: int, min_warmth: int) -> dict:
    block = load_block(ws)
    out = {"date": today.isoformat(), "enabled": bool(block.get("enabled", False)),
           "default_offer": block.get("default_offer", "consultant_first"), "employers": []}
    for e in block.get("employers") or []:
        if not isinstance(e, dict) or not str(e.get("name", "")).strip():
            continue
        name = str(e["name"]).strip()
        left = parse_date(e.get("left_on"))
        until = parse_date(e.get("restriction_until"))
        terms = str(e.get("terms", "neutral")).lower()
        status, reason = "eligible", ""
        if until and until > today:
            status, reason = "blocked", f"restriction until {until.isoformat()}"
        elif terms == "difficult":
            status, reason = "ask", "exit marked difficult: ask the user before any outreach"
        elif left and (today - left).days > STALE_YEARS * 365:
            status, reason = "stale", f"left more than {STALE_YEARS} years ago"
        row = {"name": name, "status": status, "reason": reason,
               "left_as": e.get("left_as", ""), "days_since_left": (today - left).days if left else None,
               "rehire_ok": bool(e.get("rehire_ok", False)),
               "offer": "consultant_first" if not e.get("rehire_ok") else out["default_offer"],
               "insiders": insiders(index, name, top, min_warmth) if index and status == "eligible" else []}
        out["employers"].append(row)
    order = {"eligible": 0, "ask": 1, "blocked": 2, "stale": 3}
    out["employers"].sort(key=lambda r: (order[r["status"]], -(r["insiders"][0]["warmth"] if r["insiders"] else 0)))
    return out


def write_rows(ws: Path, data: dict, today: date) -> int:
    path = ws / "trackers" / "boomerang.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing, max_n = set(), 0
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                existing.add((r.get("title") or "").lower())
                m = re.match(r"B-(\d+)$", r.get("id") or "")
                if m:
                    max_n = max(max_n, int(m.group(1)))
    new = []
    for e in data["employers"]:
        if e["status"] != "eligible" or not e["insiders"]:
            continue
        p = e["insiders"][0]
        title = f"{e['name']}: reconnect with {p['name']}"
        if title.lower() in existing:
            continue
        max_n += 1
        offer = "a scoped consulting engagement first" if e["offer"] == "consultant_first" else "consulting or a return role"
        new.append({"id": f"B-{max_n}", "date_found": today.isoformat(), "engine": "boomerang", "title": title,
                    "link": p.get("linkedin", ""), "value_usd": "", "status": "found", "deadline": "",
                    "score": str(p["warmth"]), "prepared": "",
                    "next_action": f"Check signals at {e['name']}, then draft a reconnect note offering {offer}",
                    "notes": f"warmth {p['warmth']}; {p.get('title', '')}", "updated": today.isoformat(),
                    "minutes": "", "stage": "warm"})
    if new:
        write_header = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            if write_header:
                w.writeheader()
            w.writerows(new)
    return len(new)


def render(data: dict) -> str:
    if not data["employers"]:
        return "No former employers listed. Add them to the boomerang block in context/lanes.yaml."
    lines = [f"Boomerang roster, {data['date']} (default offer: {data['default_offer'].replace('_', ' ')})"]
    for e in data["employers"]:
        head = f"- {e['name']}: {e['status']}"
        if e["reason"]:
            head += f" ({e['reason']})"
        lines.append(head)
        for p in e["insiders"]:
            lines.append(f"    {p['name']}, {p['title']} - warmth {p['warmth']}")
        if e["status"] == "eligible" and not e["insiders"]:
            lines.append("    no warm insider in the index: ask the user who they still talk to there")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__)
        return 2
    ws = Path(argv[1])
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
    today = datetime.strptime(opt("--date"), "%Y-%m-%d").date() if "--date" in argv else date.today()
    idx_path = opt("--index")
    index = json.loads(Path(idx_path).read_text(encoding="utf-8")) if idx_path else None
    data = roster(ws, today, index, int(opt("--top", 3)), int(opt("--min-warmth", 25)))
    if "--write" in argv:
        data["written"] = write_rows(ws, data, today)
    print(json.dumps(data, indent=2) if "--json" in argv else render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
