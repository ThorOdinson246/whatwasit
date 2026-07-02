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
2. Commit and push to `main`.

The workflow detects the version bump, publishes to PyPI, and tags `vX.Y.Z`.
Publishing a GitHub Release for an existing tag also triggers the workflow.

## Further reading

| Doc | Contents |
|-----|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design decisions and module layout |
| [BENCHMARKS.md](BENCHMARKS.md) | Performance measurements |
| [eval/README.md](eval/README.md) | Search quality evaluation harness |
| [FUTURE_IDEAS.md](FUTURE_IDEAS.md) | Out-of-scope ideas |
