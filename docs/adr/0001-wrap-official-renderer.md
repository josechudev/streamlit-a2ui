# ADR-001: Wrap the official renderer

Status: Accepted. Confirmed by M0.

## Context

The A2UI spec moved from 0.9 to 1.0 with wire renames within a year.

## Options

- Wrap `@a2ui/react` + `@a2ui/web_core`.
- Reimplement the catalog with `st.*` widgets.
- Wrap `@a2ui/lit`.

## Decision

Wrap React.

## Consequences

- Spec tracking and widgets are inherited from upstream.
- A Node build is required.
- npm packages are pinned exactly, because 0.13, 0.14 and 0.15 each had breaking changes.
- Lit is a cheap fallback, since the widgets are shared custom elements.
