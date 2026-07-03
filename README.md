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
- **Hybrid search** — semantic embeddings plus FTS5 keyword matching for tool
  names, flags, and short literal queries
- **Incremental indexing** — `whatwasit index` skips rebuild when history files
  are unchanged (mtime/size fingerprint)
- **Interactive TUI** — live debounced search, collapsible sessions, themes
- **Scripting** — `--json`, `--plain`, and pipe-friendly headless output
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

**Requirements:** Python 3.9+, ~100 MB for the embedding model (downloaded once on
first run), and for clipboard copy on Linux: `wl-copy` (Wayland) or `xclip`
(X11).

## Quick start

```bash
# Build the search index from your shell history
whatwasit index

# Interactive REPL (default when run with no arguments)
whatwasit

# One-shot search
whatwasit "that time I set up passwordless ssh"

# JSON for scripts and agents
whatwasit "docker compose down" --json
```

## Usage

```bash
# Refresh the index (skips if history sources unchanged)
whatwasit index

# Force a full rebuild
whatwasit index --rebuild

# Adjust session grouping window (default: 300 seconds)
whatwasit index --window 600

# Plain output (Rich panels on a TTY, line-oriented when piped)
whatwasit "docker volume that wouldn't persist" --plain

# Machine-readable JSON
whatwasit "nginx config" --json

# Return more results
whatwasit "nginx config" -k 20

# Optional warm daemon for faster repeated queries
whatwasit daemon start
whatwasit daemon status
whatwasit daemon stop
```

### TUI / REPL

Running `whatwasit` with no arguments opens a persistent REPL: search bar on top,
results below, key hints in the footer. Results update live as you type (short
debounce). Each row shows the primary command in bold, path underneath, and a
relative timestamp (`2h ago`) right-aligned. Low-confidence matches show a `⚠`
after the command.

Sessions with multiple commands collapse to the matched command plus context;
press **Space** to expand. When the top result is below the confidence threshold
(default 0.40), a soft warning banner appears without hiding results.

| Key / command | Action |
|---------------|--------|
| Type in search box | Live search (2+ characters) |
| `j` / `k` or arrows | Navigate results |
| Enter | Copy matched command(s) to clipboard |
| Space | Expand or collapse a session |
| `m` or `/more` | Show more results |
| `t` or `/theme` | Cycle color theme |
| `/theme <name>` | Set theme (`midnight`, `default`, `high-contrast`) |
| `/settings` | Show theme and config |
| `/help` | Show keybindings |
| Tab / Shift+Tab | Focus results ↔ search |
| `/quit` or `q` | Quit |

One-shot `whatwasit "query"` opens the same result browser with pre-fetched
results. Use `--plain`, `--headless`, or `--json` for non-interactive output.

### Configuration

Optional config file: `~/.config/whatwasit/config.toml`

```toml
output_mode = "tui"              # "tui" or "plain"
tui_page_size = 5
tui_theme = "midnight"           # midnight | default | high-contrast
low_confidence_threshold = 0.40
use_daemon = true                # use warm daemon when running (if started)
```

Theme changes from the REPL (`t` or `/theme`) are saved here automatically.
CLI flags override config values where applicable (for example, `--plain` forces
plain output).

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
4. **Index** — stores vectors in a local index, session metadata in SQLite, and
   command text in FTS5 for keyword search
5. **Search** — embeds your query, finds nearest sessions, merges keyword hits
   via reciprocal-rank fusion, and highlights matching commands within each session

## Privacy

- All search and indexing run on your machine
- No network calls after the one-time model download
- Your shell history is never uploaded anywhere
- Daemon Unix socket is restricted to your user (`0o600`)

## Feedback

Bug reports and feature requests:
[github.com/ThorOdinson246/whatwasit/issues](https://github.com/ThorOdinson246/whatwasit/issues)

## License

MIT — see [LICENSE](LICENSE).
