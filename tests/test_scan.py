#!/usr/bin/env python3
"""Artifact-scan tests. Forbidden names and extra hosts must deny. No payloads."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from garde import LIVE_HOST, scan  # noqa: E402


class ScanThisRepo(unittest.TestCase):
    def test_garde_tree_is_clean(self) -> None:
        verdict = scan(ROOT)
        self.assertEqual(verdict["decision"], "allow", verdict)
        self.assertEqual(verdict["findings"], [])

    def test_cli_scan_exit_0_here(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "garde.py"), "scan", "--root", str(ROOT)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(json.loads(proc.stdout)["decision"], "allow")


class ScanFixtures(unittest.TestCase):
    def test_quantum_db_filename_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quantum.db").write_bytes(b"")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "deny")
            self.assertIn("QUANTUM_IN_GIT", verdict["codes"])

    def test_famille_site_path_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "famille" / "site" / "index.html"
            path.parent.mkdir(parents=True)
            path.write_text("<p>no</p>\n", encoding="utf-8")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "deny")
            self.assertIn("FAMILLE_SITE_TOUCHED", verdict["codes"])

    def test_famille_site_touched(self) -> None:
        """Catalog-style named refuse: FAMILLE_SITE_TOUCHED via scan()."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "famille" / "site" / "index.html"
            path.parent.mkdir(parents=True)
            path.write_text("placeholder\n", encoding="utf-8")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "deny", verdict)
            self.assertIn("FAMILLE_SITE_TOUCHED", verdict["codes"])

    def test_famille_site_touched_via_scan(self) -> None:
        """Listed attack FAMILLE_SITE_TOUCHED — scan refuses famille/site/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "famille" / "site" / "readme.txt"
            path.parent.mkdir(parents=True)
            path.write_text("placeholder\n", encoding="utf-8")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "deny", verdict)
            self.assertIn("FAMILLE_SITE_TOUCHED", verdict["codes"])
            self.assertTrue(
                any(
                    f.get("code") == "FAMILLE_SITE_TOUCHED"
                    and "famille/site/" in f.get("path", "").replace("\\", "/")
                    for f in verdict.get("findings", [])
                ),
                verdict,
            )

    def test_extra_grok_host_in_config_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "host.toml").write_text('url = "https://other.grok.me"\n', encoding="utf-8")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "deny")
            self.assertIn("NEW_GROK_HOST", verdict["codes"])

    def test_live_host_alone_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("https://" + LIVE_HOST + "\n", encoding="utf-8")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "allow", verdict)

    def test_missing_root_fails_closed(self) -> None:
        verdict = scan(Path("/tmp/garde-does-not-exist-4981"))
        self.assertEqual(verdict["decision"], "deny")
        self.assertIn("FAIL_CLOSED", verdict["codes"])


if __name__ == "__main__":
    unittest.main()
