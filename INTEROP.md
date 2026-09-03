# Interop — call GARDE. Do not merge the repos.

FAMILLE is a cadastre. GARDE is the deny gate. Protocol v0s are rails.
Each stays in its own Git repository.

```
famille                 vocabulary          schema/juge.v0.json
quelle, temoin, …       emit a card         *.v0.json in that repo
GARDE                   deny / fail closed  this repo
unforge (private)       may sign            never here
QUANTUM                 local node          never in Git
```

Carl merges. The bot denies. A green gate is not a merge.

## What other repos send

A rail sends **JSON it already has**. GARDE does not import the rail package
and does not copy its schema.

Accepted shapes:

1. A protocol card (`format: quelle.v0`, `temoin.v0`, …).
2. A juge vocabulary object (`quelle`, `temoin`, `epsilon`, `horizon`) —
   the public contract in [famille/schema/juge.v0.json](https://github.com/carllaliberte/famille/blob/main/schema/juge.v0.json).
3. An envelope, if the rail wants a named rail without flattening:

```json
{
  "format": "garde.claim.v0",
  "rail": "quelle",
  "card": { "format": "quelle.v0", "source": "os" }
}
```

Unknown JSON fails closed (`FAIL_CLOSED` / `MALFORMED`). That is the point.

## How to call without merging

Pin a commit SHA of `carllaliberte/garde`. Do not submodule the lattice
into one tree. Do not vendor `famille/site/`.

### GitHub Action (preferred)

```yaml
# in quelle, temoin-protocol, … — not in famille/site
- uses: carllaliberte/garde@<sha>
  with:
    carte: examples/os-32.quelle.json
    root: .
```

`carte` is optional. Without it, only the artifact scan runs.

### Checkout + CLI

```yaml
- uses: actions/checkout@v4
  with:
    repository: carllaliberte/garde
    ref: <sha>
    path: .garde
    persist-credentials: false
- run: python3 .garde/garde.py deny --carte examples/os-32.quelle.json
- run: python3 .garde/garde.py scan --root .
```

### One-file library

Copy `garde.py` (stdlib only) into a rail's `vendor/` if CI cannot
checkout. Do not copy Git history. Do not rename the deny codes.

```python
from garde import deny
verdict = deny(card)          # dict → garde.deny.v0
# exit 0 allow, exit 2 deny
```

## What GARDE does not do

| Actor | Role |
|---|---|
| GARDE | deny forbidden claims; scan forbidden artifacts |
| MODE / `peut_dire` | collapse to classique / quantique (elsewhere) |
| UNFORGE Check | verify a file against a card — it does not sign |
| QUANTUM | seal — local, off Git, off grok.me |
| FAMILLE host | display. One live host: `acorn-royal-dune-blend.grok.me` |

A rail that wants a quantum label still needs the four cards to *hold*.
GARDE only answers: would letting this claim through break FAMILLE?

## Artifact scan (repo hygiene)

`python3 garde.py scan --root .` looks at filenames and extra `*.grok.me`
hosts. It skips `tests/` so deny fixtures can exist. It does not grep
policy prose for the words “token” or “estoc”.

Forbidden artifacts: `quantum.db`, a file named `QUANTUM`, `owner.txt`,
`*.spz` / `*.ply`, `famille/site/`, `estoc*`, any host other than the
live acorn host.

## ε — two consumers, one lie, one split

Do not unwind [famille@d55799e](https://github.com/carllaliberte/famille/commit/d55799e).
That commit is the typed map: missing field → `classique`. GARDE does not
edit famille.

Verified (read-only, 2026-09-03):

| Consumer | missing `epsilon` | `epsilon: 0` |
|---|---|---|
| famille `sdk/peut-dire.js` `lireEpsilon` | `kind: 'manque'` → MODE **classique** | `kind: 'lie'` |
| [acorn-juge](https://github.com/carllaliberte/acorn-juge) `GET /juge` | HTTP **400** `error: lie` | HTTP **400** `error: lie` |

ε = 0 is a lie on both paths. GARDE always denies it (`EPSILON_ZERO`).

Missing ε is **not aligned**. Until the SDK and the Worker share one rule,
a **juge vocabulary** card (flat `quelle` ∈ os\|qrng\|qkd) with `epsilon`
absent, null, or `""` is `EPSILON_MISSING` — fail closed. That is deny-or-align,
not an exploit recipe. (`""` is a manque in the SDK and a 400 on the Worker;
GARDE does not collapse it into `EPSILON_ZERO`.)

The epsilon **rail** (`format: epsilon.v0`, `modele: none`, `epsilon: null`)
stays allowed. That is the honest default of that protocol, not the juge
card the two consumers disagree on.

## Exit contract

Same numbers as the juge, opposite question:

| exit | GARDE | `peut_dire` (unforge) |
|---|---|---|
| 0 | no deny code — gate green | the four cards hold |
| 2 | deny / fail closed | classique |

Do not treat exit 0 as “this is quantum”.
