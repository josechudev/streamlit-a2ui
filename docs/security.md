# Security

`streamlit-a2ui` renders user interfaces that an agent describes. Treat every agent message as untrusted input: a model can be prompt-injected, and an agent can be compromised or simply wrong. This page describes what the package does to contain that, and what it cannot do.

Status: pre-release (M2), A2UI 1.0 only, `@a2ui/react` and `@a2ui/web_core` 0.15.0. Last checked 2026-11-17.

## The model

There is no browser sandbox. Streamlit Components v2 is frameless: the component runs in the app's page, inside a shadow root, and Streamlit documents that the shadow root is not a security boundary (ADR-002). The protection comes from limiting what an agent can make the renderer do:

- **Basic catalog only.** The renderer registers the official A2UI basic catalog (`https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json`) and nothing else. There are no inline catalogs and no way to register custom components (ADR-006). `renderer_capabilities()` advertises exactly that catalog and no inline catalogs.
- **No HTML, CSS or JavaScript parameters.** No Python parameter, React prop or option accepts markup, styles or code from the app author or the agent. Our code has no `dangerouslySetInnerHTML`, and error notices are set as plain text.
- **Sanitised markdown.** Markdown in `Text` components is the one place agent content becomes HTML. It is rendered only by `@a2ui/markdown-it`, which runs the output through DOMPurify with its default options. The renderer is not swappable.
- **Assets ship in the wheel.** The JavaScript and CSS bundle is built into the wheel. Nothing is loaded from a CDN, and no code or fonts are fetched at runtime. The test suite fails if the wheel contains source maps or URLs that would load remote scripts, stylesheets or fonts.
- **Python does not interpret messages.** `a2ui_surface` passes agent messages to the browser as data and returns at most one renderer-to-agent message per rerun, uninterpreted (ADR-003). Our code never evaluates message content or builds selectors or URLs from it.
- **Errors stay in the browser.** A message the renderer rejects is shown as a plain-text notice inside the component and logged with `console.warn`. An exception while React renders one surface is caught by that surface's error boundary and shown the same way, without blanking the other surfaces. Nothing is sent to Python (ADR-009).
- **Only build output is served.** Streamlit serves the component's `asset_dir` (`streamlit_a2ui/frontend/build/`) publicly. `npm run build` fails if it contains source maps, and the generated capabilities and license files are kept outside it.

## Dependency overrides (ADR-008)

`package.json` carries two scoped npm `overrides` under `@a2ui/markdown-it`:

| Override | Why | Remove when |
|---|---|---|
| `@a2ui/web_core` → the root `web_core` (0.15.0) | `@a2ui/markdown-it@0.2.2` declares peer `@a2ui/web_core@^0.14.0`, while `@a2ui/react@0.15.0` needs 0.15. A plain `npm install` fails with `ERESOLVE` | `@a2ui/markdown-it` widens its peer range |
| `dompurify` → `3.4.18`, exact | `@a2ui/markdown-it@0.2.2` pins `dompurify` 3.4.11, which has open advisories (one critical) fixed in 3.4.17. DOMPurify is the package's only HTML sanitiser, so it is not left unpatched | `@a2ui/markdown-it` ships with a patched DOMPurify |

`npm ls dompurify` shows one copy, `dompurify@3.4.18 overridden`, and the built bundle contains DOMPurify's version string `3.4.18`. The consequence: we run a combination of packages that upstream has not released together. Both issues should be reported upstream.

## Known residual risks

