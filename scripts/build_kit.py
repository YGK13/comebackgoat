#!/usr/bin/env python3
"""Build the Comeback GOAT participant kit and the coach's operator skill.

    python3 scripts/build_kit.py            # refuses while cohort.yaml has SET_ME links
    python3 scripts/build_kit.py --draft    # builds anyway, leaving blanks visible (for testing)

Output (dist/ is gitignored):
  dist/comeback-goat-kit.zip       what each paid participant downloads
    README-FIRST.txt               three steps, nothing else
    CLAUDE-SETUP.md                upload to Claude: it sets everything up
    PARTICIPANT-PROTOCOL.md        goes into the Comeback GOAT Project
    skills/<name>.zip              one ZIP per skill, for Settings > Capabilities > Skills
    install.sh / install.ps1       Claude Code users only
  dist/coach/cohort-operator.zip   the coach's own skill, with cohort.yaml filled in

Coach links ({{BOOKING_URL}}, {{WHATSAPP_GROUP_LINK}}, {{WHATSAPP_DM_LINK}}) are
written into every Markdown file in the kit, so Claude can hand them out.
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "program"
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"

REQUIRED_SKILLS = ["comeback-sprint", "comeback-setup", "daily-plan", "network-engine",
                   "boomerang", "money-sweep", "comeback-doctor"]
OPTIONAL_SKILLS = ["project-hunter", "job-insurance", "grant-hunter", "comeback-autopilot"]
COACH_ONLY = {"cohort-operator"}
SKIP = {"__pycache__", ".DS_Store"}

README = """COMEBACK GOAT: START HERE

1. Open the Claude desktop app (Pro or Max plan).
2. Start a new chat, attach CLAUDE-SETUP.md from this folder and type:
       Set me up for Comeback GOAT.
3. Follow Claude's steps (about 30 minutes). It will ask you to upload the
   ZIP files in the "skills" folder and PARTICIPANT-PROTOCOL.md. Keep this
   folder open until setup is done.

Stuck? Post a screenshot in the cohort WhatsApp group: {{WHATSAPP_GROUP_LINK}}
Private question? WhatsApp {{COACH_NAME}}: {{WHATSAPP_DM_LINK}}
"""

INSTALL_SH = """#!/usr/bin/env bash
# Claude Code only: copies the Comeback GOAT skills into ~/.claude/skills.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p "$HOME/.claude/skills"
for z in skills/*.zip; do
  unzip -oq "$z" -d "$HOME/.claude/skills"
  echo "installed $(basename "$z" .zip)"
done
echo "Done. Restart Claude Code and work from your ComebackGOAT folder."
"""

INSTALL_PS1 = """# Claude Code only: copies the Comeback GOAT skills into ~/.claude/skills.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$dest = Join-Path $HOME ".claude\\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem skills\\*.zip | ForEach-Object {
  Expand-Archive -Force -Path $_.FullName -DestinationPath $dest
  Write-Host "installed $($_.BaseName)"
}
Write-Host "Done. Restart Claude Code and work from your ComebackGOAT folder."
"""


def values(cfg: dict) -> dict[str, str]:
    coach = cfg.get("coach") or {}
    num = re.sub(r"\D", "", str(coach.get("whatsapp_dm_number", "")))
    return {
        "COACH_NAME": str(coach.get("name", "your coach")),
        "BOOKING_URL": str(coach.get("booking_url", "SET_ME")),
        "WHATSAPP_GROUP_LINK": str(coach.get("whatsapp_group_invite", "SET_ME")),
        "WHATSAPP_DM_LINK": f"https://wa.me/{num}" if num else "SET_ME",
    }


def fill(text: str, vals: dict[str, str]) -> str:
    for k, v in vals.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def skill_zip(name: str, vals: dict[str, str], extra: dict[str, str] | None = None) -> bytes:
    """ZIP with the skill folder at the root, as Claude's skill upload expects."""
    buf = io.BytesIO()
    src = SKILLS / name
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_dir() or SKIP & set(f.parts):
                continue
            rel = f.relative_to(src).as_posix()
            if extra and rel in extra:
                continue  # replaced by the filled-in version below
            arc = f"{name}/{rel}"
            if f.suffix == ".md":
                z.writestr(arc, fill(f.read_text(encoding="utf-8"), vals))
            else:
                z.write(f, arc)
        for arc, content in (extra or {}).items():
            z.writestr(f"{name}/{arc}", content)
    return buf.getvalue()


def build(draft: bool = False, out: Path = DIST) -> dict:
    cfg = yaml.safe_load((PROGRAM / "cohort.yaml").read_text(encoding="utf-8"))
    vals = values(cfg)
    missing = [k for k, v in vals.items() if v == "SET_ME"]
    if missing and not draft:
        sys.exit("Fill these in program/cohort.yaml first (or pass --draft): " + ", ".join(missing))
    for name in REQUIRED_SKILLS + OPTIONAL_SKILLS:
        if not (SKILLS / name / "SKILL.md").is_file():
            sys.exit(f"missing skill: {name}")

    if out.exists():
        shutil.rmtree(out)
    kit = out / "comeback-goat-kit"
    (kit / "skills").mkdir(parents=True)
    (out / "coach").mkdir(parents=True)

    (kit / "README-FIRST.txt").write_text(fill(README, vals), encoding="utf-8")
    for doc in ("CLAUDE-SETUP.md", "PARTICIPANT-PROTOCOL.md"):
        (kit / doc).write_text(fill((PROGRAM / doc).read_text(encoding="utf-8"), vals), encoding="utf-8")
    for name in REQUIRED_SKILLS + OPTIONAL_SKILLS:
        (kit / "skills" / f"{name}.zip").write_bytes(skill_zip(name, vals))
    (kit / "install.sh").write_text(INSTALL_SH, encoding="utf-8")
    (kit / "install.sh").chmod(0o755)
    (kit / "install.ps1").write_text(INSTALL_PS1, encoding="utf-8")

    kit_zip = out / "comeback-goat-kit.zip"
    with zipfile.ZipFile(kit_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(kit.rglob("*")):
            if f.is_file():
                z.write(f, f"comeback-goat-kit/{f.relative_to(kit).as_posix()}")

    coach_cfg = (PROGRAM / "cohort.yaml").read_text(encoding="utf-8")
    (out / "coach" / "cohort-operator.zip").write_bytes(
        skill_zip("cohort-operator", vals, {"references/cohort.yaml": coach_cfg}))

    report = {"kit": str(kit_zip), "skills": REQUIRED_SKILLS + OPTIONAL_SKILLS,
              "coach": str(out / "coach" / "cohort-operator.zip"), "unset": missing}
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", action="store_true", help="build even if links are still SET_ME")
    a = ap.parse_args()
    r = build(draft=a.draft)
    print(f"kit:   {r['kit']}  ({len(r['skills'])} skills)")
    print(f"coach: {r['coach']}")
    if r["unset"]:
        print("WARNING, still SET_ME: " + ", ".join(r["unset"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
