# Upstream issue drafts

Drafts for the owner to file on [a2ui-project/a2ui](https://github.com/a2ui-project/a2ui) (the repository named in every `@a2ui/*` `package.json`). Filed or commented on by the owner on 2026-11-17, except issue 4 (see the table).

Checked 2026-11-17 against `@a2ui/react` 0.15.0, `@a2ui/web_core` 0.15.0 and `@a2ui/markdown-it` 0.2.2. Before filing each one: check the latest published versions, search existing issues and pull requests, and follow the repository's contribution instructions. Once filed, link the issue from `docs/security.md`, ADR-008 and the relevant `package.json` override, and record the URL here. `package.json` cannot carry comments, so the overrides there are not annotated.

| # | Package | Title | Filed |
|---|---|---|---|
| 1 | `@a2ui/markdown-it` | Peer range `@a2ui/web_core@^0.14.0` conflicts with `@a2ui/react@0.15.0` | already reported by someone else as [a2ui-project/a2ui#4059](https://github.com/a2ui-project/a2ui/issues/4059); the owner added our reproduction and workaround in [a comment](https://github.com/a2ui-project/a2ui/issues/4059#issuecomment-6963622021) |
| 2 | `@a2ui/markdown-it` | Exact `dompurify` 3.4.11 pin matches published advisories | [a2ui-project/a2ui#4278](https://github.com/a2ui-project/a2ui/issues/4278) |
| 3 | `@a2ui/web_core` | Basic catalog always adopts its stylesheet onto `document` | [a2ui-project/a2ui#4279](https://github.com/a2ui-project/a2ui/issues/4279) |
| 4 | `@a2ui/web_core` | 1.0 `updateComponents` accepts component types the catalog does not define | **do not file as drafted**; see below |

### Recheck, 2026-11-17 (M3)

Latest on npm: `@a2ui/react` and `@a2ui/web_core` 0.15.0, `@a2ui/markdown-it` 0.2.2, so the drafts still apply to the latest releases. Searched `a2ui-project/a2ui` issues and pull requests, and read `main`:

1. **Duplicate.** [#4059](https://github.com/a2ui-project/a2ui/issues/4059) reports the same peer conflict (open, two comments). On `main` the peer is `workspace:*`, so the next release should carry a 0.15 range. A fix is open upstream: pull request [#4073](https://github.com/a2ui-project/a2ui/pull/4073) bumps `@a2ui/markdown-it` to 0.2.3 and guards against stale peer ranges at publish time; it does not change the `dompurify` pin, so issue 2 is still needed. Add our reproduction and the `overrides` workaround as a comment, or a reaction, and link #4059 from `docs/security.md` and ADR-008.
2. **Still open, no existing issue.** `main` still pins `dompurify` to exactly `3.4.11` (`typescript/renderers/markdown-it/package.json`). No issue or pull request mentions the advisories. File it; the repository has no `SECURITY.md`, and the advisories are public, so a normal bug report is fine.
3. **Still open, not reported.** `injectBasicCatalogStyles` on `main` still adopts the sheet onto `document` unconditionally. A related, different leak was fixed: [#3422](https://github.com/a2ui-project/a2ui/issues/3422) (`A2uiLitElement.adoptLightDomStyles()`, fixed by pull request #3666). Mention it in the report so it is not closed as a duplicate.
4. **Mostly ours, not upstream's.** `@a2ui/web_core` 0.15.0 already rejects unknown component types when the processor is given a `validationConfig` with `allowUnknownElements: false` (exported presets `STRICT_VALIDATION` and `RELAXED_VALIDATION`). Without a `validationConfig` it skips that check on purpose; [#3510](https://github.com/a2ui-project/a2ui/issues/3510), about that default, was closed. Our `session.ts` passes no `validationConfig`, which is why the draft's reproduction stores `NoSuchThing`. `STRICT_VALIDATION` also rejects a missing root, orphans and dangling references, which would break progressive streaming, so the candidate fix is `{ ...RELAXED_VALIDATION, allowUnknownElements: false }`. That is a package change for M3 step 3 (needs a test, and the README limitation and the `CLAUDE.md` note change with it); it is not done yet. Related open upstream issues: [#4018](https://github.com/a2ui-project/a2ui/issues/4018) (component id and type in `onError` reports) and [#2297](https://github.com/a2ui-project/a2ui/issues/2297) (the same gap on the 0.9 path).

Issue 2 is a security issue in a dependency, already public through the advisories. It can be filed as a normal issue; if the repository asks for security reports through a private channel, use that instead.

---

## 1. `@a2ui/markdown-it`: peer range `@a2ui/web_core@^0.14.0` conflicts with `@a2ui/react@0.15.0`

**Versions:** `@a2ui/markdown-it` 0.2.2, `@a2ui/react` 0.15.0, `@a2ui/web_core` 0.15.0, npm 11.

`@a2ui/react@0.15.0` depends on `@a2ui/web_core@^0.15.0` and `@a2ui/markdown-it@^0.2.2`. `@a2ui/markdown-it@0.2.2` declares the peer dependency `@a2ui/web_core@^0.14.0`, which does not include 0.15.x (a caret range on 0.x stops at the next minor). A plain install of the React renderer therefore fails:

```
npm install @a2ui/react@0.15.0 @a2ui/web_core@0.15.0 react react-dom
# npm error code ERESOLVE
# ... peer @a2ui/web_core@"^0.14.0" from @a2ui/markdown-it@0.2.2
```

**Workaround we use** (`package.json`):

```json
"overrides": {
  "@a2ui/markdown-it": { "@a2ui/web_core": "$@a2ui/web_core" }
}
```

With the override everything we use works on 0.15.0, so the range looks stale rather than a real incompatibility.

**Suggested fix:** widen the peer range to include 0.15 (for example `^0.14.0 || ^0.15.0`) and publish a patch release, or release `@a2ui/markdown-it` in lockstep with `web_core`.

---

## 2. `@a2ui/markdown-it`: exact `dompurify` 3.4.11 pin matches published advisories

**Versions:** `@a2ui/markdown-it` 0.2.2.

`@a2ui/markdown-it@0.2.2` depends on `dompurify` at exactly `3.4.11`. `npm audit` reports these advisories against that version, the most severe rated critical (GHSA-cg2g-xh64-v4q7) and one high (GHSA-mrv2-3pqr-j5jr):

- GHSA-cg2g-xh64-v4q7
- GHSA-mrv2-3pqr-j5jr
- GHSA-c2j3-45gr-mqc4
- GHSA-55q2-fjhq-7xh7
- GHSA-6688-9rhm-gjv2
- GHSA-c6gr-qvv4-5v3f

All are fixed in `dompurify` 3.4.17. Because the pin is exact, downstream projects cannot pick up the fix without an npm `overrides` entry. DOMPurify is the only HTML sanitiser between agent-supplied markdown and the page, so this matters more than a typical transitive pin.

**Workaround we use:**

```json
"overrides": {
  "@a2ui/markdown-it": { "dompurify": "3.4.18" }
}
```

With 3.4.18, `npm ls dompurify` shows a single copy, and markdown in `Text` components (for example a `## heading`) renders as before.

**Suggested fix:** update to `dompurify` `^3.4.17` (a caret range, so future DOMPurify security releases reach users without a new `@a2ui/markdown-it` release) and publish a patch release.

---

## 3. `@a2ui/web_core`: basic catalog always adopts its stylesheet onto `document`

**Versions:** `@a2ui/web_core` 0.15.0 (via `@a2ui/react` 0.15.0).

`BasicCatalogA2uiLitElement.connectedCallback()` (`src/universal/basic_catalog/components/basic-catalog-a2ui-lit-element.js`) calls `injectBasicCatalogStyles()` with no argument. `injectBasicCatalogStyles(targetRoot?)` (`src/universal/basic_catalog/styles/default.js`) adds the default stylesheet to `document.adoptedStyleSheets` unconditionally. A `targetRoot` is applied in addition to the document, never instead of it.

The sheet includes `:where(:root) { color-scheme: light dark; }` and default `--a2ui-*` custom properties. So rendering any basic-catalog component changes the host page's `color-scheme`, even when the renderer is mounted inside a shadow root that is meant to contain its styles.

**Why it matters:** we embed the React renderer in Streamlit, inside a shadow root. After the first component mounts, the host page's `html`, `body` and any portals outside the app container switch from `color-scheme: normal` to `light dark`. They then follow the operating system's scheme instead of the host application's theme. We saw no visible breakage in Streamlit 1.67 (it sets explicit colors almost everywhere), but a host page that relies on UA-default form controls or scrollbars would change appearance. The library offers no way to opt out.

**Suggested fix (any one):**
- When the element is inside a shadow root, adopt the sheet into `this.getRootNode()` only, not into `document`.
- When `targetRoot` is given, adopt only into it.
- Move `color-scheme` from `:root` to a scoped selector, such as the surface element or `.a2ui-light` / `.a2ui-dark`.

---

## 4. `@a2ui/web_core`: 1.0 `updateComponents` accepts component types the catalog does not define

**Versions:** `@a2ui/web_core` 0.15.0, spec version 1.0, basic catalog `https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json`.

A component whose `component` type is not in the surface's catalog is stored without any error. Plain Node reproduction:

```js
import { MessageProcessor } from "@a2ui/web_core";
import { basicCatalog } from "@a2ui/web_core/catalogs/basic/v1";

const CATALOG = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json";
const processor = new MessageProcessor([basicCatalog], () => {}, { version: "1.0" });
const errors = [];
processor.model.onError.subscribe((e) => errors.push(e));

const returned = processor.processMessagesWithErrors([
  { version: "1.0", createSurface: { surfaceId: "s", catalogId: CATALOG } },
  { version: "1.0", updateComponents: { surfaceId: "s", components: [
    { id: "root", component: "Column", children: ["x"] },
    { id: "x", component: "NoSuchThing", foo: 1 },
  ] } },
]);

console.log(returned);                                            // []
console.log(errors.length);                                       // 0
console.log(processor.getSurfaces().get("s").componentsModel.get("x").type); // "NoSuchThing"
```

By contrast, a known type with an invalid shape (for example a `Text` without `text`) is rejected with `VALIDATION_FAILED`, as expected.

**Why it matters:** an agent that hallucinates a component name gets no error to correct itself from; the component silently renders nothing. Renderers that report errors back to the agent cannot report this one.

**Expected:** a validation error (for example `VALIDATION_FAILED` or a dedicated code) naming the unknown type and the catalog, emitted through `onError` like other validation errors. If accepting unknown types is intentional (forward compatibility), it would help to document that and to emit a warning-level error instead.
