# Strong auto-merge barrier

This repository is eligible for future auto-merge only after this barrier is merged and enforced by GitHub branch protection/rulesets.

## Required invariants
- Auto-merge is not authority.
- Critical changes require explicit human review by @carllaliberte.
- Required CI must be green before merge.
- Force pushes and direct default-branch writes must remain disabled.
- Secrets, credentials, external authority, payment rails, deployment authority, and governance must never be introduced by an auto-merged change.
- A green check is evidence of the checks performed; it is not proof of external-world execution.

## Critical paths
- `/src/`
- `/tests/`
- `/.github/workflows/`
- `/.github/swarm/`

## Activation rule
Do not enable repository-wide auto-merge until GitHub branch protection/rulesets require the barrier check and the CODEOWNERS approval for critical paths.
