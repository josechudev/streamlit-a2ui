# Security policy

## Supported versions

This project is pre-release. Only the latest release gets security fixes. Before the first release, only `master` does.

## Reporting a vulnerability

Do not open a public issue for a security problem.

Use GitHub private vulnerability reporting: open the repository's **Security** tab, then **Report a vulnerability**, or go directly to https://github.com/josechudev/streamlit-a2ui/security/advisories/new.

This is a personal project. Expect an acknowledgement within a week on a best-effort basis.

## Scope

The security model, the dependency overrides and the accepted residual risks are described in [docs/security.md](docs/security.md). In short: agent messages are treated as untrusted input, only the official basic catalog is registered, no parameter accepts HTML, CSS or JavaScript, markdown is rendered only through `@a2ui/markdown-it`, and nothing is loaded from a CDN or fetched at runtime.

Issues in the upstream `@a2ui/*` packages should also be reported upstream. Reporting them here does not reach their maintainers.
