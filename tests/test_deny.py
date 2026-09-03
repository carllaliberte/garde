#!/usr/bin/env python3
"""Secure-behavior tests for GARDE. Assert deny / fail-closed. No exploit steps."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from garde import CODES, REASONS, deny, deny_path  # noqa: E402

TODAY = date(2026, 9, 3)
SHA = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def must_deny(claim: dict, code: str) -> None:
    verdict = deny(claim, today=TODAY)
    assert verdict["decision"] == "deny", verdict
    assert code in verdict["codes"], verdict
    assert verdict["format"] == "garde.deny.v0"


def must_allow(claim: dict) -> None:
    verdict = deny(claim, today=TODAY)
    assert verdict["decision"] == "allow", verdict
    assert verdict["codes"] == []
    assert verdict["fail_closed"] is False


class DenyCatalog(unittest.TestCase):
    def test_catalog_matches_schema_and_reasons(self) -> None:
        schema = json.loads((ROOT / "schema" / "deny.v0.json").read_text(encoding="utf-8"))
        listed = schema["properties"]["codes"]["items"]["enum"]
        self.assertEqual(list(CODES), listed)
        self.assertEqual(set(CODES), set(REASONS))


class FailClosed(unittest.TestCase):
    def test_none_is_malformed(self) -> None:
        must_deny(None, "MALFORMED")  # type: ignore[arg-type]

    def test_list_is_malformed(self) -> None:
        must_deny(["quelle", "os"], "MALFORMED")  # type: ignore[arg-type]

    def test_empty_object_fails_closed(self) -> None:
        must_deny({}, "FAIL_CLOSED")

    def test_unknown_object_fails_closed(self) -> None:
        must_deny({"hello": 1}, "FAIL_CLOSED")

    def test_unknown_format_claiming_quantum_is_denied(self) -> None:
        must_deny({"format": "nope.v9", "mode": "quantique"}, "QUANTUM_WITHOUT_CARDS")

    def test_unreadable_file_is_malformed(self) -> None:
        path = ROOT / "tests" / "fixtures" / "not-json.txt"
        path.write_text("{not json", encoding="utf-8")
        self.addCleanup(path.unlink)
        verdict = deny_path(path, today=TODAY)
        self.assertEqual(verdict["decision"], "deny")
        self.assertIn("MALFORMED", verdict["codes"])
        self.assertTrue(verdict["fail_closed"])


class HonestAllow(unittest.TestCase):
    def test_quelle_os(self) -> None:
        must_allow(json.loads((ROOT / "tests" / "fixtures" / "allow-quelle-os.json").read_text()))

    def test_mode_classique(self) -> None:
        must_allow(json.loads((ROOT / "tests" / "fixtures" / "allow-mode-classique.json").read_text()))

    def test_juge_classique_vocabulary(self) -> None:
        must_allow(json.loads((ROOT / "tests" / "fixtures" / "allow-juge-classique.json").read_text()))

    def test_temoin_aucun(self) -> None:
        must_allow(
            {
                "format": "temoin.v0",
                "temoin_id": "TM-1",
                "niveau": "aucun",
                "simule": True,
                "juridiction": "QC",
                "langue": "fr-CA",
                "pose_at": "2026-09-03T00:00:00Z",
            }
        )

    def test_epsilon_none(self) -> None:
        must_allow(
            {
                "format": "epsilon.v0",
                "epsilon_id": "EP-1",
                "modele": "none",
                "epsilon": None,
                "simule": True,
            }
        )

    def test_horizon_named_future(self) -> None:
        must_allow(
            {
                "format": "horizon.v0",
                "horizon_id": "HZ-1",
                "cible": "unforge",
                "suite": "UFHY1",
                "re_presser_avant": "2099-12-31",
                "juridiction": "QC",
            }
        )

    def test_bruit_ouverts(self) -> None:
        must_allow(
            {
                "format": "bruit.v0",
                "bruit_id": "BR-1",
                "trous": "ouverts",
                "detection": "ouverte",
                "localite": "ouverte",
                "liberte": "ouverte",
                "simule": True,
            }
        )

    def test_figure_majeur_with_end(self) -> None:
        must_allow(
            {
                "format": "figure.v0",
                "figure_id": "FG-1",
                "nom_public": "Exemple",
                "majeur": True,
                "usages": ["nom"],
                "fin": "2099-12-31",
                "revocable": True,
            }
        )

    def test_claim_envelope_unwraps_os_card(self) -> None:
        card = json.loads((ROOT / "tests" / "fixtures" / "allow-quelle-os.json").read_text())
        must_allow({"format": "garde.claim.v0", "rail": "quelle", "card": card})


class DenyCriteria(unittest.TestCase):
    def test_epsilon_zero(self) -> None:
        must_deny({"format": "epsilon.v0", "modele": "composable", "epsilon": 0}, "EPSILON_ZERO")

    def test_epsilon_zero_string(self) -> None:
        must_deny({"format": "epsilon.v0", "modele": "composable", "epsilon": "0"}, "EPSILON_ZERO")

    def test_juge_missing_epsilon_fails_closed(self) -> None:
        must_deny(
            {"quelle": "os", "temoin": "aucun", "horizon": "2099-12-31"},
            "EPSILON_MISSING",
        )
        verdict = deny(
            {"quelle": "os", "temoin": "aucun", "horizon": "2099-12-31"},
            today=TODAY,
        )
        self.assertTrue(verdict["fail_closed"])

    def test_juge_null_epsilon_fails_closed(self) -> None:
        must_deny(
            {
                "quelle": "os",
                "temoin": "aucun",
                "epsilon": None,
                "horizon": "2099-12-31",
            },
            "EPSILON_MISSING",
        )

    def test_juge_none_string_epsilon_is_zero_lie(self) -> None:
        must_deny(
            {
                "quelle": "os",
                "temoin": "aucun",
                "epsilon": "none",
                "horizon": "2099-12-31",
            },
            "EPSILON_ZERO",
        )

    def test_rail_epsilon_none_still_allowed(self) -> None:
        must_allow(
            {
                "format": "epsilon.v0",
                "epsilon_id": "EP-none",
                "modele": "none",
                "epsilon": None,
                "simule": True,
            }
        )

    def test_quantum_without_cards(self) -> None:
        must_deny({"format": "mode.v0", "mode": "quantique"}, "QUANTUM_WITHOUT_CARDS")

    def test_quantum_os_juge_cannot_pass(self) -> None:
        must_deny(
            {
                "mode": "quantique",
                "quelle": "os",
                "temoin": "aucun",
                "epsilon": 0.000001,
                "horizon": "2099-12-31",
            },
            "QUANTUM_WITHOUT_CARDS",
        )

    def test_loopholes_closed_while_simulated(self) -> None:
        must_deny(
            {
                "format": "bruit.v0",
                "trous": "fermes",
                "detection": "fermee",
                "localite": "fermee",
                "liberte": "fermee",
                "simule": True,
            },
            "LOOPHOLES_CLOSED_INCOMPLETE",
        )

    def test_loopholes_closed_missing_one(self) -> None:
        must_deny(
            {
                "format": "bruit.v0",
                "trous": "fermes",
                "detection": "fermee",
                "localite": "fermee",
                "liberte": "ouverte",
                "simule": False,
            },
            "LOOPHOLES_CLOSED_INCOMPLETE",
        )

    def test_di_with_simule(self) -> None:
        must_deny(
            {
                "format": "temoin.v0",
                "niveau": "di",
                "simule": True,
                "transcript_sha256": SHA,
                "chsh": 2.4,
            },
            "CHSH_SOFTWARE_AS_DI",
        )

    def test_di_without_transcript_hash(self) -> None:
        must_deny(
            {"format": "temoin.v0", "niveau": "di", "simule": False, "chsh": 2.4},
            "CHSH_SOFTWARE_AS_DI",
        )

    def test_qrng_without_device(self) -> None:
        must_deny(
            {"format": "quelle.v0", "source": "qrng", "appareil": None, "simule": True},
            "PHOTON_INVENTED_AS_QRNG",
        )

    def test_qrng_webcam_label(self) -> None:
        must_deny(
            {
                "format": "quelle.v0",
                "source": "qrng",
                "appareil": "webcam",
                "simule": True,
            },
            "PHOTON_INVENTED_AS_QRNG",
        )

    def test_qkd_software_relabel(self) -> None:
        must_deny(
            {
                "format": "quelle.v0",
                "source": "qkd",
                "appareil": "os.urandom",
                "simule": True,
            },
            "OS_RELABEL_QKD",
        )

    def test_horizon_slogan(self) -> None:
        must_deny(
            {
                "format": "horizon.v0",
                "suite": "quantum-safe",
                "re_presser_avant": "2099-12-31",
            },
            "HORIZON_SLOGAN",
        )

    def test_horizon_past_date(self) -> None:
        must_deny(
            {
                "format": "horizon.v0",
                "suite": "UFHY1",
                "re_presser_avant": "2020-01-01",
            },
            "HORIZON_DATE_INVALID",
        )

    def test_horizon_missing_date(self) -> None:
        must_deny({"format": "horizon.v0", "suite": "ed25519"}, "HORIZON_DATE_INVALID")

    def test_figure_minor(self) -> None:
        must_deny(
            {
                "format": "figure.v0",
                "majeur": False,
                "fin": "2099-12-31",
                "usages": ["nom"],
            },
            "FIGURE_MINOR_OR_NO_END",
        )

    def test_figure_no_end(self) -> None:
        must_deny(
            {"format": "figure.v0", "majeur": True, "usages": ["nom"]},
            "FIGURE_MINOR_OR_NO_END",
        )

    def test_situs_medical(self) -> None:
        must_deny(
            {"format": "situs.v0", "usages": ["medical"], "nom_public": "exemple"},
            "SITUS_MEDICAL_OR_UNLICENSED",
        )

    def test_situs_copy_without_licence(self) -> None:
        must_deny(
            {"format": "situs.v0", "copie": True, "usages": ["capture"]},
            "SITUS_MEDICAL_OR_UNLICENSED",
        )

    def test_token_key(self) -> None:
        must_deny({"format": "recu.v0", "token": "x", "rail": "cash"}, "TOKEN_MINT_COIN")

    def test_unforge_signs(self) -> None:
        must_deny(
            {"format": "unforge.v0", "role": "sign", "file": "x"},
            "UNFORGE_SIGNS",
        )

    def test_raw_transcript_body(self) -> None:
        must_deny(
            {"format": "temoin.v0", "niveau": "aucun", "transcript": "raw-log-not-a-hash"},
            "QUANTUM_IN_GIT",
        )

    def test_estoc_merge(self) -> None:
        must_deny({"format": "estoc.v0", "rail": "estoc"}, "ESTOC_MERGE")

    def test_new_grok_host(self) -> None:
        must_deny(
            {"format": "mode.v0", "mode": "classique", "host": "other.grok.me"},
            "NEW_GROK_HOST",
        )

    def test_second_slug(self) -> None:
        must_deny(
            {
                "format": "mode.v0",
                "mode": "classique",
                "slugs": ["acorn-royal-dune-blend.grok.me", "other.grok.me"],
            },
            "SECOND_SLUG",
        )


class Cli(unittest.TestCase):
    def test_allow_exit_0(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "garde.py"), "deny", "--carte", str(ROOT / "tests" / "fixtures" / "allow-quelle-os.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = json.loads(proc.stdout)
        self.assertEqual(body["decision"], "allow")

    def test_deny_exit_2(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "garde.py"), "deny", "--carte", str(ROOT / "tests" / "fixtures" / "deny-epsilon-zero.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)
        body = json.loads(proc.stdout)
        self.assertEqual(body["decision"], "deny")
        self.assertIn("EPSILON_ZERO", body["codes"])

    def test_stdin_malformed_exit_2(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "garde.py"), "deny", "--stdin"],
            check=False,
            input="{",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("MALFORMED", json.loads(proc.stdout)["codes"])


if __name__ == "__main__":
    unittest.main()
