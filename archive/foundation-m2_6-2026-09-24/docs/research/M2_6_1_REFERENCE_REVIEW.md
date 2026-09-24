# M2.6.0–1: source-backed architecture review

Date: 2026-09-22. Scope: runtime composition and baseline preservation only.
These are source inspections, not claims that the full upstream suites were run.
No upstream implementation code is copied or added as a dependency.

## Pinned evidence

- Kerykeion commit `f7608a1dee404afc16a440e4bf565eeeec46bcbd`:
  [backend.py](https://github.com/g-battaglia/kerykeion/blob/f7608a1dee404afc16a440e4bf565eeeec46bcbd/kerykeion/ephemeris_backend/backend.py),
  [factory.py](https://github.com/g-battaglia/kerykeion/blob/f7608a1dee404afc16a440e4bf565eeeec46bcbd/kerykeion/astrological_subject/factory.py),
  [path tests](https://github.com/g-battaglia/kerykeion/blob/f7608a1dee404afc16a440e4bf565eeeec46bcbd/tests/core/test_ephemeris_backend_path.py).
- Immanuel commit `eba98099b7724598064113ffa1322e78dc4bccf6`:
  [charts.py](https://github.com/theriftlab/immanuel-python/blob/eba98099b7724598064113ffa1322e78dc4bccf6/immanuel/charts.py),
  [settings.py](https://github.com/theriftlab/immanuel-python/blob/eba98099b7724598064113ffa1322e78dc4bccf6/immanuel/settings.py),
  [ephemeris.py](https://github.com/theriftlab/immanuel-python/blob/eba98099b7724598064113ffa1322e78dc4bccf6/immanuel/tools/ephemeris.py),
  [settings tests](https://github.com/theriftlab/immanuel-python/blob/eba98099b7724598064113ffa1322e78dc4bccf6/tests/test_settings.py).

## Findings and bounded adoption

| Observed implementation | RAVI decision | Verification |
| --- | --- | --- |
| Kerykeion exposes one backend facade; its factory delegates session setup to `ephemeris_session`. | Concrete runtime wiring belongs in one composition root, not the application pipeline. | Import-boundary and backend-free application tests. |
| Kerykeion chooses its backend and data path at module import, including environment-based discovery and fallback. | Do not copy discovery: require an explicit runtime and named source profile. Importing RAVI must not load Swiss or select runtime data. | Fresh-process import test; invalid/missing runtime tests. |
| Kerykeion's session validates settings, rejects nesting, locks state and cleans up in `finally`. | Preserve as evidence for M2.6.2. Do not claim this step fixes the existing Swiss session. | Deferred to the next milestone gate. |
| Immanuel `Chart.__init__` snapshots passed `Config` into `FrozenConfig` and passes it to calculations. | Own a detached policy snapshot for the lifetime of each engine. | Mutate the caller's original mapping; repeat A → B → A and check both result and engine policy. |
| Immanuel `FrozenConfig` blocks attribute assignment, recursively freezes selected ChainMaps, but deep-copies other fields; those copied nested collections are not all immutable. | Do not equate the class name with universal deep immutability. Freeze RAVI's current string-to-string policy map at the engine boundary. Hierarchical Canon and fingerprint remain M2.6.4. | Mutation rejection and caller-alias tests. |
| Immanuel explicitly separates per-chart settings from process-global ephemeris paths, whose helper functions mutate Swiss state. | Keep runtime configuration distinct from calculation policy; do not copy its global path setter API. | Frozen runtime object and explicit construction tests. |

## Limits

- Structural baseline uses the explicitly non-canonical development profile. A green
  structural suite is not proof of strict Swiss-file correctness (M2.6.3).
- Startup can validate a directory and manifest, but cannot promise astronomical
  coverage for every future birth date. The existing adapter's returned-source guard
  still checks each calculation. Dataset coverage/official checksums are M2.6.3.
- Engine immutability does not make arbitrary caller-injected ports immutable or
  thread-safe. Dependency injection is a trusted integration boundary.
- The existing session lifecycle, generic charts, policy fingerprint and schema
  semantic hardening remain separate steps. No new Jyotish technique is introduced.
