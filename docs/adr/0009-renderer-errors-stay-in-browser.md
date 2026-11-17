# ADR-009: Renderer errors stay in the browser for v0.1

Status: Accepted.

## Context

Only one message returns to Python per rerun, so errors sent on the same trigger could displace an action.

## Options

- Console only.
- An in-component notice.
- A second trigger.
- Batch outbound messages into a list.

## Decision

An in-component plain-text notice.

## Consequences

- Developers see broken payloads.
- Agents cannot self-correct from validation errors yet.
- Batching is the likely later answer, and it would change the return type.
