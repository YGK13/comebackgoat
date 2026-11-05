"""Tests for the network index. Run: python3 -m unittest discover tests"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/network-engine/scripts/network_index.py"
FX = ROOT / "tests/fixtures/network"


def run(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class NetworkIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.out = cls.tmp / "network.json"
        code, out = run("build", "--owner", "Dana Reyes", "--out", str(cls.out),
                        "--connections", str(FX / "Connections.csv"), "--contacts", str(FX / "contacts.csv"),
                        "--messages", str(FX / "messages.csv"))
        assert code == 0, out
        cls.data = json.loads(cls.out.read_text())
        cls.by = {p["name"]: p for p in cls.data["people"]}

    def test_merges_linkedin_and_contacts(self):
        self.assertEqual(self.data["meta"]["people"], 4)
        self.assertEqual(sorted(self.by["Priya Shah"]["sources"]), ["contacts", "linkedin"])

    def test_owner_not_indexed(self):
        self.assertNotIn("Dana Reyes", self.by)

    def test_messages_counted_both_directions_and_drafts_skipped(self):
        p = self.by["Priya Shah"]
        self.assertEqual((p["msg_total"], p["msg_sent"], p["msg_received"]), (2, 1, 1))
        self.assertEqual(self.by["Lena Ortiz"]["msg_total"], 0)

    def test_warmest_first(self):
        self.assertEqual(self.data["people"][0]["name"], "Priya Shah")
        self.assertGreater(self.by["Priya Shah"]["warmth"], self.by["Tom Becker"]["warmth"])
        for p in self.data["people"]:
            self.assertTrue(0 <= p["warmth"] <= 100)

    def test_company_lookup_is_word_bounded(self):
        code, out = run("lookup", "--index", str(self.out), "--company", "Acme Health")
        names = [p["name"] for p in json.loads(out)]
        self.assertEqual(set(names), {"Priya Shah", "Lena Ortiz"})
        code, out = run("lookup", "--index", str(self.out), "--company", "Anthropic")
        self.assertEqual(json.loads(out), [])

    def test_no_message_content_stored(self):
        self.assertNotIn("hello", self.out.read_text())

    def test_stats(self):
        code, out = run("stats", "--index", str(self.out))
        self.assertEqual(code, 0, out)
        self.assertIn("warmth_bands", json.loads(out))


if __name__ == "__main__":
    unittest.main()
