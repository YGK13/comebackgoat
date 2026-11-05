"""Cohort operator: screening, sprint calendar, health and drafts due. Run: python3 -m unittest discover tests"""
import importlib.util
import json
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cohort", ROOT / "skills/cohort-operator/scripts/cohort.py")
cohort = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cohort)

REPORT = ("Day {d} of 14 · Streak {s}\nSent today: {t} (R4)\nTotal sent: {n} · Replies received: {r} · "
          "Calls booked: 0 · Offers sent: 0\nMoney found or collected: nothing\nStuck on: {k}\n"
          "Tomorrow's top 3: a\nTracker: not shared")


class CohortTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ops = Path(self.tmp.name) / "ops"
        cohort.main(["init", str(self.ops), "--day1", "2026-11-16"])  # a Monday
        cfg = (self.ops / "cohort.yaml").read_text()
        # Override whatever the live cohort.yaml holds, so the test never depends on real links.
        cfg = re.sub(r'booking_url: "[^"]*"', 'booking_url: "https://calendly.com/x/30"', cfg)
        cfg = re.sub(r'whatsapp_dm_number: "[^"]*"', 'whatsapp_dm_number: "+1 555 123 4567"', cfg)
        cfg = re.sub(r'whatsapp_group_invite: "[^"]*"', 'whatsapp_group_invite: "https://chat.whatsapp.com/A"', cfg)
        cfg = re.sub(r'(kit:\n(?:  #.*\n)*  link: )"[^"]*"', r'\1"SET_ME"', cfg)
        (self.ops / "cohort.yaml").write_text(cfg)
        apps = [{"name": "Dana Levi", "email": "dana@x.com", "linkedin": "https://linkedin.com/in/d",
                 "situation": "Laid off in the last 6 months", "role": "VP People",
                 "goal": "Two consulting clients at $10K each by February 2027"}]
        f = Path(self.tmp.name) / "apps.json"
        f.write_text(json.dumps(apps))
        cohort.main(["ingest", str(self.ops), str(f)])
        cohort.main(["ingest", str(self.ops), str(f)])  # dedupe

    def tearDown(self):
        self.tmp.cleanup()

    def roster(self):
        return cohort.read_csv(self.ops / "roster.csv", cohort.ROSTER_COLS)

    def add_reports(self, items):
        f = Path(self.tmp.name) / "r.json"
        f.write_text(json.dumps(items))
        cohort.main(["reports", str(self.ops), str(f)])

    def test_ingest_dedupes_and_screen_recommends(self):
        self.assertEqual(len(self.roster()), 1)
        cohort.main(["screen", str(self.ops)])
        self.assertEqual(self.roster()[0]["recommendation"], "accept")

    def test_red_flag_caps_score(self):
        s, flags, rec = cohort.screen_one({"situation": "Left by choice", "role": "VP Sales",
                                           "goal": "I need a guarantee you will find me a job fast", "linkedin": ""})
        self.assertEqual(rec, "decline")
        self.assertTrue(any("red flag" in x for x in flags))

    def test_sprint_days_skip_weekends(self):
        cfg = cohort.load_config(self.ops)
        p = self.roster()[0]
        self.assertEqual(cohort.sprint_day(cfg, p, date(2026, 11, 16)), 1)
        self.assertIsNone(cohort.sprint_day(cfg, p, date(2026, 11, 21)))  # Saturday
        self.assertEqual(cohort.sprint_day(cfg, p, date(2026, 11, 23)), 6)
        self.assertEqual(cohort.date_of_day(cfg, p, 14), date(2026, 12, 3))

    def test_thursday_drafts_friday_for_schedule_send(self):
        cohort.main(["set", str(self.ops), "dana@x.com", "status=active"])
        t = cohort.today(self.ops, date(2026, 11, 19))  # Thursday, Day 4
        missions = [d for d in t["drafts_due"] if d["template"].startswith("Day ")]
        self.assertEqual([d["template"] for d in missions], ["Day 4", "Day 5"])
        self.assertIn("schedule_send", missions[1])

    def test_health_yellow_behind_then_red_quiet(self):
        cohort.main(["set", str(self.ops), "dana@x.com", "status=active"])
        self.add_reports([
            {"email": "dana@x.com", "date": "2026-11-18", "body": REPORT.format(d=3, s=1, t=0, n=0, r=0, k="nothing")},
            {"email": "dana@x.com", "date": "2026-11-19", "body": REPORT.format(d=4, s=2, t=3, n=3, r=0, k="nothing")},
        ])
        cfg = cohort.load_config(self.ops)
        p = self.roster()[0]
        status, why = cohort.health(cfg, p, cohort.read_csv(self.ops / "reports.csv", cohort.REPORT_COLS), date(2026, 11, 20))
        self.assertEqual(status, "yellow")
        self.assertIn("behind", why[0])
        status, _ = cohort.health(cfg, p, cohort.read_csv(self.ops / "reports.csv", cohort.REPORT_COLS), date(2026, 11, 24))
        self.assertEqual(status, "red")

    def test_report_parsing_blanks_nothing(self):
        r = cohort.parse_report(REPORT.format(d=6, s=3, t=2, n=14, r=3, k="nothing"))
        self.assertEqual((r["day"], r["total_sent"], r["replies"], r["stuck"], r["tracker"]), ("6", "14", "3", "", ""))

    def test_marked_drafts_are_not_due_again(self):
        cohort.main(["set", str(self.ops), "dana@x.com", "status=paid"])
        self.assertIn("S3", [d["template"] for d in cohort.today(self.ops, date(2026, 11, 10))["drafts_due"]])
        cohort.main(["mark", str(self.ops), "dana@x.com", "S3"])
        self.assertNotIn("S3", [d["template"] for d in cohort.today(self.ops, date(2026, 11, 10))["drafts_due"]])

    def test_render_fills_links_and_strips_markdown(self):
        cfg = cohort.load_config(self.ops)
        r = cohort.render(cfg, "Day 4", self.roster()[0], date(2026, 11, 19))
        self.assertTrue(r["body"].startswith("Hi Dana,"))
        self.assertIn("https://wa.me/15551234567", r["body"])
        self.assertNotIn("**", r["body"])
        self.assertNotIn("{{", r["body"])
        s3 = cohort.render(cfg, "S3", self.roster()[0], date(2026, 11, 10))
        self.assertEqual(s3["unset"], ["KIT_LINK"])  # kit link still SET_ME in this test

    def test_every_template_parses(self):
        t = cohort.load_templates()
        for tid in ["S1", "S2", "S3", "S4", "D15", "D30", "T1", "T2", "T3", "T4", "G0", "G5"] + [f"Day {n}" for n in range(1, 15)]:
            self.assertIn(tid, t)
            if t[tid]["kind"] == "email":
                self.assertTrue(t[tid]["subject"], tid)


if __name__ == "__main__":
    unittest.main()
