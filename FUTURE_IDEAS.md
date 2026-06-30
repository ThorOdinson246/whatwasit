# Future Ideas (explicitly out of MVP scope)

These are deliberately **not** built in v1. The MVP scope is fixed to the Hard
Requirements. Good ideas are parked here instead of expanding scope.

## Captured from the spec (Full Version)

- **Background daemon / shell hooks for live indexing.** Embed and index new
  commands as they are run, in the background, with zero perceptible latency.
  This is also the clean way to capture the *real* working directory going
  forward (instead of reconstructing it from `cd` replay).
- **Fish shell support.** Reading `~/.local/share/fish/fish_history` (YAML-ish).
- **Interactive mode.** fzf-style fuzzy re-filtering of the ranked results.
- **Deeper atuin integration.** Beyond reading its DB: respect its richer
  metadata (hostname, session id, exit status) for ranking.
- **Git semantic search (`giths`).** Same architecture applied to commit
  messages + first N lines of each diff.
- **Distribution beyond pip.** Homebrew formula; a single static Rust binary for
  the CLI front-end (the embedding/index core could stay Python or move to a
  Rust core with ONNX + usearch bindings).

## Engineering ideas surfaced during design

- **Asymmetric query/passage embedding models** (e5, bge, gte) with
  query/passage prefixes, to better match natural-language queries against
  command documents. Trivial to try behind the existing `Embedder` ABC.
- **Per-command vectors** in addition to per-session, for finer-grained
  highlighting and "jump to the exact command" results.
- **numpy brute-force `VectorIndex` backend** as a zero-native-dep fallback
  (already trivially supported by the `VectorIndex` interface).
- **Incremental indexing** (only embed sessions whose commands changed) once a
  live daemon exists, using content hashes.
- **Schema migrations** beyond the version stamp, once `schema_version > 1`.
- **Secret redaction** on read (mask things that look like tokens/passwords in
  the displayed output). Shell history is sensitive; worth doing carefully.
- **Encryption / sync.** Explicitly out of scope (that is atuin's domain), noted
  only for completeness.

## Process note

If a feature here starts to feel necessary for the MVP, stop and confirm scope
before building it.
