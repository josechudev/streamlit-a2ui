# streamlit-a2ui

Streamlit component that allows you to do X

## Installation instructions

```sh
uv pip install streamlit-a2ui
```

## Local development

Build the frontend before the first run. Streamlit loads the files in `streamlit_a2ui/frontend/build`, and each `js=` / `css=` glob must match exactly one file there.

From `streamlit_a2ui/frontend`:

```sh
npm install
npm run build
```

From the project root:

```sh
uv pip install -e . --force-reinstall
streamlit run example.py
```

While editing the frontend, run `npm run dev` in `streamlit_a2ui/frontend`. That runs Vite in watch mode. If a glob matches more than one file, run `npm run clean` and build again.

## Usage instructions

```python
import streamlit as st

from streamlit_a2ui import streamlit_a2ui

value = streamlit_a2ui()

st.write(value)
```

## Build a wheel

To package this component for distribution:

1. Build the frontend with Vite (from `streamlit_a2ui/frontend`):

   ```sh
   npm install
   npm run build
   ```

2. Build the Python wheel using UV (from the project root):
   ```sh
   uv build
   ```

This will create a `dist/` directory containing your wheel. The wheel includes the compiled frontend from `streamlit_a2ui/frontend/build`.

### Requirements

- Python >= 3.10
- Node.js >= 24 (LTS)

### Expected output

- `dist/streamlit_a2ui-0.0.1-py3-none-any.whl`
- If you run `uv run --with build python -m build` (without `--wheel`), you’ll also get an sdist: `dist/streamlit-a2ui-0.0.1.tar.gz`
