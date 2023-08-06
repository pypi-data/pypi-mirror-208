# sphinx-shikijs

Use [Shiki](https://shiki.matsu.io/) to highlight code.

## Installation

```
pip install sphinx-shikijs
```

Then, add `sphinx_shikijs` to your extensions in `conf.py`:

```python
extensions = [
  # ...
  "sphinx_shikijs",
]
```

## Configuration

| Setting | Default | Description |
| --- | --- | --- |
| shikijs_mode | `"cli"` | Either `"cli"` or `"browser"`. In browser mode, this will load Shiki from [unpkg](https://unpkg.com/shiki@0.14.1/dist/index.unpkg.iife.js). |
| shikijs_path | `"shiki-cli"` | Path to a Shiki CLI executable. |
| shikijs_highlight_theme | `"dark-plus"` | A Shiki theme. For possible themes, see [here](https://github.com/shikijs/shiki/blob/main/docs/themes.md) |