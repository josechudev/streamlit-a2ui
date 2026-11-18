# Contributing

`streamlit-a2ui` is a small personal project: a Streamlit Components v2 wrapper around the official A2UI web renderer. Bug reports and small fixes are welcome. For anything larger, open an issue first; the scope is deliberately narrow (see "Out of scope" below).

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Node 24 and npm. If your system Node is older, put Node 24 first on the `PATH`, for example `export PATH=~/.nvm/versions/node/v24.15.0/bin:$PATH`.
- Python 3.10 or newer.

## Build and test

Build the frontend before installing the package, and again after any frontend change. Package only from `npm run build`: `npm run dev` writes source maps into the publicly served `asset_dir`, and the build check rejects them.

### Frontend

From `streamlit_a2ui/frontend`:

```bash
npm install
npm run build          # clean + tsc + vite build into build/ (the asset_dir), fail on source maps,
                       # then write ../renderer_capabilities.json and ../THIRD_PARTY_LICENSES.txt
npm run dev            # vite build --watch; emits source maps into build/, never package from it
npm run typecheck
npm test               # Vitest unit tests (src/*.test.ts)
npm run format:check   # Prettier, as CI runs it
```

### Python

From the repository root:

```bash
uv venv
uv pip install -e . --force-reinstall
uv pip install pytest ruff
.venv/bin/streamlit run examples/basic_app.py
.venv/bin/streamlit run examples/streaming_app.py
.venv/bin/pytest -q    # builds and inspects the wheel, so needs npm run build first
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

### Browser smoke test

One Playwright test in `e2e/`, outside the default pytest run. It starts `examples/basic_app.py`, clicks Send and checks the round trip.

```bash
uv pip install pytest-playwright
.venv/bin/playwright install chromium
.venv/bin/pytest e2e -q
```

### Wheel and sdist

After `npm run build`. Delete the setuptools cache `build/` at the repository root first: it keeps old bundles and setuptools ships them (`tests/test_wheel.py` fails on a second bundle). Build the sdist and the wheel separately: a bare `uv build` makes the wheel from the sdist, leaving nothing to compare.

```bash
uv build --sdist --out-dir dist
uv build --wheel --out-dir dist
uvx twine@7.0.0 check --strict dist/*
```

The sdist must rebuild the same wheel without Node. CI runs this with a `PATH` that has no `node`:

```bash
uv build --wheel --out-dir /tmp/from-sdist dist/*.tar.gz
python3 scripts/compare_wheels.py dist/*.whl /tmp/from-sdist/*.whl
```

### Installed-wheel smoke test

Tests the wheel, not the source tree; the e2e server runs from a temporary directory.

```bash
uv venv --python 3.13 /tmp/a2ui-wheel
uv pip install --python /tmp/a2ui-wheel dist/*.whl pytest==9.2.0 pytest-playwright==0.10.0 playwright==1.65.2
(cd /tmp && /tmp/a2ui-wheel/bin/python -c "import streamlit_a2ui; print(streamlit_a2ui.__file__, streamlit_a2ui.renderer_capabilities())")
/tmp/a2ui-wheel/bin/playwright install chromium
/tmp/a2ui-wheel/bin/pytest e2e -q
```

### Streamlit floor

CI's other leg; the first one is Python 3.13 with the latest Streamlit.

```bash
uv venv --python 3.10 .venv-floor
uv pip install --python .venv-floor -e . "streamlit==1.59.*" pytest==9.2.0 ruff==0.17.5 pytest-playwright==0.10.0 playwright==1.65.2
.venv-floor/bin/pytest -q && .venv-floor/bin/pytest e2e -q
```

### Install a published version from PyPI

In a fresh venv, with no cache, outside the checkout, so neither a cached wheel nor the source tree stands in for the published package. Pin the version. A plain install picks the latest final release; a release candidate needs the exact pin (or `--pre` with pip, `--prerelease=allow` with uv), except while no final release exists.

```bash
uv venv --python 3.13 /tmp/a2ui-pypi
uv pip install --python /tmp/a2ui-pypi --no-cache "streamlit-a2ui==<version>"
(cd /tmp && /tmp/a2ui-pypi/bin/python -c "import streamlit_a2ui, importlib.metadata as m; print(streamlit_a2ui.__file__, m.version('streamlit-a2ui'))")
```

The examples are not in the wheel. Take them from the release tag into an empty folder and run them there:

```bash
mkdir -p /tmp/a2ui-pypi-examples && git show v<version>:examples/basic_app.py > /tmp/a2ui-pypi-examples/basic_app.py
(cd /tmp/a2ui-pypi-examples && /tmp/a2ui-pypi/bin/streamlit run basic_app.py)
```

### CI

`.github/workflows/ci.yml` runs all of the above on every pull request and on pushes to `master` and `develop`, with Node 24, on two legs: Python 3.10 with the Streamlit floor (`1.59.*`) and Python 3.13 with the latest Streamlit. A `package` job builds the wheel and sdist once, rebuilds the wheel from the sdist without Node and compares them, runs `twine check` and uploads `dist`; `wheel-smoke` installs that wheel into a fresh venv and runs the browser test against it. Keep the workflow and these commands in step. Third-party actions are pinned to a commit SHA.

Before merging a change that affects rendering, or after upgrading Streamlit or any `@a2ui/*` package, follow [docs/testing-playbook.md](docs/testing-playbook.md), including the manual click-through of both examples.

### Troubleshooting

- A `js=`/`css=` glob matches more than one file in `build/`: run `npm run clean` and rebuild.
- After a rebuild, restart Streamlit and reload the page. The first bundle loaded claims the page's custom elements, and a second copy only shows a notice.

## Branches

The project follows gitflow:

- `master` holds released code only. Every release tag (`v*`) is on a `master` merge commit.
- `develop` is the integration branch. Pull requests for features, fixes and docs go here.
- `feature/<topic>`: cut from `develop`, merged into `develop` by pull request.
- `release/<version>` (for example `release/0.1.0`): cut from `develop` when it is ready to release. It carries only the version bump, the dated CHANGELOG section and fixes found while releasing. Merged into `master` by pull request; after the tag, `master` is merged back into `develop`.
- `hotfix/<version>` (for example `hotfix/0.1.1`): cut from `master` for a bug in a released version, with a test. Merged into `master` by pull request, tagged, then merged back into `develop`.
- `hotfix/<topic>` (for example `hotfix/readme-gif`): a docs-only fix that must reach `master` before the next release, because a published README links it there (images and pages on `master`). Cut from `master`, merged by pull request, then merged back into `develop`. No version bump and no tag.

Every merge goes through a pull request with the four CI checks green. Dependabot's version updates target `develop`.

## Conventions

- Python 3.10+, full type hints, ruff. The public API is exactly `a2ui_surface` and `renderer_capabilities`.
- TypeScript strict mode, no `any`, function components except the one `ErrorBoundary` class.
- Small commits, imperative subject, one concern each.
- Changes to the architecture or the security model need an ADR in `docs/adr/` and the maintainer's approval first.
- `renderer_capabilities.json` and `THIRD_PARTY_LICENSES.txt` are generated by `npm run build`. Never edit them by hand.
- The `@a2ui/*` versions and the `dompurify` override are pinned on purpose ([docs/security.md](docs/security.md)). Don't bump them in an unrelated change.

## Out of scope

These are not planned for 0.1. Please open an issue before working on any of them:

- custom or geospatial catalogs, inline catalogs;
- agent adapters (ADK, LangChain, A2A, AG-UI);
- A2UI 0.9.x or 0.8;
- persisting typed-but-unsent form state across remounts;
- typed Python message models;
- more than one outbound trigger, or sending renderer errors to Python (changes the return type);
- an iframe / Components v1 fallback;
- a streaming helper function;
- a docs site.

## Release process

Releases are published from GitHub Actions with [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/): no API token is stored in the repository or in GitHub secrets. Only the maintainer releases.

### One-time setup (maintainer)

Done for this repository after M2; kept here as a record and for forks.

1. On PyPI, add a pending publisher (Account settings → Publishing → Add a new pending publisher → GitHub): project name `streamlit-a2ui`, owner `josechudev`, repository `streamlit-a2ui`, workflow `release.yml`, environment `pypi`. The first successful upload creates the project and claims the name.
2. On GitHub, create the environment `pypi` (Settings → Environments → New environment) and add yourself as a required reviewer, so every publish waits for an approval. Optionally restrict it to tags matching `v*`.
3. Enable private vulnerability reporting (Settings → Code security), which `SECURITY.md` points to.
4. Rulesets (Settings → Rules): `master` with no deletion or force-push, pull requests required, and the four CI checks required (`Test (py3.10 / streamlit floor)`, `Test (py3.13 / streamlit latest)`, `Build wheel and sdist`, `Installed wheel smoke test`); `develop` with the same rules as `master`; and `release tag` on `refs/tags/v*` with no deletion, update or force-push. None has a bypass.
5. Restrict the `pypi` environment to tags matching `v*` and do not let administrators bypass its reviewer.

### Each release

1. Cut `release/<version>` from `develop` (or `hotfix/<version>` from `master`). Set `version` in `pyproject.toml` (the only place it is defined) and move the `Unreleased` entries in `CHANGELOG.md` under the new version with today's date.
2. Open a pull request into `master`, merge it once CI passes.
3. Dry run on the `master` merge commit: Actions → Release → Run workflow, or `gh workflow run release.yml --ref master`. It builds and checks the wheel and sdist and stops before publishing.
4. Tag and push: `git tag -a v<version> -m v<version>` on the commit the dry run built, then `git push origin v<version>`. The tag must equal the version, for example `v0.1.0rc1` for `0.1.0rc1`; the workflow refuses a mismatch. A pending publisher does not reserve the name on PyPI, so check it is still free before the first release.
5. Approve the `pypi` environment when the workflow asks. Then install the published version in a fresh venv, outside the checkout and with no package cache, and run both examples. Install a pre-release with an exact pin (`==<version>`): a plain install picks it only while no final release exists.
6. Merge `master` back into `develop` with a pull request, so `develop` has the release commit and the CHANGELOG.

### When a release fails

- **Before anything reached PyPI** (the build or the publish job failed): fix it on the release branch and merge it into `master`, then temporarily disable the `release tag` ruleset, delete the tag locally and on GitHub, re-create it on the fixed commit, re-enable the ruleset and push the tag again.
- **After an upload:** never re-tag. Fix it on `hotfix/<next version>` from `master`. PyPI never accepts the same file name twice, even after a deletion. Fix it in the next version (for example `0.1.0rc2`), and yank the broken one on PyPI if users should not get it.
