"""Tests for the boomerang roster. Run: python3 -m unittest discover tests"""
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/boomerang/scripts/boomerang_targets.py"
LANES = """boomerang:
  enabled: true
  default_offer: consultant_first
  employers:
    - {name: "Acme Health Inc.", left_on: "2025-06-30", left_as: "VP People", terms: good, restriction_until: "2025-12-31", rehire_ok: true}
    - {name: "Northwind", left_on: "2026-03-01", left_as: "CHRO", terms: neutral, restriction_until: "2027-03-01"}
    - {name: "Globex", left_on: "2024-01-15", terms: difficult}
    - {name: "Initech", left_on: "2012-05-01", terms: good}
"""
INDEX = {"meta": {}, "people": [
    {"name": "Sam Ortiz", "company": "Acme Health", "title": "COO", "warmth": 71, "msg_last": "2026-08-01", "linkedin": "https://linkedin.com/in/sam"},
    {"name": "Lee Park", "company": "Acme Health, Inc.", "title": "Director HR", "warmth": 40, "msg_last": "", "linkedin": ""},
    {"name": "Cold Contact", "company": "Acme Health", "title": "Analyst", "warmth": 12, "msg_last": "", "linkedin": ""},
    {"name": "Nia Bell", "company": "Northwind", "title": "CEO", "warmth": 90, "msg_last": "", "linkedin": ""},
    {"name": "Acme Fan", "company": "Acme Healthcare Partners", "title": "VP", "warmth": 60, "msg_last": "", "linkedin": ""},
]}


def run(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class BoomerangTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ws = self.tmp / "ws"
        (self.ws / "context").mkdir(parents=True)
        (self.ws / "context" / "lanes.yaml").write_text(LANES, encoding="utf-8")
        self.idx = self.tmp / "network.json"
        self.idx.write_text(json.dumps(INDEX), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def roster(self, *extra):
        code, out = run(str(self.ws), "--index", str(self.idx), "--date", "2026-11-05", "--json", *extra)
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def test_statuses(self):
        by = {e["name"]: e for e in self.roster()["employers"]}
        self.assertEqual(by["Acme Health Inc."]["status"], "eligible")
        self.assertEqual(by["Northwind"]["status"], "blocked")
        self.assertIn("2027-03-01", by["Northwind"]["reason"])
        self.assertEqual(by["Globex"]["status"], "ask")
        self.assertEqual(by["Initech"]["status"], "stale")

    def test_blocked_employer_gets_no_insiders(self):
        by = {e["name"]: e for e in self.roster()["employers"]}
        self.assertEqual(by["Northwind"]["insiders"], [])

    def test_insiders_match_company_and_warmth_floor(self):
        acme = self.roster()["employers"][0]
        names = [p["name"] for p in acme["insiders"]]
        self.assertEqual(names, ["Sam Ortiz", "Lee Park"])  # cold contact under floor; "Acme Healthcare Partners" is not Acme Health

    def test_offer_defaults_to_consultant_first(self):
        by = {e["name"]: e for e in self.roster()["employers"]}
        self.assertEqual(by["Initech"]["offer"], "consultant_first")

    def test_write_rows_once(self):
        data = self.roster("--write")
        self.assertEqual(data["written"], 1)
        again = self.roster("--write")
        self.assertEqual(again["written"], 0)
        with open(self.ws / "trackers" / "boomerang.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["id"], "B-1")
        self.assertEqual(rows[0]["stage"], "warm")
        self.assertEqual(rows[0]["status"], "found")

    def test_planner_picks_up_boomerang_rows(self):
        self.roster("--write")
        planner = ROOT / "skills/daily-plan/scripts/plan_today.py"
        p = subprocess.run([sys.executable, str(planner), "plan", str(self.ws), "--date", "2026-11-05", "--json"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        plan = json.loads(p.stdout)
        item = plan["claude"][0]
        self.assertEqual(item["id"], "B-1")
        self.assertEqual(item["engine"], "boomerang")
        self.assertEqual(item["r"], 4)


if __name__ == "__main__":
    unittest.main()
