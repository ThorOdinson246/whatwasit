# hist

**Local-first semantic search for your shell history.** Search by what you were
*trying to do*, not the exact command you typed -- and nothing ever leaves your
machine.

```bash
hist "how did I fix that nginx issue"
```

...returns the actual session of commands you ran (the `cd`, the `vim`, the
`systemctl reload nginx`) weeks ago, even though you never typed "fix" or
"issue".

## How it works

1. Reads your existing `~/.zsh_history` / `~/.bash_history` (and atuin's DB if
   present) non-destructively.
2. Groups commands into **sessions** (commands close in time and in the same
   working directory).
3. Embeds each session locally with a small ONNX sentence-embedding model
   (`all-MiniLM-L6-v2`, ~22MB, runs on CPU).
4. Stores vectors in a local on-disk index and does nearest-neighbour search at
   query time.

No cloud calls. No API keys. No data leaves your machine.

## Install

```bash
pip install .
```

## Usage

```bash
hist index            # build / refresh the index from your shell history
hist "your query"     # semantic search
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions, and
[FUTURE_IDEAS.md](FUTURE_IDEAS.md) for out-of-scope ideas.
