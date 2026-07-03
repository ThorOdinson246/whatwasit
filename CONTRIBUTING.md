# Contributing

Thanks for your interest in `whatwasit`. End-user documentation is in [README.md](README.md).

## Development setup

```bash
git clone https://github.com/ThorOdinson246/whatwasit.git
cd whatwasit
pip install -e ".[dev]"
pytest
```

## Pull requests

- Keep changes focused; match existing style in the files you touch.
- Run `pytest` before opening a PR.
- For search or indexing changes, note whether you re-ran `eval/run_eval.py`.

## Further reading

| Doc | Contents |
|-----|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design decisions and module layout |
| [BENCHMARKS.md](BENCHMARKS.md) | Performance measurements |
| [eval/README.md](eval/README.md) | Search quality evaluation harness |
| [FUTURE_IDEAS.md](FUTURE_IDEAS.md) | Out-of-scope ideas |
