# ADR-0005 — Hardened Swiss process-global session boundary

Status: Accepted for M2.6.2
Date: 2026-09-22

## Context

Pyswisseph exposes process-global native configuration. RAVI already serialized
`snapshot()` with a private lock, but that boundary was incomplete:

- `julian_time()` called `swe.utc_to_jd()` outside the session;
- path setup happened only when RAVI had a non-null path, so a later development
  calculation could inherit process state set by unrelated prior Swiss use;
- upstream Swiss lets a non-empty `SE_EPHE_PATH` environment variable override even an
  explicit `set_ephe_path(path)` argument, which could defeat RAVI's explicit canonical
  runtime path;
- the adapter itself owned `set_ephe_path`, `set_sid_mode`, and `close`;
- there was no same-thread nested-session guard;
- cleanup used `close()` without an explicit statement of what it does and does not reset.

The upstream pyswisseph documentation is important here: after `close()`, callers must
call `set_ephe_path()` before using Swiss again, while parameters set by
`set_sid_mode()` survive `close()`. Therefore "restore prior global state on exit" is
not a truthful contract because Swiss does not expose all prior state for reconstruction.

## Decision

1. Introduce one `SwissSession` class as the only RAVI owner of Swiss global-state
   mutation and lifecycle cleanup.
2. Serialize sessions with one process-local `RLock`.
3. Track same-thread nesting separately and reject a nested session **before** it mutates
   Swiss state. Re-entrant locking is an implementation detail, not permission to nest
   semantically destructive sessions.
4. On every entry, explicitly apply the complete state RAVI currently depends on:
   ephemeris path, sidereal mode, and calculation flags.
5. While applying the RAVI ephemeris path, temporarily mask a non-empty process
   `SE_EPHE_PATH` so upstream Swiss cannot override the explicit runtime choice. Restore
   the caller's environment immediately after `set_ephe_path()`, before yielding.
6. Development sessions with no explicit ephemeris directory still call
   `swe.set_ephe_path()`, so they reinitialize path state instead of implicitly inheriting
   a prior RAVI path.
7. On every exit, including exceptions, call `swe.close()` to release native resources.
   Do **not** claim that this restores an unknown pre-session sidereal/path configuration.
   Safety comes from deterministic reapplication on the next entry.
8. A configured `SwissEphemerisAdapter` opens one scoped astronomy session per chart
   calculation. That active handle performs both `utc_to_jd` and snapshot production
   while one `SwissSession.open()` lifecycle remains active; the configured adapter
   itself performs no native calculation calls.
9. Active astronomy-session handles expire when their context exits and reject later use;
   they are also bound to the thread that opened them.
10. Static contract tests make direct Swiss global-state mutators outside `session.py`
   fail CI and keep native calculation calls off the configured adapter object.

## Consequences

- Sequential A → B → A calculations cannot depend on RAVI's preceding session path or
  sidereal setting.
- A process-level `SE_EPHE_PATH` cannot silently replace the RAVI runtime path, while
  the user's environment is preserved outside the brief native path-setup call.
- Failed calculations still close native resources and the next session starts from
  explicitly applied RAVI state.
- Julian conversion and position/Ascendant calculation cannot be separated by an
  intervening RAVI Swiss session; they share one calculation-scoped native lifecycle.
- A rejected nested session cannot reset or change the active outer session.
- The adapter becomes a consumer of a lifecycle boundary rather than an owner of global
  state mechanics.
- This does not make arbitrary third-party code that imports `swisseph` obey RAVI's
  lock. Mixing unsynchronized external Swiss calls in the same process is outside the
  supported runtime contract.
- Dataset authenticity and date coverage remain M2.6.3, not M2.6.2.
