#!/usr/bin/env python3
"""Validate every skills/<name>/SKILL.md.

Checks: YAML frontmatter opens on line 1 and parses to a mapping; `name`
equals the folder name (lowercase letters, digits, hyphens, <= 64 chars);
`description` is present and <= 1024 characters; `description` +
`when_to_use` fit the 1,536-char skill-listing cap; every
`references/<file>` the skill mentions exists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(r"(?:references|scripts)/[A-Za-z0-9_.\-/]+\.(?:md|py|yaml)")


def check(skill_dir: Path) -> list[str]:
    errs: list[str] = []
    rel = skill_dir.relative_to(ROOT)
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return [f"{rel}: missing SKILL.md"]
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return [f"{rel}/SKILL.md: frontmatter must start on line 1 between --- markers"]
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        return [f"{rel}/SKILL.md: frontmatter is not valid YAML: {exc}"]
    if not isinstance(fm, dict):
        return [f"{rel}/SKILL.md: frontmatter must be a YAML mapping"]

    name = fm.get("name")
    if name != skill_dir.name:
        errs.append(f"{rel}/SKILL.md: name {name!r} must equal folder name {skill_dir.name!r}")
    if not isinstance(name, str) or not NAME_RE.match(name or "") or len(name) > 64:
        errs.append(f"{rel}/SKILL.md: name must be lowercase letters/digits/hyphens, <= 64 chars")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errs.append(f"{rel}/SKILL.md: description is required")
        desc = ""
    elif len(desc) > 1024:
        errs.append(f"{rel}/SKILL.md: description is {len(desc)} chars (max 1024)")
    when = fm.get("when_to_use") or ""
    if len(desc) + len(str(when)) > 1536:
        errs.append(f"{rel}/SKILL.md: description + when_to_use is {len(desc) + len(str(when))} chars (listing cap 1536)")

    for ref in sorted(set(REF_RE.findall(text))):
        if not (skill_dir / ref).is_file():
            errs.append(f"{rel}/SKILL.md: mentions {ref}, which does not exist")
    return errs


def main() -> int:
    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if not dirs:
        print("no skills found", file=sys.stderr)
        return 1
    errors = [e for d in dirs for e in check(d)]
    for d in dirs:
        print(f"checked {d.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(dirs)} skill(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
