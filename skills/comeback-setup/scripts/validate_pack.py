#!/usr/bin/env python3
"""Validate a Comeback GOAT workspace and optionally export the portable Context Pack.

Usage:
    python3 validate_pack.py <workspace-dir>
    python3 validate_pack.py <workspace-dir> --export pack.json

Checks:
  - required context files exist and the YAML files parse
  - claims.yaml: every claim has id, claim, source, ok_for (public|applications|private); ids unique
  - constraints.yaml / lanes.yaml: known enum values; scoring weights in each lane sum to 100
  - autopilot.approval is draft_only (the engines never send or submit on their own)
  - no sensitive identifiers anywhere in context/ (SSN pattern, payment card numbers that pass Luhn,
    IBAN-like strings, "password:" lines)
  - never_say terms do not appear in profile.md, messaging-kit.md or claims
  - logistics.yaml (optional): links are https, systems use known values, no secret-bearing keys
  - lanes.yaml today block (optional): sane focus mode and daily limits

Exit code 0 when clean, 1 when any error is found. Warnings never fail the run.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML is required: pip install pyyaml\n")
    sys.exit(2)

PACK_VERSION = "1.0"
REQUIRED = ["profile.md", "claims.yaml", "voice.md", "messaging-kit.md", "constraints.yaml", "lanes.yaml"]
OK_FOR = {"public", "applications", "private"}
ENTITY_TYPES = {"", "sole_prop", "llc", "s_corp", "c_corp", "nonprofit", "none"}
APPETITE = {"client_work", "no_equity", "job", "equity", "loans"}
JOB_STANCE = {"no", "if_great_fit", "active"}
JOB_TYPES = {"full_time", "contract", "fractional", "part_time"}
CADENCE = {"daily", "weekly", "monthly", "quarterly"}
ENGAGEMENTS = {"advisory", "fractional", "project", "workshop", "speaking", "expert_calls", "subcontract", "rfp"}
LANES = ["money_sweep", "grant_hunter", "project_hunter", "job_insurance"]
SYSTEMS = {
    "email": {"gmail", "outlook", "other"},
    "calendar": {"google", "outlook", "apple", "other"},
    "scheduler": {"calendly", "cal_com", "savvycal", "google_appointments", "hubspot_meetings", "none", "other"},
    "invoicing": {"stripe", "quickbooks", "freshbooks", "wave", "xero", "honeybook", "dubsado", "paypal", "none", "other"},
    "esign": {"dropbox_sign", "docusign", "pandadoc", "adobe_sign", "none", "other"},
    "proposals": {"pandadoc", "proposify", "google_docs", "word", "notion", "none", "other"},
    "crm": {"hubspot", "pipedrive", "notion", "airtable", "sheet", "none", "other"},
    "files": {"google_drive", "onedrive", "dropbox", "local", "other"},
}
SECRET_KEY_RE = re.compile(r"(?i)(password|passcode|api[_-]?key|secret|token|ssn|passport|account[_-]?number|routing|iban|card[_-]?number)")

SSN_RE = re.compile(r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}\b")
PASSWORD_RE = re.compile(r"(?i)\b(password|passcode|one[- ]time code)\s*[:=]\s*\S+")


def luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def scan_sensitive(name: str, text: str) -> list[str]:
    errs = []
    for n, line in enumerate(text.splitlines(), 1):
        if SSN_RE.search(line):
            errs.append(f"{name}:{n}: looks like a Social Security number; remove it")
        for m in CARD_RE.finditer(line):
            digits = re.sub(r"\D", "", m.group())
            if 13 <= len(digits) <= 19 and luhn_ok(digits) and len(set(digits)) > 1:
                errs.append(f"{name}:{n}: looks like a payment card number; keep only the last 4 digits")
        if IBAN_RE.search(line):
            errs.append(f"{name}:{n}: looks like a bank account (IBAN); keep only institution and last 4")
        if PASSWORD_RE.search(line):
            errs.append(f"{name}:{n}: contains a password or code; remove it")
    return errs


def load_yaml(path: Path, errs: list[str]):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        errs.append(f"{path.name}: invalid YAML: {exc}")
        return {}
    if not isinstance(data, dict):
        errs.append(f"{path.name}: must be a mapping")
        return {}
    return data


def check_claims(c: dict, errs: list[str], warns: list[str]) -> None:
    claims = c.get("claims") or []
    if not isinstance(claims, list) or not claims:
        errs.append("claims.yaml: claims must be a non-empty list")
        return
    seen = set()
    for i, cl in enumerate(claims):
        where = f"claims.yaml: claims[{i}]"
        if not isinstance(cl, dict):
            errs.append(f"{where}: must be a mapping")
            continue
        cid = cl.get("id")
        if not cid:
            errs.append(f"{where}: missing id")
        elif cid in seen:
            errs.append(f"{where}: duplicate id {cid!r}")
        seen.add(cid)
        if cid == "example-claim":
            errs.append(f"{where}: template example still present; replace it")
        if not str(cl.get("claim", "")).strip():
            errs.append(f"{where}: missing claim text")
        if not str(cl.get("source", "")).strip():
            errs.append(f"{where} ({cid}): missing source; every claim needs one")
        ok = cl.get("ok_for") or []
        if not ok or not set(ok) <= OK_FOR:
            errs.append(f"{where} ({cid}): ok_for must be a list from {sorted(OK_FOR)}")
    person = c.get("person") or {}
    if not str(person.get("name", "")).strip():
        errs.append("claims.yaml: person.name is required")
    contact = c.get("contact") or {}
    if not str(contact.get("email", "")).strip():
        warns.append("claims.yaml: contact.email is empty; drafts cannot be signed")
    ent = c.get("entity") or {}
    if str(ent.get("type", "")) not in ENTITY_TYPES:
        errs.append(f"claims.yaml: entity.type must be one of {sorted(ENTITY_TYPES - {''})}")
    for k in ("ein", "ein_number", "ssn", "tax_id"):
        if k in ent:
            errs.append(f"claims.yaml: entity.{k} is not allowed; use ein_on_file: true/false")


def check_constraints(k: dict, errs: list[str]) -> None:
    money = k.get("money") or {}
    bad = set(money.get("appetite") or []) - APPETITE
    if bad:
        errs.append(f"constraints.yaml: money.appetite has unknown values {sorted(bad)}")
    job = k.get("job") or {}
    if str(job.get("stance", "no")) not in JOB_STANCE:
        errs.append(f"constraints.yaml: job.stance must be one of {sorted(JOB_STANCE)}")
    bad = set(job.get("types") or []) - JOB_TYPES
    if bad:
        errs.append(f"constraints.yaml: job.types has unknown values {sorted(bad)}")
    tz = (k.get("schedule") or {}).get("timezone", "")
    if tz and "/" not in str(tz):
        errs.append("constraints.yaml: schedule.timezone must be an IANA name like America/New_York")


def check_lanes(l: dict, errs: list[str], warns: list[str]) -> None:
    for lane in LANES:
        block = l.get(lane)
        if not isinstance(block, dict):
            errs.append(f"lanes.yaml: missing block {lane}")
            continue
        if block.get("cadence") and block["cadence"] not in CADENCE:
            errs.append(f"lanes.yaml: {lane}.cadence must be one of {sorted(CADENCE)}")
        w = block.get("weights")
        if w is not None:
            total = sum(v for v in w.values() if isinstance(v, (int, float)))
            if total != 100:
                errs.append(f"lanes.yaml: {lane}.weights sum to {total}, must be 100")
    eng = set((l.get("project_hunter") or {}).get("engagement_types") or []) - ENGAGEMENTS
    if eng:
        errs.append(f"lanes.yaml: project_hunter.engagement_types has unknown values {sorted(eng)}")
    cap = (l.get("job_insurance") or {}).get("daily_cap", 0)
    if isinstance(cap, int) and cap > 10:
        errs.append("lanes.yaml: job_insurance.daily_cap above 10 is not allowed (quality and platform rules)")
    net = l.get("network") or {}
    if isinstance(net.get("max_drafts_per_day", 0), int) and net.get("max_drafts_per_day", 0) > 5:
        errs.append("lanes.yaml: network.max_drafts_per_day above 5 is not allowed (no mass outreach)")
    ap = l.get("autopilot") or {}
    if ap.get("approval", "draft_only") != "draft_only":
        errs.append("lanes.yaml: autopilot.approval must be draft_only")
    if not any((l.get(x) or {}).get("enabled") for x in LANES):
        warns.append("lanes.yaml: no engine is enabled")


def walk_keys(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield f"{path}.{k}" if path else str(k), k
            yield from walk_keys(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_keys(v, f"{path}[{i}]")


def check_logistics(g: dict, claims: dict, errs: list[str], warns: list[str]) -> None:
    for where, key in walk_keys(g):
        if SECRET_KEY_RE.search(str(key)):
            errs.append(f"logistics.yaml: {where} is not allowed; never store secrets or ID numbers")
    for k, v in (g.get("links") or {}).items():
        if v and not str(v).startswith("https://"):
            errs.append(f"logistics.yaml: links.{k} must start with https://")
    for k, v in (g.get("systems") or {}).items():
        if v and k in SYSTEMS and v not in SYSTEMS[k]:
            errs.append(f"logistics.yaml: systems.{k} must be one of {sorted(SYSTEMS[k])}")
    ids = {c.get("id") for c in (claims.get("claims") or []) if isinstance(c, dict)}
    for i, cr in enumerate(g.get("credentials") or []):
        if isinstance(cr, dict) and cr.get("claim_id") and cr["claim_id"] not in ids:
            warns.append(f"logistics.yaml: credentials[{i}].claim_id {cr['claim_id']!r} has no matching claim; add a sourced claim")
    eeo = (g.get("application_answers") or {}).get("eeo_self_id", "decline")
    if eeo not in {"decline", "ask_me"}:
        errs.append("logistics.yaml: application_answers.eeo_self_id must be decline or ask_me (answers are never stored)")
    if not (g.get("links") or {}).get("booking"):
        warns.append("logistics.yaml: links.booking is empty; replies cannot offer a time")


def check_boomerang(l: dict, errs: list[str], warns: list[str]) -> None:
    b = l.get("boomerang")
    if not isinstance(b, dict):
        return
    if b.get("default_offer", "consultant_first") not in {"consultant_first", "either"}:
        errs.append("lanes.yaml: boomerang.default_offer must be consultant_first or either")
    for i, e in enumerate(b.get("employers") or []):
        where = f"lanes.yaml: boomerang.employers[{i}]"
        if not isinstance(e, dict) or not str(e.get("name", "")).strip():
            errs.append(f"{where}: name is required")
            continue
        for k in ("left_on", "restriction_until"):
            v = str(e.get(k, "") or "")
            if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                errs.append(f"{where}.{k} must be YYYY-MM-DD")
        if str(e.get("terms", "neutral")) not in {"good", "neutral", "difficult"}:
            errs.append(f"{where}.terms must be good, neutral or difficult")
        until = str(e.get("restriction_until", "") or "")
        if until and until > date.today().isoformat():
            warns.append(f"{where}: {e['name']} is blocked for outreach until {until}")


def check_today(l: dict, errs: list[str]) -> None:
    t = l.get("today")
    if not isinstance(t, dict):
        return
    if "focus_mode" in t and not isinstance(t["focus_mode"], bool):
        errs.append("lanes.yaml: today.focus_mode must be true or false")
    mi = t.get("max_items", 7)
    if not isinstance(mi, int) or not 1 <= mi <= 10:
        errs.append("lanes.yaml: today.max_items must be 1 to 10")
    hm = t.get("human_minutes_per_day", 45)
    if not isinstance(hm, int) or not 5 <= hm <= 480:
        errs.append("lanes.yaml: today.human_minutes_per_day must be 5 to 480")


def check_never_say(ctx: Path, claims: dict, errs: list[str]) -> None:
    terms = [t for t in (claims.get("never_say") or []) if str(t).strip()]
    if not terms:
        return
    haystacks = {
        "profile.md": (ctx / "profile.md").read_text(encoding="utf-8") if (ctx / "profile.md").exists() else "",
        "messaging-kit.md": (ctx / "messaging-kit.md").read_text(encoding="utf-8") if (ctx / "messaging-kit.md").exists() else "",
        "claims": " ".join(str(c.get("claim", "")) for c in (claims.get("claims") or []) if isinstance(c, dict)),
    }
    for term in terms:
        for name, text in haystacks.items():
            if str(term).lower() in text.lower():
                errs.append(f"{name}: contains never_say term {term!r}")


def export_pack(ctx: Path, claims: dict, constraints: dict, lanes: dict, logistics: dict | None = None) -> dict:
    read = lambda n: (ctx / n).read_text(encoding="utf-8") if (ctx / n).exists() else ""
    public = [c for c in claims.get("claims", []) if "private" not in (c.get("ok_for") or [])]
    return {
        "pack_version": PACK_VERSION,
        "exported_on": date.today().isoformat(),
        "person": claims.get("person", {}),
        "contact": claims.get("contact", {}),
        "entity": claims.get("entity", {}),
        "claims": public,
        "never_say": claims.get("never_say", []),
        "constraints": constraints,
        "lanes": lanes,
        "logistics": logistics or {},
        "voice_md": read("voice.md"),
        "messaging_kit_md": read("messaging-kit.md"),
        "profile_md": read("profile.md"),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    ws = Path(argv[1])
    ctx = ws / "context"
    errs: list[str] = []
    warns: list[str] = []
    if not ctx.is_dir():
        print(f"ERROR: {ctx} not found")
        return 1
    for f in REQUIRED:
        if not (ctx / f).is_file():
            errs.append(f"missing context/{f}")
    claims = load_yaml(ctx / "claims.yaml", errs) if (ctx / "claims.yaml").exists() else {}
    constraints = load_yaml(ctx / "constraints.yaml", errs) if (ctx / "constraints.yaml").exists() else {}
    lanes = load_yaml(ctx / "lanes.yaml", errs) if (ctx / "lanes.yaml").exists() else {}
    if claims:
        check_claims(claims, errs, warns)
        check_never_say(ctx, claims, errs)
    if constraints:
        check_constraints(constraints, errs)
    if lanes:
        check_lanes(lanes, errs, warns)
        check_today(lanes, errs)
        check_boomerang(lanes, errs, warns)
    logistics = load_yaml(ctx / "logistics.yaml", errs) if (ctx / "logistics.yaml").exists() else {}
    if logistics:
        check_logistics(logistics, claims, errs, warns)
    for p in sorted(ctx.glob("*")):
        if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".csv", ".txt"}:
            errs.extend(scan_sensitive(f"context/{p.name}", p.read_text(encoding="utf-8", errors="ignore")))
    for w in warns:
        print(f"WARN  {w}")
    for e in errs:
        print(f"ERROR {e}")
    if errs:
        print(f"{len(errs)} error(s). Fix them and run again.")
        return 1
    print(f"OK: context pack in {ws} is valid ({len(claims.get('claims', []))} claims).")
    if "--export" in argv:
        out = Path(argv[argv.index("--export") + 1])
        out.write_text(json.dumps(export_pack(ctx, claims, constraints, lanes, logistics), indent=2, default=str), encoding="utf-8")
        print(f"Exported portable pack to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
