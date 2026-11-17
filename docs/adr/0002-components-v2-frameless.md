# ADR-002: Components v2, frameless

Status: Accepted.

## Context

Streamlit's recommended component API since 1.51 (Components v2) has no iframe.

## Options

- Components v2.
- Components v1 (iframe).

## Decision

Components v2.

## Consequences

- Once-only trigger delivery, in-place updates on rerun, theming through CSS variables.
- No browser sandbox, so the catalog and the sanitiser carry the security argument.
