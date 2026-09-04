# GARDE

Les certitudes ont une date de fin. Certainties expire.

VERT = match · AMBRE = match; a date is due again · ROUGE = refuse.
Preview ≠ receipt. Cursor calls the juge — is not the juge.

**Attacks that must deny.** If one passes, the FAMILLE label is broken.

GARDE is the public deny gate of the lattice. It is not a bot named FAMILLE,
not a judge that says “quantique”, and not a place to publish QUANTUM.
Carl merges. The bot denies.

```
claim JSON  →  garde.deny  →  {decision, codes, reasons}
                               exit 0 allow | 2 deny
```

Unknown, unreadable, or incomplete privileged input **fails closed** (`deny`).
Tests in this repository only check that forbidden claims are refused.
They do not implement exploits, payloads, or attack procedures.

## Deny criteria

| Code | Must deny |
|---|---|
| `EPSILON_ZERO` | ε = 0; `none` / `iid` used as a bound — a lie on either consumer |
| `EPSILON_MISSING` | juge card with no ε — SDK → classique; acorn-juge Worker → 400. Fail closed |
| `QUANTUM_WITHOUT_CARDS` | `quantique` without QUELLE + TÉMOIN + EPSILON + HORIZON holding |
| `LOOPHOLES_CLOSED_INCOMPLETE` | `trous: fermes` without the three closed **and** `simule: false` |
| `CHSH_SOFTWARE_AS_DI` | `temoin: di` with `simule`, no transcript hash, or CHSH outside (2, 2√2] |
| `PHOTON_INVENTED_AS_QRNG` | `source: qrng` without a named device, or webcam/software as qrng |
| `OS_RELABEL_QKD` | software / `os` labelled `qkd` |
| `HORIZON_SLOGAN` | “quantum-safe” / vendor job instead of `ed25519` \| `UFHY1` \| `mldsa87` |
| `HORIZON_DATE_INVALID` | horizon date missing, unreadable, a suite name (`UFHY1` is not a date), or not strictly after today |
| `FIGURE_MINOR_OR_NO_END` | figure of a minor, or no calendar end |
| `SITUS_MEDICAL_OR_UNLICENSED` | medical situs usage, or a copy without a licence |
| `TOKEN_MINT_COIN` | mint / coin / token / L1 |
| `PREVIEW_AS_RECEIPT` | preview = quittance — a PREVIEW badge or GET `/juge` 200 is not a receipt |
| `UNFORGE_SIGNS` | Unforge that signs (the sas stays private) |
| `QUANTUM_IN_GIT` | QUANTUM node or a raw transcript body |
| `ESTOC_MERGE` | Estoc merged into the file |
| `NEW_GROK_HOST` | any `*.grok.me` other than the live acorn host |
| `SECOND_SLUG` | a second published slug |
| `FAMILLE_SITE_TOUCHED` | `famille/site/` (scan) |
| `FAIL_CLOSED` / `MALFORMED` | unrecognized or unreadable claim |

Physics enters as **source and bound**. ε is a statistical margin on a finite
sample. It is never zero. `os` is an honest default. It is not a photon.

Live host (only): `https://acorn-royal-dune-blend.grok.me` — kit page `#/garde`.

## Run

stdlib Python. No keys. No network.

```bash
python3 garde.py deny --carte examples/classique.juge.json   # exit 0
python3 garde.py deny --carte examples/deny-epsilon-zero.json  # exit 2
python3 garde.py scan --root .
python3 garde.py codes
python3 -m unittest discover -s tests -v
```

Red fixtures (each must deny): `examples/deny-epsilon-zero.json`,
`examples/deny-photon-invente.json`, `examples/deny-preview-quittance.json`,
`examples/deny-quantique-sans-bornes.json`, `examples/deny-ufhy1-as-date.json`.
See [JUGE.md](JUGE.md).

Other protocol repos call this gate **without merging Git history**. See
[INTEROP.md](INTEROP.md). Pin a SHA:

```yaml
- uses: carllaliberte/garde@<sha>
  with:
    carte: examples/os-32.quelle.json
```

## This repo

| File | Role |
|---|---|
| [`garde.py`](garde.py) | deny + scan + CLI |
| [`schema/deny.v0.json`](schema/deny.v0.json) | verdict contract |
| [`INTEROP.md`](INTEROP.md) | famille + protocol v0s plug in here |
| [`MERGE.md`](MERGE.md) | squash, one branch, no auto-merge |
| [`JUGE.md`](JUGE.md) | GARDE denies; it is not the juge |
| [`BOTS.md`](BOTS.md) | no bot is owner; no bot merges |
| [`LICENSE`](LICENSE) | MIT — this repo, not QUANTUM |
| [`COPYRIGHT.md`](COPYRIGHT.md) | © 2026 Carl Laliberté, Québec |
| [famille/GARDE.md](https://github.com/carllaliberte/famille/blob/main/GARDE.md) | page on the live host |
| [famille/INTERDIT.md](https://github.com/carllaliberte/famille/blob/main/INTERDIT.md) | cadastre interdits |

FAMILLE is not a rail. Do not open a FAMILLE bot. Do not add a second grok.me.
Do not put QUANTUM or a real transcript in Git.

## License

MIT. See [LICENSE](LICENSE) and [COPYRIGHT.md](COPYRIGHT.md).

This repository licenses the public deny gate. It does not license QUANTUM.
Tests check that forbidden claims are refused. They do not formally verify
the lattice.
