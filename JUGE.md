# Juge

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

Autres nies : di+simule, os relabel qkd, token, 2e slug, QUANTUM sur Git.

```
python3 garde.py deny --carte carte.json    # exit 0 allow | 2 deny
```

Verdict : [schema/deny.v0.json](schema/deny.v0.json).
Vocabulaire : https://github.com/carllaliberte/famille/blob/main/schema/juge.v0.json
Hôte : https://acorn-royal-dune-blend.grok.me
`peut_dire` vit ailleurs. Judgment = Carl.
