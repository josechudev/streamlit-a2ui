# ADR-008: Dependency overrides

Status: Accepted.

## Context

`@a2ui/markdown-it@0.2.2` has a stale peer range on `@a2ui/web_core` and pins `dompurify` 3.4.11, which has open advisories fixed by 3.4.17. zod 3 has an advisory with no 3.x fix.

## Options

- Override.
- Wait for upstream.

## Decision

Scoped npm overrides for the `web_core` peer and for `dompurify` (exact), and accept the zod advisory.

## Consequences

- We run a combination upstream has not released together.
- Remove each override when upstream fixes it.
- Report both upstream.
