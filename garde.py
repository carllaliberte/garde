#!/usr/bin/env python3
"""GARDE v0 — deny gate for the FAMILLE label.

Defensive. Fail closed. No network. No keys. No QUANTUM.
Other rails call this file. They do not merge this repository.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

FORMAT = "garde.deny.v0"
LIVE_HOST = "acorn-royal-dune-blend.grok.me"
HORIZON_SUITES = frozenset({"ed25519", "UFHY1", "mldsa87"})
QUELLE_SOURCES = frozenset({"os", "qrng", "qkd"})
TEMOIN_NIVEAUX = frozenset({"aucun", "stat", "fabricant", "di"})
CARD_FORMATS = frozenset(
    {
        "quelle.v0",
        "temoin.v0",
        "epsilon.v0",
        "horizon.v0",
        "bruit.v0",
        "mode.v0",
        "figure.v0",
        "dossier.v0",
        "recu.v0",
        "garde.claim.v0",
        "famille.juge.v0",
        "situs.v0",
        "situs-annuaire.v0",
        "ANCRAGE-v0",
        "ancrage.v0",
        "MESURE-v0",
        "mesure.v0",
    }
)
TOKEN_KEYS = frozenset(
    {"token", "mint", "coin", "l1", "quantum_coin", "quantum-coin", "quantumcoin"}
)
TOKEN_VALUES = frozenset(
    {
        "token",
        "mint",
        "coin",
        "l1",
        "quantum coin",
        "quantum-coin",
        "quantumcoin",
        "meta-protocol coin",
        "paiement quantique",
    }
)
MEDICAL_USAGES = frozenset(
    {
        "medical",
        "sante",
        "santé",
        "clinique",
        "hopital",
        "hôpital",
        "patient",
        "diagnostic",
        "prescription",
        "pharma",
        "pharmacie",
    }
)
PREVIEW_LABELS = frozenset({"preview", "aperçu", "apercu", "preview00001"})
RECEIPT_LABELS = frozenset({"quittance", "receipt", "recu", "reçu", "recu.v0"})
SOFTWARE_APPAREIL = (
    "os",
    "urandom",
    "secrets",
    "webcam",
    "camera",
    "micro",
    "microphone",
    "software",
    "logiciel",
    "cpu",
    "prng",
    "simule",
    "simul",
    "ibm",
    "ionq",
    "job",
)
HOST_RE = re.compile(r"\b([a-z0-9-]+(?:\.[a-z0-9-]+)*)\.grok\.me\b", re.I)
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
FORBIDDEN_FILENAMES = frozenset({"quantum.db", "owner.txt", "quantum"})
FORBIDDEN_SUFFIXES = frozenset({".spz", ".ply"})
SCAN_SKIP_DIRS = frozenset(
    {".git", ".github", "__pycache__", ".venv", "venv", "tests", "node_modules"}
)

CODES = (
    "FAIL_CLOSED",
    "MALFORMED",
    "EPSILON_ZERO",
    "EPSILON_MISSING",
    "QUANTUM_WITHOUT_CARDS",
    "LOOPHOLES_CLOSED_INCOMPLETE",
    "CHSH_SOFTWARE_AS_DI",
    "PHOTON_INVENTED_AS_QRNG",
    "OS_RELABEL_QKD",
    "HORIZON_SLOGAN",
    "HORIZON_DATE_INVALID",
    "FIGURE_MINOR_OR_NO_END",
    "SITUS_MEDICAL_OR_UNLICENSED",
    "TOKEN_MINT_COIN",
    "PREVIEW_AS_RECEIPT",
    "UNFORGE_SIGNS",
    "QUANTUM_IN_GIT",
    "ESTOC_MERGE",
    "NEW_GROK_HOST",
    "SECOND_SLUG",
    "FAMILLE_SITE_TOUCHED",
)

REASONS = {
    "FAIL_CLOSED": "unreadable or unrecognized claim — deny",
    "MALFORMED": "not a JSON object",
    "EPSILON_ZERO": "ε = 0 (or none/iid used as a bound) — a finite sample has no zero advantage",
    "EPSILON_MISSING": "juge card missing ε — SDK treats that as classique; acorn-juge Worker returns 400. Fail closed until those two agree",
    "QUANTUM_WITHOUT_CARDS": "quantique without holding QUELLE + TÉMOIN + EPSILON + HORIZON",
    "LOOPHOLES_CLOSED_INCOMPLETE": "trous fermés without detection+locality+freedom closed and simule=false",
    "CHSH_SOFTWARE_AS_DI": "temoin=di with simule, missing transcript hash, or CHSH outside (2, 2√2]",
    "PHOTON_INVENTED_AS_QRNG": "source=qrng without a named device, or webcam/software sold as qrng",
    "OS_RELABEL_QKD": "os (or software) labelled qkd",
    "HORIZON_SLOGAN": "horizon suite is a slogan or vendor job, not ed25519|UFHY1|mldsa87",
    "HORIZON_DATE_INVALID": "horizon date missing, unreadable, a suite name (UFHY1 is not a date), or not strictly after today",
    "FIGURE_MINOR_OR_NO_END": "figure of a minor, or no calendar end date",
    "SITUS_MEDICAL_OR_UNLICENSED": "situs medical usage, or a copy without a licence",
    "TOKEN_MINT_COIN": "mint / coin / token / L1",
    "PREVIEW_AS_RECEIPT": "preview ≠ quittance — a PREVIEW badge or GET /juge 200 is not a receipt",
    "UNFORGE_SIGNS": "unforge that signs — the sas stays private",
    "QUANTUM_IN_GIT": "QUANTUM node or a raw transcript body in the claim",
    "ESTOC_MERGE": "estoc merged into the file",
    "NEW_GROK_HOST": "host other than " + LIVE_HOST,
    "SECOND_SLUG": "second published slug",
    "FAMILLE_SITE_TOUCHED": "famille/site/ is not this rail",
}


def _today(today: date | None) -> date:
    return today or datetime.now(timezone.utc).date()


def _as_dict(obj: Any) -> dict[str, Any] | None:
    return obj if isinstance(obj, dict) else None


def _unwrap(obj: dict[str, Any]) -> dict[str, Any]:
    envelope_keys = (
        "rail",
        "assert",
        "mode",
        "host",
        "slug",
        "slugs",
        "preview",
        "quittance",
        "receipt",
        "badge",
        "status",
    )
    if obj.get("format") == "garde.claim.v0" and isinstance(obj.get("card"), dict):
        inner = dict(obj["card"])
        for key in envelope_keys:
            if key in obj and key not in inner:
                inner[key] = obj[key]
        return inner
    # famille.flux.v0 — typed flux envelope; deny rules apply to nested carte
    if obj.get("format") in {"famille.flux.v0", "flux.v0"} and isinstance(obj.get("carte"), dict):
        inner = dict(obj["carte"])
        for key in envelope_keys:
            if key in obj and key not in inner:
                inner[key] = obj[key]
        inner.setdefault("format", "flux.v0")
        return inner
    return obj


def _rail_of(obj: dict[str, Any]) -> str | None:
    fmt = obj.get("format")
    if fmt in {"ANCRAGE-v0", "ancrage.v0"}:
        return "ancrage"
    if fmt in {"MESURE-v0", "mesure.v0"}:
        return "mesure"
    if fmt in {"famille.flux.v0", "flux.v0"}:
        return "flux"
    if isinstance(fmt, str) and fmt.endswith(".v0"):
        return fmt.split(".", 1)[0]
    if isinstance(obj.get("quelle"), str) and "temoin" in obj:
        return "juge"
    if all(k in obj for k in ("quelle", "temoin", "epsilon", "horizon")):
        return "juge"
    return obj.get("rail") if isinstance(obj.get("rail"), str) else None


def _claims_quantum(obj: dict[str, Any]) -> bool:
    mode = obj.get("mode") or obj.get("assert") or obj.get("verdict")
    if isinstance(mode, str) and mode.strip().lower() in {"quantique", "quantum"}:
        return True
    return obj.get("quantique") is True


def _lower(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _parse_day(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.match(value))


def _softwareish(value: Any) -> bool:
    text = _lower(value)
    return bool(text) and any(word in text for word in SOFTWARE_APPAREIL)


def _hosts_in(text: str) -> set[str]:
    return {m.group(0).lower() for m in HOST_RE.finditer(text)}


def _walk_strings(obj: Any) -> Iterable[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, str):
                yield key
            yield from _walk_strings(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_strings(item)


def _add(hits: list[str], code: str) -> None:
    if code not in hits:
        hits.append(code)


def _is_preview_claim(obj: dict[str, Any]) -> bool:
    if obj.get("preview") is True:
        return True
    for key in ("badge", "status", "kind", "type", "role"):
        if _lower(obj.get(key)) in PREVIEW_LABELS:
            return True
    fmt = _lower(obj.get("format"))
    return fmt.startswith("preview") or fmt.startswith("attest.preview")


def _is_receipt_claim(obj: dict[str, Any]) -> bool:
    if obj.get("quittance") is True or obj.get("receipt") is True:
        return True
    fmt = _lower(obj.get("format"))
    if fmt == "recu.v0" or fmt.startswith("recu"):
        return True
    if _lower(obj.get("rail")) == "recu":
        return True
    for key in ("assert", "kind", "type", "role"):
        if _lower(obj.get(key)) in RECEIPT_LABELS:
            return True
    return False


def _check_preview_as_receipt(obj: dict[str, Any], hits: list[str]) -> None:
    # Preview canal / badge presented as a receipt. Not an exploit recipe.
    if _is_preview_claim(obj) and _is_receipt_claim(obj):
        _add(hits, "PREVIEW_AS_RECEIPT")


def _check_token(obj: dict[str, Any], hits: list[str]) -> None:
    for key in obj:
        if _lower(key) in TOKEN_KEYS:
            _add(hits, "TOKEN_MINT_COIN")
            return
    for key in ("rail", "assert", "kind", "type", "asset", "suite"):
        if _lower(obj.get(key)) in TOKEN_VALUES:
            _add(hits, "TOKEN_MINT_COIN")
            return


def _check_estoc(obj: dict[str, Any], hits: list[str]) -> None:
    fmt = _lower(obj.get("format"))
    rail = _lower(obj.get("rail"))
    if "estoc" in fmt or rail in {"estoc", "estoc-proto"} or obj.get("estoc") is True:
        _add(hits, "ESTOC_MERGE")


def _check_hosts(obj: dict[str, Any], hits: list[str]) -> None:
    found: set[str] = set()
    for text in _walk_strings(obj):
        found |= _hosts_in(text)
    extra = {h for h in found if h != LIVE_HOST}
    if extra:
        _add(hits, "NEW_GROK_HOST")
    slugs = obj.get("slugs")
    if isinstance(slugs, list) and len(slugs) > 1:
        _add(hits, "SECOND_SLUG")
    slug = obj.get("slug")
    if isinstance(slug, str) and slug and slug.lower() not in {LIVE_HOST, "garde", "famille"}:
        if slug.lower().endswith(".grok.me") and slug.lower() != LIVE_HOST:
            _add(hits, "SECOND_SLUG")


def _check_quantum_body(obj: dict[str, Any], hits: list[str]) -> None:
    if obj.get("quantum_db") or _lower(obj.get("node")) == "quantum":
        _add(hits, "QUANTUM_IN_GIT")
    transcript = obj.get("transcript")
    if transcript in (None, "", {}):
        return
    if isinstance(transcript, str) and (_is_sha256(transcript) or transcript in TEMOIN_NIVEAUX):
        return
    if isinstance(transcript, dict) and _is_sha256(transcript.get("transcript_sha256")):
        return
    _add(hits, "QUANTUM_IN_GIT")


def _check_unforge_signs(obj: dict[str, Any], hits: list[str]) -> None:
    fmt = _lower(obj.get("format"))
    rail = _lower(obj.get("rail") or _rail_of(obj))
    if not (fmt.startswith("unforge") or rail.startswith("unforge")):
        return
    if obj.get("signe") is True or obj.get("signed") is True:
        _add(hits, "UNFORGE_SIGNS")
    if _lower(obj.get("role")) in {"sign", "signer", "seal", "sceau"}:
        _add(hits, "UNFORGE_SIGNS")
    if _lower(obj.get("signer")) == "unforge":
        _add(hits, "UNFORGE_SIGNS")
    for key in ("private_key", "sk", "signing_key"):
        if obj.get(key):
            _add(hits, "UNFORGE_SIGNS")
            return


def _epsilon_value(obj: dict[str, Any]) -> Any:
    if "epsilon" in obj:
        return obj.get("epsilon")
    return None


def _flat_juge(obj: dict[str, Any]) -> bool:
    """True for the public juge vocabulary (quelle as os|qrng|qkd), not a rail card."""
    fmt = obj.get("format")
    if fmt in CARD_FORMATS and fmt not in {"famille.juge.v0", "garde.claim.v0"}:
        return False
    return isinstance(obj.get("quelle"), str) and _lower(obj.get("quelle")) in QUELLE_SOURCES


def _check_epsilon(obj: dict[str, Any], hits: list[str], *, quantum: bool) -> None:
    eps = _epsilon_value(obj)
    modele = _lower(obj.get("modele"))
    if eps == 0 or eps == 0.0 or eps == "0":
        _add(hits, "EPSILON_ZERO")
        return
    if _lower(eps) in {"none", "iid"}:
        _add(hits, "EPSILON_ZERO")
        return
    if quantum and modele in {"none", "iid"}:
        _add(hits, "EPSILON_ZERO")
    if quantum and modele != "none":
        if not isinstance(eps, (int, float)) or isinstance(eps, bool) or eps <= 0 or eps > 1:
            _add(hits, "EPSILON_ZERO")
    # famille SDK (d55799e): missing ε → classique / manques.
    # acorn-juge Worker: missing ε → HTTP 400, same phrase as ε=0.
    # GARDE does not unwind the SDK. It fails closed on the split.
    if _flat_juge(obj) and (eps is None or eps == ""):
        _add(hits, "EPSILON_MISSING")


def _check_quelle(obj: dict[str, Any], hits: list[str]) -> None:
    source = obj.get("source") if "source" in obj else obj.get("quelle")
    if isinstance(source, dict):
        return _check_quelle(source, hits)
    source_l = _lower(source)
    if source in (None, ""):
        return
    if source_l not in QUELLE_SOURCES:
        _add(hits, "FAIL_CLOSED")
        return
    appareil = obj.get("appareil")
    note = obj.get("note")
    if source_l == "qrng":
        if not appareil:
            _add(hits, "PHOTON_INVENTED_AS_QRNG")
        elif _softwareish(appareil) or _softwareish(note):
            _add(hits, "PHOTON_INVENTED_AS_QRNG")
    if source_l == "qkd":
        if not appareil or obj.get("simule") is True or _softwareish(appareil):
            _add(hits, "OS_RELABEL_QKD")


def _check_temoin(obj: dict[str, Any], hits: list[str]) -> None:
    niveau = obj.get("niveau") if "niveau" in obj else obj.get("temoin")
    if isinstance(niveau, dict):
        return _check_temoin(niveau, hits)
    niveau_l = _lower(niveau)
    if niveau in (None, ""):
        return
    if niveau_l not in TEMOIN_NIVEAUX:
        _add(hits, "FAIL_CLOSED")
        return
    if niveau_l != "di":
        return
    if obj.get("simule") is True:
        _add(hits, "CHSH_SOFTWARE_AS_DI")
    digest = obj.get("transcript_sha256")
    nested = obj.get("transcript")
    if isinstance(nested, dict):
        digest = digest or nested.get("transcript_sha256")
        chsh = nested.get("chsh", obj.get("chsh"))
    else:
        chsh = obj.get("chsh")
    if not _is_sha256(digest):
        _add(hits, "CHSH_SOFTWARE_AS_DI")
    if chsh is not None:
        try:
            value = float(chsh)
        except (TypeError, ValueError):
            _add(hits, "CHSH_SOFTWARE_AS_DI")
            return
        if value <= 2 or value > (2 * (2**0.5)) + 1e-9:
            _add(hits, "CHSH_SOFTWARE_AS_DI")


def _check_horizon(obj: dict[str, Any], hits: list[str], today: date, *, required: bool) -> None:
    raw = obj.get("re_presser_avant")
    if raw is None:
        raw = obj.get("horizon") if isinstance(obj.get("horizon"), str) else None
    nested = obj.get("horizon")
    suite = obj.get("suite")
    if isinstance(nested, dict):
        raw = raw or nested.get("re_presser_avant") or nested.get("horizon")
        suite = suite or nested.get("suite")
    if suite is not None and suite not in HORIZON_SUITES:
        _add(hits, "HORIZON_SLOGAN")
    job = _lower(obj.get("job") or obj.get("ibm_job") or obj.get("horizon_suite"))
    if job and job not in {s.lower() for s in HORIZON_SUITES}:
        if "ibm" in job or "ionq" in job or "quantum-safe" in job or job == "quantum-safe":
            _add(hits, "HORIZON_SLOGAN")
    if required or raw is not None or obj.get("format") == "horizon.v0":
        day = _parse_day(raw)
        if day is None or day <= today:
            _add(hits, "HORIZON_DATE_INVALID")


def _check_bruit(obj: dict[str, Any], hits: list[str]) -> None:
    body = obj.get("bruit") if isinstance(obj.get("bruit"), dict) else obj
    if body.get("trous") != "fermes":
        return
    closed = all(body.get(k) == "fermee" for k in ("detection", "localite", "liberte"))
    if not closed or body.get("simule") is True:
        _add(hits, "LOOPHOLES_CLOSED_INCOMPLETE")


def _check_figure(obj: dict[str, Any], hits: list[str], today: date) -> None:
    if obj.get("format") != "figure.v0" and "figure_id" not in obj and "majeur" not in obj:
        return
    if obj.get("majeur") is not True:
        _add(hits, "FIGURE_MINOR_OR_NO_END")
    day = _parse_day(obj.get("fin"))
    if day is None or day <= today:
        _add(hits, "FIGURE_MINOR_OR_NO_END")


def _is_ancrage_card(obj: dict[str, Any]) -> bool:
    fmt = obj.get("format")
    return fmt in {"ANCRAGE-v0", "ancrage.v0"} or _lower(obj.get("rail")) == "ancrage"


def _is_mesure_card(obj: dict[str, Any]) -> bool:
    fmt = obj.get("format")
    return fmt in {"MESURE-v0", "mesure.v0"} or _lower(obj.get("rail")) == "mesure"


def _check_ancrage(obj: dict[str, Any], hits: list[str], today: date) -> None:
    """ANCRAGE is a re-measure date. Physique ≠ crypto. UFHY1 is not a date."""
    if not _is_ancrage_card(obj):
        return
    avant = obj.get("avant")
    if isinstance(avant, str) and avant.strip() in HORIZON_SUITES:
        _add(hits, "HORIZON_DATE_INVALID")
        return
    day = _parse_day(avant)
    if day is None or day <= today:
        _add(hits, "HORIZON_DATE_INVALID")


def _check_flux_envelope(obj: dict[str, Any], hits: list[str]) -> None:
    """famille.flux.v0 is preview-only. Nested ancrage dates are calendars, not suites."""
    if obj.get("format") not in {"famille.flux.v0", "flux.v0"}:
        return
    # Schema: preview true, receipt false. A receipt bit on flux is a lie.
    if obj.get("receipt") is True or obj.get("quittance") is True:
        _add(hits, "PREVIEW_AS_RECEIPT")
    sats = obj.get("satellites")
    if not isinstance(sats, dict):
        return
    ancrage = sats.get("ancrage")
    if isinstance(ancrage, dict):
        avant = ancrage.get("re_mesurer_avant")
        if isinstance(avant, str) and avant.strip() in HORIZON_SUITES:
            _add(hits, "HORIZON_DATE_INVALID")
        elif avant is not None and _parse_day(avant) is None:
            _add(hits, "HORIZON_DATE_INVALID")
    mesure = sats.get("mesure")
    if isinstance(mesure, dict) and (
        mesure.get("fork") is True or mesure.get("forker") is True
    ):
        # Flux v1: consulter destroys here / born there — no fork.
        _add(hits, "FAIL_CLOSED")


def _check_mesure(obj: dict[str, Any], hits: list[str]) -> None:
    """MESURE counts readings. It does not invent a qubit or a coin."""
    if not _is_mesure_card(obj):
        return
    if not _is_sha256(obj.get("sha256")):
        _add(hits, "FAIL_CLOSED")
    lectures = obj.get("lectures")
    if not isinstance(lectures, int) or lectures < 0:
        _add(hits, "FAIL_CLOSED")
    niveau = _lower(obj.get("temoin") or obj.get("niveau") or obj.get("di"))
    if niveau == "di" or obj.get("chsh") is not None or obj.get("photon") is True:
        _add(hits, "PHOTON_INVENTED_AS_QRNG")
    if _lower(obj.get("assert")) in {"monnaie", "coin", "token"} or obj.get("monnaie") is True:
        _add(hits, "TOKEN_MINT_COIN")


def _usages_of(obj: dict[str, Any]) -> list[str]:
    raw = obj.get("usages") or obj.get("usage")
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return []


def _check_situs(obj: dict[str, Any], hits: list[str]) -> None:
    fmt = _lower(obj.get("format"))
    rail = _lower(obj.get("rail") or "")
    looks = fmt.startswith("situs") or rail == "situs" or "situs_id" in obj
    if not looks:
        return
    usages = {_lower(u) for u in _usages_of(obj)}
    if usages & MEDICAL_USAGES:
        _add(hits, "SITUS_MEDICAL_OR_UNLICENSED")
    copie = obj.get("copie") is True or obj.get("scan") is True
    licence = obj.get("licence") or obj.get("license") or obj.get("owner")
    if copie and not licence:
        _add(hits, "SITUS_MEDICAL_OR_UNLICENSED")


def _nested_card(obj: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = obj.get(key)
    return value if isinstance(value, dict) else None


def _has_four_cards(obj: dict[str, Any]) -> bool:
    keys = ("quelle", "temoin", "epsilon", "horizon")
    if all(obj.get(k) not in (None, "") for k in keys):
        return True
    ids = ("quelle_id", "temoin_id", "epsilon_id", "horizon_id")
    return all(obj.get(k) not in (None, "") for k in ids)


def _check_quantum_claim(obj: dict[str, Any], hits: list[str], today: date) -> None:
    if not _claims_quantum(obj):
        return
    if not _has_four_cards(obj):
        _add(hits, "QUANTUM_WITHOUT_CARDS")
    quelle = _nested_card(obj, "quelle")
    temoin = _nested_card(obj, "temoin")
    epsilon = _nested_card(obj, "epsilon")
    horizon = _nested_card(obj, "horizon")
    if quelle:
        _check_quelle(quelle, hits)
    elif _lower(obj.get("quelle")) == "os":
        _add(hits, "QUANTUM_WITHOUT_CARDS")
    if temoin:
        _check_temoin(temoin, hits)
    elif _lower(obj.get("temoin")) in {"aucun", "stat"}:
        _add(hits, "QUANTUM_WITHOUT_CARDS")
    if epsilon:
        _check_epsilon(epsilon, hits, quantum=True)
    else:
        _check_epsilon(obj, hits, quantum=True)
    if horizon:
        _check_horizon(horizon, hits, today, required=True)
    else:
        _check_horizon(obj, hits, today, required=True)
    bruit = _nested_card(obj, "bruit")
    if bruit:
        _check_bruit(bruit, hits)


def _recognized(obj: dict[str, Any]) -> bool:
    fmt = obj.get("format")
    if fmt in CARD_FORMATS or (isinstance(fmt, str) and fmt.startswith("situs")):
        return True
    if all(k in obj for k in ("quelle", "temoin", "epsilon", "horizon")):
        return True
    if isinstance(fmt, str) and fmt.endswith(".v0"):
        return True
    return False


def deny(obj: Any, *, today: date | None = None) -> dict[str, Any]:
    """Return a garde.deny.v0 verdict. Fail closed on unknown or unreadable input."""
    today = _today(today)
    if not isinstance(obj, dict):
        return _verdict(["MALFORMED"], rail=None)
    card = _unwrap(obj)
    hits: list[str] = []
    _check_token(card, hits)
    _check_preview_as_receipt(card, hits)
    _check_estoc(card, hits)
    _check_hosts(card, hits)
    _check_quantum_body(card, hits)
    _check_unforge_signs(card, hits)
    _check_quelle(card, hits)
    _check_temoin(card, hits)
    _check_epsilon(card, hits, quantum=_claims_quantum(card))
    _check_horizon(
        card,
        hits,
        today,
        required=card.get("format") == "horizon.v0" or _claims_quantum(card),
    )
    _check_bruit(card, hits)
    _check_figure(card, hits, today)
    _check_situs(card, hits)
    _check_flux_envelope(obj, hits)
    _check_ancrage(card, hits, today)
    _check_mesure(card, hits)
    _check_quantum_claim(card, hits, today)
    if not _recognized(card) and not hits:
        _add(hits, "FAIL_CLOSED")
    return _verdict(hits, rail=_rail_of(card))


def _verdict(codes: list[str], rail: str | None) -> dict[str, Any]:
    fail_closed = any(c in {"FAIL_CLOSED", "MALFORMED", "EPSILON_MISSING"} for c in codes)
    decision = "deny" if codes else "allow"
    return {
        "format": FORMAT,
        "decision": decision,
        "codes": codes,
        "reasons": [REASONS[c] for c in codes],
        "fail_closed": fail_closed,
        "rail": rail,
        "note": (
            "deny — if this passed, the FAMILLE label is broken"
            if codes
            else "allow — no deny code fired; classique remains the default"
        ),
    }


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def deny_path(path: Path, *, today: date | None = None) -> dict[str, Any]:
    obj = load_json(path)
    if obj is None:
        return _verdict(["MALFORMED"], rail=None)
    return deny(obj, today=today)


def _forbidden_path(rel: Path) -> str | None:
    parts = [p.lower() for p in rel.parts]
    if "famille" in parts and "site" in parts:
        return "FAMILLE_SITE_TOUCHED"
    name = rel.name.lower()
    if name in FORBIDDEN_FILENAMES or rel.stem.lower() == "quantum":
        return "QUANTUM_IN_GIT"
    if rel.suffix.lower() in FORBIDDEN_SUFFIXES:
        return "QUANTUM_IN_GIT"
    if name.startswith("estoc"):
        return "ESTOC_MERGE"
    return None


def scan(root: Path, *, today: date | None = None) -> dict[str, Any]:
    """Artifact scan. Does not evaluate test fixtures. Fail closed on a broken tree."""
    root = root.resolve()
    if not root.is_dir():
        return _verdict(["FAIL_CLOSED"], rail="scan")
    hits: list[str] = []
    findings: list[dict[str, str]] = []

    def note(code: str, path: str) -> None:
        _add(hits, code)
        findings.append({"code": code, "path": path})

    for path in sorted(root.rglob("*")):
        if any(part in SCAN_SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        code = _forbidden_path(rel)
        if code:
            note(code, str(rel))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        extra = {h for h in _hosts_in(text) if h != LIVE_HOST}
        if extra:
            note("NEW_GROK_HOST", str(rel))

    verdict = _verdict(hits, rail="scan")
    verdict["findings"] = findings
    verdict["root"] = str(root)
    return verdict


def _print(verdict: dict[str, Any]) -> int:
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0 if verdict.get("decision") == "allow" else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="garde",
        description="FAMILLE deny gate. Exit 0 allow, 2 deny. Fail closed.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_deny = sub.add_parser("deny", help="evaluate one JSON claim")
    src = p_deny.add_mutually_exclusive_group(required=True)
    src.add_argument("--carte", help="path to a card or claim")
    src.add_argument("--stdin", action="store_true", help="read JSON from stdin")

    p_scan = sub.add_parser("scan", help="scan a repo for forbidden artifacts")
    p_scan.add_argument("--root", default=".")

    sub.add_parser("codes", help="print the deny catalog")

    args = parser.parse_args(argv)
    if args.cmd == "codes":
        catalog = [
            {"code": code, "reason": REASONS[code]}
            for code in CODES
        ]
        print(json.dumps({"format": "garde.codes.v0", "codes": catalog}, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "scan":
        return _print(scan(Path(args.root)))
    if args.stdin:
        try:
            obj = json.load(sys.stdin)
        except json.JSONDecodeError:
            return _print(_verdict(["MALFORMED"], rail=None))
        return _print(deny(obj))
    return _print(deny_path(Path(args.carte)))


if __name__ == "__main__":
    sys.exit(main())
