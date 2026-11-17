# ADR-004: The log in session_state is the source of truth

Status: Accepted. Confirmed by M0.

## Context

Not recorded.

## Options

Not recorded.

## Decision

An append-only log in Python. The frontend is a replayable projection of it, with a cursor.

## Consequences

- Remounts are correct by construction.
- The full log is re-sent on every rerun.
- Unsent in-surface edits are lost on remount.
