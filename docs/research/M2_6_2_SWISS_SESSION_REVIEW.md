# M2.6.2 — SwissSession source review

Date: 2026-09-22
Scope: Swiss process-global lifecycle only. No new Jyotish calculation policy.

## Pinned evidence

### Kerykeion

Inspected commit `f7608a1dee404afc16a440e4bf565eeeec46bcbd`:

- `kerykeion/ephemeris_backend/backend.py`
- `tests/core/test_ephemeris_data.py`

Observed:

- one shared re-entrant lock serializes ephemeris access;
- thread-local nesting depth is checked before an inner session changes backend state;
- the session applies path/configuration on entry and cleans up in `finally`;
- the upstream test proves a rejected nested session leaves the active outer sidereal
  result unchanged.

RAVI adopts those lifecycle properties, but not Kerykeion's multi-backend,
topocentric/perspective configuration surface.

### Immanuel

Inspected commit `eba98099b7724598064113ffa1322e78dc4bccf6`:

- `immanuel/settings.py`
- `immanuel/tools/ephemeris.py`

Observed:

- chart configuration is separated from process-global Swiss path configuration;
- `_swe_file_path` is process-global and helper functions call `swe.set_ephe_path()`;
- there is a reset helper for the configured path, but not a scoped session boundary
  equivalent to the target RAVI contract.

RAVI keeps the useful separation between chart policy and runtime data, while avoiding a
public mutable global path API.

### Pyswisseph

Inspected upstream source/docs snapshot
`astrorigin/pyswisseph@91ec65631badc7faf4a4b913570c944a4c1b101d` and validated the
relied-on behavior under RAVI's exact dependency pin `pyswisseph==2.10.3.2` in CI.

Relevant upstream evidence:

- `docs/programmers_manual/sidereal_mode.rst` states that parameters set by
  `set_sid_mode()` survive `close()`;
- `pyswisseph.c` documents `close()` as releasing resources and requires
  `set_ephe_path()` again before subsequent Swiss use;
- upstream tests routinely call no-argument `swe.set_ephe_path()` during setup.

This means `close()` is **resource cleanup, not a universal state restore**.

## RAVI design derived from the evidence

| Risk | Decision | Verification |
| --- | --- | --- |
| Swiss path and sidereal mode are process-global. | One `SwissSession` owns RAVI mutation and a shared lock. | Static mutator-boundary test. |
| `RLock` permits recursion but inner cleanup is semantically unsafe. | Reject same-thread nesting before mutation. | Mock lifecycle test + real outer-state preservation test. |
| `close()` does not erase sidereal configuration. | Reapply complete known RAVI state on every entry; never claim prior-state restoration. | Real Lahiri → True Pushya → Lahiri A/B/A test. |
| Development mode could inherit an old custom path if path setup is skipped. | Even a `None` path executes `swe.set_ephe_path()`. | A/B/A lifecycle event test. |
| Exceptions can leave native resources open. | `close()` runs in `finally`. | Failure-recovery test. |
| Julian conversion previously bypassed the lock/session. | Put `utc_to_jd` inside the same session contract. | Static adapter native-call boundary test. |

## Deliberate limits

- The lock coordinates RAVI code. Third-party code directly mutating `swisseph` in the
  same process can bypass it and is unsupported.
- M2.6.2 does not prove official `.se1` identity or date coverage; that is M2.6.3.
- No new astrological technique, ayanamsha, node rule, house rule, or Varga rule is added.
