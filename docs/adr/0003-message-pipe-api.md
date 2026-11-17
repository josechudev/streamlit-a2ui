# ADR-003: The API is a message pipe

Status: Accepted. Confirmed by M0.

## Context

Not recorded.

## Options

Not recorded.

## Decision

Agent-to-renderer messages go in; at most one renderer-to-agent message comes out per rerun. Python does not interpret either.

## Consequences

- Function calls need no new API.
- App authors handle raw protocol dicts.
