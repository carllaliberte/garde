# GARDE schemas

- [`deny.v0.json`](deny.v0.json) — verdict of this gate.
- Vocabulary for a quantum claim: [famille/schema/juge.v0.json](https://github.com/carllaliberte/famille/blob/main/schema/juge.v0.json). GARDE does not vendor that file. Rails keep their own `*.v0.json`.

Exit contract (same numbers as the juge):

| exit | meaning |
|---|---|
| 0 | allow — no deny code fired |
| 2 | deny — the FAMILLE label would be broken if this passed |
