"""Command-line entry point for ``hist``.

Two modes:

- ``hist index [--window N] [--rebuild]`` builds/refreshes the on-disk index
  from shell history.
- ``hist <natural language query...>`` (the common case) searches the index
  and renders the results with :mod:`hist.output`.

Implemented with :mod:`argparse`; the query subcommand is detected purely by
position (``index`` is only ever a subcommand when it is the first token),
so a bare quoted natural-language query never collides with it unless the
query literally starts with the word ``index``.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from .config import Config
from .indexer import build_index_from_history
from .output import display_results
from .search import search

PROG = "hist"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Local-first semantic search over your shell history.",
    )
    subparsers = parser.add_subparsers(dest="command")

    index_parser = subparsers.add_parser(
        "index", help="Build or refresh the search index from shell history."
    )
    index_parser.add_argument(
        "--window",
        type=int,
        default=None,
        help="Session grouping window in seconds (default: config default).",
    )
    index_parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force a full rebuild of the index from scratch.",
    )

    return parser


def _print_help(parser: argparse.ArgumentParser) -> None:
    parser.print_help()


def _run_index(args: argparse.Namespace) -> int:
    config = Config.default()
    if args.window is not None:
        config.session_window_seconds = args.window

    stats = build_index_from_history(config)
    print(
        f"Indexed {stats.n_commands} commands into {stats.n_sessions} sessions "
        f"in {stats.elapsed_seconds:.2f}s."
    )
    return 0


def _run_query(
    query: str,
    top_k: Optional[int],
    *,
    force_plain: bool = False,
) -> int:
    config = Config.default()
    if top_k is not None:
        config.top_k = top_k

    if not config.db_path.exists():
        print(
            "No index found. Run `hist index` first to build a search index "
            "from your shell history."
        )
        return 1

    results = search(config, query, k=top_k)
    display_results(results, query, config, force_plain=force_plain)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)

    parser = _build_parser()

    if not argv or argv[0] in ("-h", "--help"):
        _print_help(parser)
        return 0

    if argv[0] == "index":
        args = parser.parse_args(argv)
        return _run_index(args)

    # Anything else is a natural-language query. Pull out -k/--top-k,
    # --plain/--headless (which may appear anywhere) and treat the remaining
    # tokens as the query text.
    top_k: Optional[int] = None
    force_plain = False
    query_tokens: List[str] = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in ("-k", "--top-k"):
            if i + 1 >= len(argv):
                print(f"{PROG}: argument {token}: expected one argument", file=sys.stderr)
                return 2
            try:
                top_k = int(argv[i + 1])
            except ValueError:
                print(f"{PROG}: argument {token}: invalid int value: {argv[i + 1]!r}", file=sys.stderr)
                return 2
            i += 2
            continue
        if token in ("--plain", "--headless"):
            force_plain = True
            i += 1
            continue
        query_tokens.append(token)
        i += 1

    query = " ".join(query_tokens).strip()
    if not query:
        _print_help(parser)
        return 0

    return _run_query(query, top_k, force_plain=force_plain)


if __name__ == "__main__":
    sys.exit(main())
