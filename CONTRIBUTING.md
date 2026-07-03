# Contributing

Notes for contributors and maintainers. End-user documentation is in [README.md](README.md).

## Development setup

```bash
git clone https://github.com/ThorOdinson246/whatwasit.git
cd whatwasit
pip install -e ".[dev]"
pytest
```

## Releasing to PyPI

Publishing is automated via [.github/workflows/publish.yml](.github/workflows/publish.yml).

**One-time:** add GitHub Actions secret `PYPI_API_TOKEN` (PyPI API token scoped to
project `whatwasit`).

**Each release:**

1. Bump `version` in `pyproject.toml` and `whatwasit/__init__.py`.
2. Commit and push to `main` (do **not** push `vX.Y.Z` yourself — the workflow
   creates the tag after a successful PyPI upload).

The workflow detects the version bump, publishes to PyPI, verifies the package
is indexed, and creates `vX.Y.Z` on GitHub. If you already pushed the tag
manually, the workflow still succeeds and skips tag creation.

Publishing a GitHub Release for an existing tag also triggers the workflow.
To re-publish a version that failed before upload, use **Actions → Publish to
PyPI → Run workflow** (skips if that version is already on PyPI).

## Further reading

| Doc | Contents |
|-----|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design decisions and module layout |
| [BENCHMARKS.md](BENCHMARKS.md) | Performance measurements |
| [eval/README.md](eval/README.md) | Search quality evaluation harness |
| [FUTURE_IDEAS.md](FUTURE_IDEAS.md) | Out-of-scope ideas |
