#!/usr/bin/env python3
"""Every listed attack still refuses. Secure-behavior checks only. No payloads."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from garde import CODES, deny, scan  # noqa: E402

TODAY = date(2026, 9, 3)
SHA = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# Claims / scan probes for each deny code listed in README, JUGE.md, MERGE.md.
# Values are forbidden *claims* the gate must refuse — not procedures.
LISTED_CLAIMS: dict[str, dict] = {
    "FAIL_CLOSED": {"hello": 1},
    "MALFORMED": None,  # type: ignore[dict-item]
    "EPSILON_ZERO": {"format": "epsilon.v0", "modele": "composable", "epsilon": 0},
    "EPSILON_MISSING": {
        "quelle": "os",
        "temoin": "aucun",
        "horizon": "2099-12-31",
    },
    "QUANTUM_WITHOUT_CARDS": {"format": "mode.v0", "mode": "quantique"},
    "LOOPHOLES_CLOSED_INCOMPLETE": {
        "format": "bruit.v0",
        "trous": "fermes",
        "detection": "fermee",
        "localite": "fermee",
        "liberte": "fermee",
        "simule": True,
    },
    "CHSH_SOFTWARE_AS_DI": {
        "format": "temoin.v0",
        "niveau": "di",
        "simule": True,
        "transcript_sha256": SHA,
        "chsh": 2.4,
    },
    "PHOTON_INVENTED_AS_QRNG": {
        "format": "quelle.v0",
        "source": "qrng",
        "appareil": None,
        "simule": True,
    },
    "OS_RELABEL_QKD": {
        "format": "quelle.v0",
        "source": "qkd",
        "appareil": "os.urandom",
        "simule": True,
    },
    "HORIZON_SLOGAN": {
        "format": "horizon.v0",
        "suite": "quantum-safe",
        "re_presser_avant": "2099-12-31",
    },
    "HORIZON_DATE_INVALID": {
        "quelle": "os",
        "temoin": "aucun",
        "epsilon": 0.000001,
        "horizon": "UFHY1",
    },
    "FIGURE_MINOR_OR_NO_END": {
        "format": "figure.v0",
        "majeur": False,
        "fin": "2099-12-31",
        "usages": ["nom"],
    },
    "SITUS_MEDICAL_OR_UNLICENSED": {
        "format": "situs.v0",
        "usages": ["medical"],
        "nom_public": "exemple",
    },
    "TOKEN_MINT_COIN": {"format": "recu.v0", "token": "x", "rail": "cash"},
    "PREVIEW_AS_RECEIPT": {
        "format": "recu.v0",
        "preview": True,
        "assert": "quittance",
        "rail": "cash",
        "montant_cents": 100,
    },
    "UNFORGE_SIGNS": {"format": "unforge.v0", "role": "sign", "file": "x"},
    "QUANTUM_IN_GIT": {
        "format": "temoin.v0",
        "niveau": "aucun",
        "transcript": "raw-log-not-a-hash",
    },
    "ESTOC_MERGE": {"format": "estoc.v0", "rail": "estoc"},
    "NEW_GROK_HOST": {"format": "mode.v0", "mode": "classique", "host": "other.grok.me"},
    "SECOND_SLUG": {
        "format": "mode.v0",
        "mode": "classique",
        "slugs": ["acorn-royal-dune-blend.grok.me", "other.grok.me"],
    },
}

# Scan-only listed codes — same catalog shape as LISTED_CLAIMS.
# Rel paths are probes for scan(), not exploit recipes.
LISTED_SCANS: dict[str, tuple[str, ...]] = {
    "FAMILLE_SITE_TOUCHED": ("famille", "site", "index.html"),
}


def _readme_listed_codes() -> list[str]:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    start = text.index("## Deny criteria")
    end = text.index("Physics enters", start)
    found: list[str] = []
    for a, b in re.findall(
        r"^\| `([A-Z][A-Z0-9_]+)`(?: / `([A-Z][A-Z0-9_]+)`)?",
        text[start:end],
        flags=re.M,
    ):
        found.append(a)
        if b:
            found.append(b)
    return found


def _juge_listed_fixtures() -> list[str]:
    text = (ROOT / "JUGE.md").read_text(encoding="utf-8")
    return re.findall(r"examples/(deny-[a-z0-9-]+\.json)", text)


class ListedCatalogComplete(unittest.TestCase):
    def test_every_code_is_listed_in_readme(self) -> None:
        listed = _readme_listed_codes()
        self.assertEqual(set(CODES), set(listed), (set(CODES) - set(listed), set(listed) - set(CODES)))

    def test_every_listed_code_has_a_refuse_probe(self) -> None:
        covered = set(LISTED_CLAIMS) | set(LISTED_SCANS)
        self.assertEqual(set(CODES), covered)

    def test_each_listed_claim_still_refuses(self) -> None:
        for code, claim in LISTED_CLAIMS.items():
            with self.subTest(code=code):
                verdict = deny(claim, today=TODAY)
                self.assertEqual(verdict["decision"], "deny", verdict)
                self.assertIn(code, verdict["codes"], verdict)
                self.assertEqual(verdict["format"], "garde.deny.v0")

    def test_each_listed_scan_still_refuses(self) -> None:
        for code, rel in LISTED_SCANS.items():
            with self.subTest(code=code):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    path = root.joinpath(*rel)
                    path.parent.mkdir(parents=True)
                    path.write_text("placeholder\n", encoding="utf-8")
                    verdict = scan(root)
                    self.assertEqual(verdict["decision"], "deny", verdict)
                    self.assertIn(code, verdict["codes"], verdict)
                    self.assertEqual(verdict["format"], "garde.deny.v0")

    def test_famille_site_touched(self) -> None:
        rel = LISTED_SCANS["FAMILLE_SITE_TOUCHED"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root.joinpath(*rel)
            path.parent.mkdir(parents=True)
            path.write_text("placeholder\n", encoding="utf-8")
            verdict = scan(root)
            self.assertEqual(verdict["decision"], "deny", verdict)
            self.assertIn("FAMILLE_SITE_TOUCHED", verdict["codes"])

    def test_juge_listed_fixtures_still_deny(self) -> None:
        names = _juge_listed_fixtures()
        self.assertGreaterEqual(len(names), 13)
        for name in names:
            with self.subTest(name=name):
                path = ROOT / "examples" / name
                self.assertTrue(path.is_file(), path)
                claim = json.loads(path.read_text(encoding="utf-8"))
                verdict = deny(claim, today=TODAY)
                self.assertEqual(verdict["decision"], "deny", (name, verdict))

    def test_license_holds_mit(self) -> None:
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("MIT License"))
        self.assertIn("Carl Laliberté", text)
        self.assertIn("2026", text)

    def test_landing_preview_is_not_receipt(self) -> None:
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Preview ≠ receipt", html)
        self.assertNotRegex(html, r"\bQuantum\b")


class ListedVariantsStillRefuse(unittest.TestCase):
    """README / JUGE wording that already has a deny rule, now named."""

    def test_iid_used_as_bound(self) -> None:
        verdict = deny(
            {
                "quelle": "os",
                "temoin": "aucun",
                "epsilon": "iid",
                "horizon": "2099-12-31",
            },
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("EPSILON_ZERO", verdict["codes"])

    def test_chsh_at_or_below_two(self) -> None:
        verdict = deny(
            {
                "format": "temoin.v0",
                "niveau": "di",
                "simule": False,
                "transcript_sha256": SHA,
                "chsh": 2,
            },
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("CHSH_SOFTWARE_AS_DI", verdict["codes"])

    def test_chsh_above_tsirelson(self) -> None:
        verdict = deny(
            {
                "format": "temoin.v0",
                "niveau": "di",
                "simule": False,
                "transcript_sha256": SHA,
                "chsh": 3,
            },
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("CHSH_SOFTWARE_AS_DI", verdict["codes"])

    def test_ibm_job_as_horizon_slogan(self) -> None:
        verdict = deny(
            {
                "format": "horizon.v0",
                "suite": "ed25519",
                "re_presser_avant": "2099-12-31",
                "ibm_job": "ibm-quantum-safe",
            },
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("HORIZON_SLOGAN", verdict["codes"])

    def test_node_quantum_in_claim(self) -> None:
        verdict = deny(
            {"format": "mode.v0", "mode": "classique", "node": "quantum"},
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("QUANTUM_IN_GIT", verdict["codes"])

    def test_unforge_signed_flag(self) -> None:
        verdict = deny(
            {"format": "unforge.v0", "signed": True, "file": "x"},
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("UNFORGE_SIGNS", verdict["codes"])

    def test_juge_http_200_is_not_a_receipt(self) -> None:
        verdict = deny(
            {
                "quelle": "os",
                "temoin": "aucun",
                "epsilon": 0.000001,
                "horizon": "2099-12-31",
                "path": "/juge",
                "status": 200,
                "assert": "quittance",
            },
            today=TODAY,
        )
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("PREVIEW_AS_RECEIPT", verdict["codes"])

    def test_second_slug_fixture_under_tests(self) -> None:
        claim = json.loads(
            (ROOT / "tests" / "fixtures" / "deny-second-slug.json").read_text(encoding="utf-8")
        )
        verdict = deny(claim, today=TODAY)
        self.assertEqual(verdict["decision"], "deny", verdict)
        self.assertIn("SECOND_SLUG", verdict["codes"])


if __name__ == "__main__":
    unittest.main()
