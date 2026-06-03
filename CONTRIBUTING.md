# Contributing

Contributions are welcome. Please keep notebooks short, executable, and teaching-focused.

## Development checks

```bash
pip install -r requirements.txt
python scripts/make_notebooks.py
jupyter-book build .
```

Do not commit generated `_build/` output.
