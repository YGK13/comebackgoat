"""Tests for the Context Pack validator. Run: python3 -m unittest discover tests"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/revenue-engine-setup/scripts/validate_pack.py"
SAMPLE = ROOT / "examples/sample-workspace"


def run(ws: Path, *extra: str):
    p = subprocess.run([sys.executable, str(SCRIPT), str(ws), *extra], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ws = self.tmp / "ws"
        shutil.copytree(SAMPLE, self.ws)
        self.ctx = self.ws / "context"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def append(self, name: str, text: str):
        with open(self.ctx / name, "a", encoding="utf-8") as f:
            f.write(text)

    def replace(self, name: str, old: str, new: str):
        p = self.ctx / name
        t = p.read_text(encoding="utf-8")
        self.assertIn(old, t)
        p.write_text(t.replace(old, new), encoding="utf-8")

    def test_sample_is_valid_and_exports(self):
        out_file = self.tmp / "pack.json"
        code, out = run(self.ws, "--export", str(out_file))
        self.assertEqual(code, 0, out)
        pack = json.loads(out_file.read_text())
        self.assertEqual(pack["pack_version"], "1.0")
        ids = [c["id"] for c in pack["claims"]]
        self.assertIn("coo-18y", ids)

    def test_private_claims_not_exported(self):
        self.replace("claims.yaml", "ok_for: [applications]", "ok_for: [private]")
        out_file = self.tmp / "pack.json"
        code, out = run(self.ws, "--export", str(out_file))
        self.assertEqual(code, 0, out)
        ids = [c["id"] for c in json.loads(out_file.read_text())["claims"]]
        self.assertNotIn("first-clients", ids)

    def test_ssn_is_rejected(self):
        self.append("profile.md", "\nSSN 123-45-6789\n")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("Social Security", out)

    def test_card_number_is_rejected(self):
        self.append("evidence.md", "\n| card | 4111 1111 1111 1111 | stmt |\n")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("payment card", out)

    def test_phone_number_is_not_a_card(self):
        code, out = run(self.ws)
        self.assertEqual(code, 0, out)

    def test_claim_without_source_fails(self):
        self.replace("claims.yaml", 'source: "LinkedIn profile PDF"', 'source: ""')
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("missing source", out)

    def test_never_say_term_in_kit_fails(self):
        self.append("messaging-kit.md", "\nFormer COO at Midwest Freight Holdings.\n")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("never_say", out)

    def test_weights_must_sum_to_100(self):
        self.replace("lanes.yaml", "weights: {fit: 30, value: 25, odds: 20", "weights: {fit: 50, value: 25, odds: 20")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("sum to 120", out)

    def test_autopilot_must_be_draft_only(self):
        self.replace("lanes.yaml", "approval: draft_only", "approval: auto_send")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("draft_only", out)

    def test_job_cap_above_10_fails(self):
        self.replace("lanes.yaml", "daily_cap: 5", "daily_cap: 50")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("daily_cap", out)

    def test_ein_number_field_rejected(self):
        self.replace("claims.yaml", "ein_on_file: true", "ein_on_file: true\n  ein: \"12-3456789\"")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("entity.ein", out)

    def test_template_example_claim_rejected(self):
        tmpl = ROOT / "skills/revenue-engine-setup/references/templates/claims.yaml"
        shutil.copy(tmpl, self.ctx / "claims.yaml")
        code, out = run(self.ws)
        self.assertEqual(code, 1)
        self.assertIn("template example", out)


if __name__ == "__main__":
    unittest.main()
