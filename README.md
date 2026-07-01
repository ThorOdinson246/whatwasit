# hist

**Local-first semantic search for your shell history.**

Search by what you were *trying to do*, not the exact command you typed — and
nothing ever leaves your machine.

```bash
hist "how did I fix that nginx issue"
```

Returns the session of commands you actually ran (`cd`, `vim`, `systemctl reload
nginx`) weeks ago, even though you never typed "fix" or "issue".

## Features

- **Intent-based recall** — embeds whole command sessions, not individual lines
- **Session grouping** — reconstructs working directory and groups commands by time
- **Hybrid reranking** — boosts exact tool-name / flag matches when the query
  contains them, without hurting natural-language queries
- **Fully offline** — ONNX embedding model runs on CPU; no cloud, no API keys
- **Non-destructive** — reads your existing history files; never modifies them

## Install

From source (PyPI publish coming soon):

```bash
git clone https://github.com/ThorOdinson246/hist.git
cd hist
pip install .
```

For development:

```bash
pip install -e ".[dev]"
```

**Requirements:** Python 3.9+, ~100 MB disk for the embedding model (downloaded
once on first run).

## Usage

```bash
# Build or refresh the search index from your shell history
hist index

# Force a full rebuild
hist index --rebuild

# Adjust session grouping window (default: 300 seconds)
hist index --window 600

# Interactive REPL (default when run with no arguments)
hist

# One-shot search by intent (TUI with pre-fetched results)
hist "that time I set up passwordless ssh"

# Plain / headless output (Rich panels on a TTY, line-oriented when piped)
hist "docker volume that wouldn't persist" --plain
hist "nginx config" --headless

# Return more results
hist "docker volume that wouldn't persist" -k 20
```

### TUI / REPL

Running ``hist`` with no arguments opens a persistent REPL with a bottom input
bar. Type a natural-language query and press Enter to search; results update in
place with matched commands highlighted. Directory and timestamp appear as dim
secondary metadata under each result. Ranks (#1, #2, …) and qualitative
confidence badges (``strong`` / ``medium`` / ``weak``) replace raw similarity
scores. When the top result is below the low-confidence threshold (default
0.40), a soft warning banner appears without hiding results.

| Key / command | Action |
|---------------|--------|
| ``j`` / ``k`` or arrows | Navigate results |
| Enter (on a result) | Copy matched command(s) to clipboard |
| ``n`` or ``/more`` | Show more results |
| ``/help`` | Show help |
| ``/quit`` or ``q`` | Quit |

One-shot ``hist "query"`` still opens the TUI with the same result layout.
Use ``--plain`` or ``--headless`` for non-interactive output.

**Configuration** (`~/.config/hist/config.toml`):

```toml
# Output mode: "tui" (default) or "plain"
output_mode = "tui"

# Number of results shown initially in the TUI; ``n`` or ``/more`` loads more
tui_page_size = 5

# Banner when top-1 score is below this value (does not suppress results)
low_confidence_threshold = 0.40

# Reserved for a future background daemon (not yet implemented)
use_daemon = false
```

CLI flags override config file values. For example, ``--plain`` forces plain
output even when ``output_mode = "tui"`` in the config file.

**Data location:** `~/.local/share/hist/` (`hist.db` + `index.usearch`).

**Supported history sources:** `~/.zsh_history`, `~/.bash_history`, Atuin DB
(if present). All are read non-destructively.

## How it works

1. **Parse** — reads your shell history files into timestamped commands
2. **Group** — clusters commands into sessions by time gap and working directory
   (replaying `cd` / `pushd` / `popd` to reconstruct CWD)
3. **Embed** — encodes each session locally with
   [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
   (~22 MB ONNX, CPU-only via `onnxruntime`)
4. **Index** — stores vectors in a local `usearch` index with SQLite metadata
5. **Search** — embeds your query, finds nearest sessions, highlights matching
   commands within each session

## Performance

On an Intel i9-14900 (unthrottled), hist meets its design targets:

| Scale | Index time | Query latency (avg) |
|------:|-----------:|--------------------:|
| 10k commands | 7.2 s | 165 ms |
| 100k commands | 92.9 s | 153 ms |

Pure ANN search over 100k session vectors: **< 1 ms**. Details in
[BENCHMARKS.md](BENCHMARKS.md).

## Search quality

Evaluated on a labeled dataset of 86 intent-paraphrase queries (P@1 = 0.535,
MRR = 0.700) against a keyword baseline (P@1 = 0.291). See
[eval/README.md](eval/README.md) for methodology and full metrics.

## Documentation

| Doc | Contents |
|-----|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design decisions and module layout |
| [BENCHMARKS.md](BENCHMARKS.md) | Performance measurements and reproduction |
| [FUTURE_IDEAS.md](FUTURE_IDEAS.md) | Explicitly out-of-scope ideas |
| [eval/README.md](eval/README.md) | Search quality evaluation harness |

## Privacy

- All processing is local — no network calls after the one-time model download
- Your shell history never leaves your machine
- Index data stays in `~/.local/share/hist/`

## Development

```bash
pip install -e ".[dev]"
pytest
python benchmarks/run_bench.py --write-md   # performance benchmarks
python eval/run_eval.py                     # search quality evaluation
```

## License

MIT — see [LICENSE](LICENSE).
