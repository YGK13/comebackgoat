"""Tests for the today planner. Run: python3 -m unittest discover tests"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/daily-plan/scripts/plan_today.py"
HEADER = "id,date_found,engine,title,link,value_usd,status,deadline,score,prepared,next_action,notes,updated,minutes,stage\n"
TODAY = "2026-11-05"  # a Thursday


def run(ws, *args):
    p = subprocess.run([sys.executable, str(SCRIPT), *args[:1], str(ws), *args[1:]], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ws = self.tmp / "ws"
        (self.ws / "context").mkdir(parents=True)
        (self.ws / "trackers").mkdir()
        (self.ws / "context" / "lanes.yaml").write_text(
            "today:\n  focus_mode: false\n  human_minutes_per_day: 60\n  max_items: 7\n  follow_up_days: 5\n"
            "project_hunter:\n  project_minimum_usd: 5000\n", encoding="utf-8")
        (self.ws / "context" / "constraints.yaml").write_text(
            "schedule:\n  days_off: [Saturday]\n  timezone: America/New_York\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rows(self, name, lines):
        (self.ws / "trackers" / name).write_text(HEADER + "\n".join(lines) + "\n", encoding="utf-8")

    def plan(self, *extra):
        code, out = run(self.ws, "plan", "--date", TODAY, "--json", *extra)
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def test_cash_beats_bigger_cold_lead(self):
        self.rows("projects.csv", [
            "P-9,2026-11-01,project-hunter,Public post fractional CHRO,,20000,needs_you,,70,Comment drafted,Post comment,,,,cold",
            "M-1,2026-11-01,money-sweep,Unpaid invoice Client B,,4200,needs_you,,,Reminder draft,Send reminder draft,,,,",
        ])
        p = self.plan()
        self.assertEqual([i["id"] for i in p["you"]][:2], ["M-1", "P-9"])
        self.assertEqual(p["you"][0]["r"], 1)

    def test_deadline_inside_48h_goes_first(self):
        self.rows("all.csv", [
            "M-1,2026-11-01,money-sweep,Unpaid invoice,,4200,needs_you,,,Reminder draft,Send reminder draft,,,,",
            "G-7,2026-11-01,grant-hunter,State microgrant,,5000,needs_you,2026-11-06,80,Form filled,Submit (tab open),,,,",
        ])
        self.assertEqual(self.plan()["you"][0]["id"], "G-7")

    def test_found_goes_to_claude_and_old_sent_gets_follow_up(self):
        self.rows("projects.csv", [
            "P-1,2026-11-04,project-hunter,Inbound speaking request,,,found,,,,Reply in thread,,,,",
            "P-2,2026-10-20,project-hunter,Proposal to Acme,,12000,sent,,,,,,2026-10-29,,close",
            "P-3,2026-11-03,project-hunter,Proposal to Beta,,9000,sent,,,,,,2026-11-03,,close",
        ])
        p = self.plan()
        ids = {i["id"]: i for i in p["claude"]}
        self.assertIn("P-1", ids)
        self.assertIn("P-2", ids)
        self.assertIn("follow-up", ids["P-2"]["action"])
        self.assertNotIn("P-3", ids)
        self.assertEqual(p["waiting"], 1)

    def test_focus_mode_caps_and_leads_with_starter(self):
        self.rows("all.csv", [
            "P-1,2026-11-01,project-hunter,Discovery call Acme,,15000,needs_you,,,,Prep and take the call,,,45,conversation",
            "M-1,2026-11-01,money-sweep,Payout claim,,300,needs_you,,,Claim link,Open claim link and confirm,,,4,",
            "P-2,2026-11-01,project-hunter,Warm note to former boss,,,needs_you,,,Draft,Send draft,,,,warm",
            "P-3,2026-11-01,project-hunter,Warm note to former client,,,needs_you,,,Draft,Send draft,,,,warm",
            "P-4,2026-11-01,project-hunter,Warm note to colleague,,,needs_you,,,Draft,Send draft,,,,warm",
        ])
        p = self.plan("--focus")
        self.assertTrue(p["focus_mode"])
        self.assertEqual(len(p["you"]), 3)
        self.assertTrue(p["you"][0].get("starter"))
        self.assertLessEqual(p["you"][0]["minutes"], 10)
        self.assertEqual(len(p["parked"]), 2)

    def test_live_and_decide_classification(self):
        self.rows("all.csv", [
            "P-1,2026-11-01,project-hunter,Discovery call Acme,,,needs_you,,,,Take the call at 15:00,,,,",
            "P-2,2026-11-01,project-hunter,Pricing for Beta,,,needs_you,,,,Decide the fee range,,,,",
        ])
        ex = {i["id"]: i["executor"] for i in self.plan()["you"]}
        self.assertEqual(ex, {"P-1": "you_live", "P-2": "you_decide"})

    def test_day_off(self):
        self.rows("all.csv", ["M-1,2026-11-01,money-sweep,Invoice,,100,needs_you,,,,Send,,,,"])
        code, out = run(self.ws, "plan", "--date", "2026-11-07")
        self.assertEqual(code, 0)
        self.assertIn("day off", out)

    def test_expired_is_not_ranked(self):
        self.rows("all.csv", ["G-1,2026-10-01,grant-hunter,Old grant,,5000,needs_you,2026-11-01,,,Submit,,,,"])
        p = self.plan()
        self.assertEqual(p["you"], [])
        self.assertEqual(p["expired"][0]["id"], "G-1")

    def test_learn_moves_rates_and_planner_uses_them(self):
        lines = [f"P-{n},2026-06-01,project-hunter,Warm note {n},,,lost,,,,,,2026-07-01,,warm" for n in range(20)]
        lines += [f"P-{n},2026-06-01,project-hunter,Warm note {n},,,won,,,,,,2026-07-01,,warm" for n in range(20, 30)]
        self.rows("history.csv", lines)
        code, out = run(self.ws, "learn", "--date", TODAY)
        self.assertEqual(code, 0, out)
        cal = json.loads((self.ws / "trackers" / "calibration.json").read_text())
        rate = cal["stage"]["warm"]["rate"]
        self.assertGreater(rate, 0.05)          # 10 wins in 30 pulls the 5% prior up
        self.assertAlmostEqual(rate, (10 + 0.05 * 10) / 40, places=3)
        self.rows("open.csv", ["P-99,2026-11-01,project-hunter,Warm note,,,needs_you,,,Draft,Send draft,,,,warm"])
        p = self.plan()
        self.assertAlmostEqual(p["you"][0]["p"], rate, places=3)

    def test_carryover_triggers_decision_in_focus_mode(self):
        self.rows("all.csv", ["P-2,2026-11-01,project-hunter,Warm note,,,needs_you,,,Draft,Send draft,,,,warm"])
        (self.ws / "runs").mkdir()
        prev = {"you": [{"id": "P-2", "carried_days": 1}]}
        (self.ws / "runs" / "2026-11-04-today.json").write_text(json.dumps(prev))
        item = self.plan("--focus")["you"][0]
        self.assertEqual(item["carried_days"], 2)
        self.assertIn("defer", item["decide"])

    def test_suggests_cash_check_when_no_cash_items(self):
        self.rows("all.csv", ["P-9,2026-11-01,project-hunter,Public post,,,needs_you,,,,Post comment,,,,cold"])
        s = " ".join(self.plan()["suggestions"])
        self.assertIn("receivables", s)
        self.assertIn("reactivations", s)


if __name__ == "__main__":
    unittest.main()