1. **Renderer bugs run with the app page's privileges.** Without an iframe, a bug in `@a2ui/react`, `@a2ui/web_core`, Lit, markdown-it or DOMPurify that lets agent content execute script runs as the Streamlit app, with access to its page and session.
2. **Agent-chosen URLs are fetched or opened by the browser.** `Image`, `Video` and `AudioPlayer` take URLs from the agent; `web_core` accepts only `http(s):` and `data:` ones. The user's browser requests them, which reveals the user's IP address and the fact that the surface was viewed, and loads whatever content the URL serves. The catalog's `openUrl` function lets a surface open an agent-chosen `http(s):`, `mailto:` or `tel:` URL in a new tab (`noopener,noreferrer`).
3. **A hostile agent can spoof UI.** A surface can imitate a sign-in form, a payment prompt or a system message. A renderer cannot tell an honest form from a phishing one. App authors should make clear which parts of the page come from an agent.
4. **zod advisory, accepted.** `npm audit` reports `zod <4.6.6` as high severity (GHSA-mrhx-c7xc-m3w5: memory exhaustion while validating oversized constrained collections). `@a2ui/web_core` requires zod 3, and the latest zod 3 (3.25.76) has no fix. A hostile agent could exhaust the browser tab's memory. Accepted until `web_core` moves off zod 3.
5. **Page-wide stylesheet.** `@a2ui/web_core` adopts a stylesheet onto the host document, outside the component's shadow root, that sets `:root { color-scheme: light dark }` and default `--a2ui-*` variables. `isolate_styles=True` does not contain it and the package cannot opt out. On Streamlit 1.67 in a Chromium-based browser it caused no visible change to Streamlit's widgets (`docs/notes-m1.md`), but `html`, `body` and Streamlit's portals now follow the operating system's scheme rather than Streamlit's theme wherever Streamlit does not set colors explicitly.
6. **Custom elements are global.** The basic catalog's widgets are custom elements registered on the page's single registry. Two different builds of this bundle on one page would register the same tag names with different classes. The bundle that loads first claims the page; a later copy shows a notice instead of rendering. Reload the page after rebuilding the frontend.

## Release and supply chain

- **Publishing** uses PyPI Trusted Publishing (OIDC) from `.github/workflows/release.yml`. No API token is stored in the repository or in GitHub secrets. Only the publish job has `id-token: write`, and it runs in the `pypi` environment, which requires the maintainer's approval.
- **GitHub Actions** are pinned to commit SHAs, workflows default to `contents: read`, and checkouts do not persist credentials.
- **Dependabot** proposes weekly updates for npm, pip and GitHub Actions, but ignores `@a2ui/*` and `dompurify`: those pins and overrides are changed by hand (ADR-008).
- **The sdist** ships the prebuilt frontend, so building from it runs no npm install and fetches no JavaScript. CI checks that the wheel built from the sdist equals the direct wheel.

## Current `npm audit`

Run from `streamlit_a2ui/frontend` on 2026-11-17, after the overrides. Two advisories:

- **zod** (GHSA-mrhx-c7xc-m3w5), in the shipped bundle: the accepted residual risk above.
- **picomatch** (GHSA-fc5q-39xc-vjpf, ReDoS through repeated extglobs), published after M1. It is reached only through build and test tooling (`vite`, `vitest`, `tinyglobby`, `fdir`), with globs we write, and is not in the bundle or the wheel. `npm audit fix --force` would downgrade Vitest across a major version, so it is left for Dependabot to pick up once fixed releases exist.

The zod part of the report, unchanged since M1:

```
# npm audit report

zod  <4.6.6
Severity: high
Zod can exhaust memory while validating oversized constrained collections - https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
No fix available
node_modules/zod
  @a2ui/react  *
  Depends on vulnerable versions of @a2ui/markdown-it
  Depends on vulnerable versions of @a2ui/web_core
  Depends on vulnerable versions of zod
  node_modules/@a2ui/react
  @a2ui/web_core  *
  Depends on vulnerable versions of zod
  node_modules/@a2ui/web_core
    @a2ui/markdown-it  *
    Depends on vulnerable versions of @a2ui/web_core
    node_modules/@a2ui/markdown-it

4 high severity vulnerabilities
```

All four zod findings are the one advisory, reported once for zod and once for each package that depends on it. With picomatch, `npm audit` now reports 10 high-severity findings in total.

## Reporting a vulnerability

See [SECURITY.md](../SECURITY.md): use GitHub private vulnerability reporting. Please do not open a public issue for an undisclosed vulnerability.
