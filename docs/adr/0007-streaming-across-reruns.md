# ADR-007: Streaming happens across reruns

Status: Accepted. Forced by M0.

## Context

Streamlit allows one call per keyed element per script run.

## Options

- A fragment timer.
- `st.rerun()` per chunk.
- A new key per step. Rejected: it resets state.

## Decision

Document the fragment pattern: the component inside `@st.fragment(run_every=...)`, reading a log that the agent's stream appends to.

## Consequences

- No streaming helper in v0.1.
- Repaint granularity is the fragment interval.
