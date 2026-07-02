# whatwasit

**Local-first semantic search for your shell history.**

Search by what you were *trying to do*, not the exact command you typed — and
nothing ever leaves your machine.

```bash
whatwasit "how did I fix that nginx issue"
```

Returns the session of commands you actually ran (`cd`, `vim`, `systemctl reload
nginx`) weeks ago, even though you never typed "fix" or "issue".

## Features

- **Intent-based recall** — searches whole command sessions, not isolated lines
- **Session grouping** — reconstructs working directory and groups commands by time
- **Hybrid reranking** — boosts exact tool-name and flag matches when your query
  contains them, without hurting natural-language queries
- **Fully offline** — ONNX embedding model on CPU; no cloud, no API keys
- **Non-destructive** — reads your existing history files; never modifies them

## Install

```bash
pip install whatwasit
```

Upgrade an existing install:

```bash
pip install -U whatwasit
```

**Requirements:** Python 3.9+ and ~100 MB disk for the embedding model (downloaded
once on first run).

## Quick start

```bash
# Build the search index from your shell history
whatwasit index

# Interactive REPL (default when run with no arguments)
whatwasit

# One-shot search
whatwasit "that time I set up passwordless ssh"
```

## Usage

```bash
# Refresh the index after new history accumulates
whatwasit index

# Force a full rebuild
whatwasit index --rebuild

# Adjust session grouping window (default: 300 seconds)
whatwasit index --window 600

# Plain output for scripts and piping
whatwasit "docker volume that wouldn't persist" --plain

# Return more results
whatwasit "nginx config" -k 20

# Keep the embedder warm for faster repeated queries (optional)
whatwasit daemon start
whatwasit daemon status
whatwasit daemon stop
```

### TUI / REPL

Running `whatwasit` with no arguments opens a persistent REPL with a bottom input
bar. Type a natural-language query and press Enter to search; results update in
place with matched commands highlighted. Directory and timestamp appear as dim
metadata under each result. Ranks (#1, #2, …) and confidence badges
(`strong` / `medium` / `weak`) replace raw scores. When the top result is below
the low-confidence threshold (default 0.40), a soft warning banner appears
without hiding results.

| Key / command | Action |
|---------------|--------|
| `j` / `k` or arrows | Navigate results |
| Enter (on a result) | Copy matched command(s) to clipboard |
| `n` or `/more` | Show more results |
| `/help` | Show help |
| `/quit` or `q` | Quit |

One-shot `whatwasit "query"` opens the same TUI layout with pre-fetched results.
Use `--plain` or `--headless` for line-oriented output.

### Configuration

Optional config file: `~/.config/whatwasit/config.toml`

```toml
output_mode = "tui"              # "tui" or "plain"
tui_page_size = 5
low_confidence_threshold = 0.40
use_daemon = true                # use warm daemon when running (if started)
```

CLI flags override config values (for example, `--plain` forces plain output).

**Data directory:** `~/.local/share/whatwasit/` (`whatwasit.db` + `index.usearch`)

If you indexed under the older `hist` app name, that data path is still detected
automatically — no re-index required.

**History sources:** `~/.zsh_history`, `~/.bash_history`, and Atuin (if installed).
All sources are read non-destructively.

## How it works

1. **Parse** — reads shell history into timestamped commands
2. **Group** — clusters commands into sessions by time gap and working directory
3. **Embed** — encodes each session locally with
   [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
   (~22 MB ONNX, CPU-only)
4. **Index** — stores vectors in a local index with SQLite metadata
5. **Search** — embeds your query, finds nearest sessions, highlights matching
   commands within each session

## Privacy

- All search and indexing run on your machine
- No network calls after the one-time model download
- Your shell history is never uploaded anywhere

## Feedback

Bug reports and feature requests:
[github.com/ThorOdinson246/whatwasit/issues](https://github.com/ThorOdinson246/whatwasit/issues)

## License

MIT — see [LICENSE](LICENSE).
