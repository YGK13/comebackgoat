#!/usr/bin/env python3
"""Build and query a warmth-scored network index from the user's own exports.

Generalized from Yuri Kruman's private job-engine index (Portfolio Leverage Co.).
Standard library only. Never sends anything anywhere; reads files, writes one JSON file.

Build:
    python3 network_index.py build --owner "Full Name" --out RevenueEngine/private/network.json \
        [--connections Connections.csv] [--contacts google-contacts.csv] \
        [--messages messages.csv] [--invitations Invitations.csv]

Query:
    python3 network_index.py lookup --index RevenueEngine/private/network.json --company "Acme" [--top 15]
    python3 network_index.py lookup --index ... --title "head of people" [--top 15]
    python3 network_index.py stats  --index ...

Warmth (0-100): 10 base for any connection or contact; up to 40 for message volume
(log scale, 100+ messages caps it); up to 25 for recency of the last message (full within
6 months, linear to 0 at 5 years); +10 if an email is known; +10 if the person is in both
LinkedIn and saved contacts; +5 if connected on LinkedIn in the last 2 years.

Only aggregates are kept from messages (counts and last date), never message text.
The index holds personal data about other people: keep it in a private folder the user
owns, never commit it to a repository and never copy it into drafts or public files.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

CONNECTIONS_HEADER_START = "First Name,Last Name"
_NON_ALNUM = re.compile(r"[^a-z0-9 ]+")
_WS = re.compile(r"\s+")


def norm(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii").lower()
    return _WS.sub(" ", _NON_ALNUM.sub(" ", folded)).strip()


def parse_date(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%d %b %Y", "%Y-%m-%d %H:%M:%S %Z", "%Y-%m-%d %H:%M:%S", "%m/%d/%y, %I:%M %p", "%m/%d/%Y, %I:%M %p", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.strptime(raw.rsplit(" ", 1)[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def new_person(name: str) -> dict:
    return {"name": name, "company": "", "title": "", "email": "", "linkedin": "", "connected_on": "",
            "sources": [], "msg_total": 0, "msg_sent": 0, "msg_received": 0, "msg_last": "", "warmth": 0}


def read_connections(path: Path):
    """LinkedIn Connections.csv starts with a free-text notes preamble; skip to the real header."""
    with path.open(encoding="utf-8-sig", newline="") as fh:
        lines = fh.read().splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(CONNECTIONS_HEADER_START)), None)
    if start is None:
        raise ValueError(f"{path}: header starting with '{CONNECTIONS_HEADER_START}' not found")
    yield from csv.DictReader(lines[start:])


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        yield from csv.DictReader(fh)


def build(args) -> dict:
    owner_keys = {norm(n) for n in args.owner.split("|") if n.strip()}
    people: dict[str, dict] = {}
    now = datetime.now(timezone.utc)
    stats = {"linkedin": 0, "contacts": 0, "contacts_merged": 0, "message_rows": 0, "invitations": 0}

    if args.connections:
        for row in read_connections(Path(args.connections)):
            name = f"{row.get('First Name', '').strip()} {row.get('Last Name', '').strip()}".strip()
            key = norm(name)
            if not key or key in owner_keys:
                continue
            p = people.setdefault(key, new_person(name))
            p["company"] = p["company"] or (row.get("Company") or "").strip()
            p["title"] = p["title"] or (row.get("Position") or "").strip()
            p["email"] = p["email"] or (row.get("Email Address") or "").strip()
            p["linkedin"] = p["linkedin"] or (row.get("URL") or "").strip()
            p["connected_on"] = p["connected_on"] or (row.get("Connected On") or "").strip()
            if "linkedin" not in p["sources"]:
                p["sources"].append("linkedin")
            stats["linkedin"] += 1

    if args.contacts:
        for row in read_csv(Path(args.contacts)):
            name = (row.get("Name") or " ".join(x for x in (row.get("First Name", ""), row.get("Last Name", "")) if x)).strip()
            key = norm(name)
            if not key or key in owner_keys:
                continue
            merged = key in people
            p = people.setdefault(key, new_person(name))
            email = (row.get("E-mail 1 - Value") or row.get("Email") or "").strip()
            p["email"] = p["email"] or email.split(" ::: ")[0]
            p["company"] = p["company"] or (row.get("Organization 1 - Name") or row.get("Organization Name") or "").strip()
            p["title"] = p["title"] or (row.get("Organization 1 - Title") or row.get("Organization Title") or "").strip()
            if "contacts" not in p["sources"]:
                p["sources"].append("contacts")
            stats["contacts"] += 1
            stats["contacts_merged"] += int(merged)

    if args.messages:
        for row in read_csv(Path(args.messages)):
            if (row.get("FOLDER") or "").upper() == "DRAFT":
                continue
            stats["message_rows"] += 1
            sender = (row.get("FROM") or "").strip()
            recipients = [r.strip() for r in (row.get("TO") or "").split(",") if r.strip()]
            when = parse_date(row.get("DATE", ""))
            sent_by_owner = norm(sender) in owner_keys
            counterparts = recipients if sent_by_owner else [sender]
            for c in counterparts:
                p = people.get(norm(c))
                if not p:
                    continue
                p["msg_total"] += 1
                p["msg_sent" if sent_by_owner else "msg_received"] += 1
                if when and (not p["msg_last"] or when.isoformat() > p["msg_last"]):
                    p["msg_last"] = when.isoformat()

    if args.invitations:
        for _ in read_csv(Path(args.invitations)):
            stats["invitations"] += 1  # counted only; direction and dates can be added later

    for p in people.values():
        p["warmth"] = warmth(p, now)
    ranked = sorted(people.values(), key=lambda x: (-x["warmth"], x["name"]))
    return {"meta": {"owner": args.owner, "built": now.isoformat(timespec="seconds"), "people": len(ranked), **stats},
            "people": ranked}


def warmth(p: dict, now: datetime) -> int:
    score = 10.0
    if p["msg_total"]:
        score += 40 * min(1.0, math.log1p(p["msg_total"]) / math.log1p(100))
    last = parse_date(p["msg_last"].replace("T", " ").split("+")[0]) if p["msg_last"] else None
    if last:
        days = (now - last).days
        if days <= 182:
            score += 25
        elif days < 5 * 365:
            score += 25 * (1 - (days - 182) / (5 * 365 - 182))
    if p["email"]:
        score += 10
    if "linkedin" in p["sources"] and "contacts" in p["sources"]:
        score += 10
    connected = parse_date(p["connected_on"])
    if connected and (now - connected).days <= 730:
        score += 5
    return int(round(min(100.0, score)))


def word_match(needle: str, hay: str) -> bool:
    n = norm(needle)
    return bool(n) and re.search(rf"(?:^| ){re.escape(n)}(?: |$)", norm(hay)) is not None


def lookup(args) -> list[dict]:
    data = json.loads(Path(args.index).read_text(encoding="utf-8"))
    hits = data["people"]
    if args.company:
        hits = [p for p in hits if word_match(args.company, p["company"])]
    if args.title:
        hits = [p for p in hits if word_match(args.title, p["title"])]
    return [{k: p[k] for k in ("name", "company", "title", "warmth", "msg_total", "msg_last", "linkedin")} for p in hits[: args.top]]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--owner", required=True, help="the user's name as LinkedIn shows it; several with |")
    b.add_argument("--out", required=True)
    for f in ("connections", "contacts", "messages", "invitations"):
        b.add_argument(f"--{f}")
    q = sub.add_parser("lookup")
    q.add_argument("--index", required=True)
    q.add_argument("--company")
    q.add_argument("--title")
    q.add_argument("--top", type=int, default=15)
    s = sub.add_parser("stats")
    s.add_argument("--index", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "build":
        if not any((args.connections, args.contacts)):
            ap.error("give at least --connections or --contacts")
        index = build(args)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(index, indent=1), encoding="utf-8")
        m = index["meta"]
        print(f"Indexed {m['people']} people (LinkedIn rows {m['linkedin']}, contacts {m['contacts']}, "
              f"merged {m['contacts_merged']}, message rows {m['message_rows']}). Wrote {out}")
    elif args.cmd == "lookup":
        if not (args.company or args.title):
            ap.error("give --company or --title")
        print(json.dumps(lookup(args), indent=1))
    else:
        data = json.loads(Path(args.index).read_text(encoding="utf-8"))
        bands = {"80+": 0, "60-79": 0, "40-59": 0, "under 40": 0}
        for p in data["people"]:
            w = p["warmth"]
            bands["80+" if w >= 80 else "60-79" if w >= 60 else "40-59" if w >= 40 else "under 40"] += 1
        companies: dict[str, int] = {}
        for p in data["people"]:
            if p["company"]:
                companies[p["company"]] = companies.get(p["company"], 0) + 1
        top = sorted(companies.items(), key=lambda kv: -kv[1])[:15]
        print(json.dumps({"meta": data["meta"], "warmth_bands": bands, "top_companies": top}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
