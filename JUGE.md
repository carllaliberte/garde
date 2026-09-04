# Juge

Les certitudes ont une date de fin. Certainties expire.
GARDE denies; it is not the juge. Cursor calls `peut-dire` / this gate.

GARDE n'est pas le juge. Il lit INTERDIT.md. Ici on nie.
Si une attaque passe, le label FAMILLE est cassé.

## Attaques qui doivent deny

1. **ε=0** — `EPSILON_ZERO`. Marge nulle = mensonge partout.
   ε absent sur une carte juge : SDK=classique, Worker acorn=400.
   GARDE nie (`EPSILON_MISSING`) jusqu'à alignement. Ne pas défaire famille d55799e.
   Fixture : [examples/deny-epsilon-zero.json](examples/deny-epsilon-zero.json)
2. **photon inventé** — `PHOTON_INVENTED_AS_QRNG`.
   `source=qrng` sans appareil, ou webcam / logiciel vendu comme photon.
   Fixture : [examples/deny-photon-invente.json](examples/deny-photon-invente.json)
3. **preview = quittance** — `PREVIEW_AS_RECEIPT`.
   Preview ≠ receipt. Un badge PREVIEW ou un GET `/juge` 200 n'est pas une quittance UNFORGE.
   Fixture : [examples/deny-preview-quittance.json](examples/deny-preview-quittance.json)
4. **quantique sans bornes** — `QUANTUM_WITHOUT_CARDS`.
   `quantique` sans QUELLE + TÉMOIN + EPSILON + HORIZON qui tiennent.
   Fixture : [examples/deny-quantique-sans-bornes.json](examples/deny-quantique-sans-bornes.json)
5. **UFHY1 comme date de calendrier** — `HORIZON_DATE_INVALID`.
   UFHY1 est une suite (Ed25519 + ML-DSA-65), jamais un jour `YYYY-MM-DD`.
   Fixture : [examples/deny-ufhy1-as-date.json](examples/deny-ufhy1-as-date.json)

6. **flux ε=0 imbriqué** — `EPSILON_ZERO`.
   `famille.flux.v0` unwrap `carte`. ε=0 nested is still a lie.
   Fixture : [examples/deny-flux-epsilon-zero.json](examples/deny-flux-epsilon-zero.json)
7. **flux receipt** — `PREVIEW_AS_RECEIPT`. Flux is preview-only.
   Fixture : [examples/deny-flux-receipt.json](examples/deny-flux-receipt.json)
8. **flux ancrage UFHY1** — `HORIZON_DATE_INVALID`. Suite ≠ calendar date.
   Fixture : [examples/deny-flux-ancrage-ufhy1.json](examples/deny-flux-ancrage-ufhy1.json)

Autres nies : di+simule, os relabel qkd, token, 2e slug, QUANTUM sur Git.

```
python3 garde.py deny --carte carte.json    # exit 0 allow | 2 deny
```

Verdict : [schema/deny.v0.json](schema/deny.v0.json).
Vocabulaire : https://github.com/carllaliberte/famille/blob/main/schema/juge.v0.json
Hôte : https://acorn-royal-dune-blend.grok.me
`peut_dire` vit ailleurs. Judgment = Carl.
