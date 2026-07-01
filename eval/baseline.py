"""Keyword / substring / fuzzy search baseline for comparison against semantic.

This is the "is semantic actually better than fuzzy grep?" control. It searches
the exact same session documents the semantic path indexes (directory basename +
commands), using classic lexical matching:

  score(session) = (# query content-tokens occurring as substrings in the doc)
                   + 0.1 * difflib_ratio(query, doc)   # fuzzy tie-breaker

Content tokens are the query words with stopwords and very short tokens removed,
giving the lexical baseline its best fair shot. Sessions are ranked by score
descending; ties broken by the fuzzy ratio already folded into the score.

Deliberately dependency-free (stdlib only): SQL LIKE, substring, and difflib are
exactly the "basic fuzzy match" the task asks the baseline to represent.
"""

from __future__ import annotations

import difflib
import re
from typing import Dict, List, Tuple

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "was", "were", "is", "are", "be", "been", "that", "this", "it", "its",
    "my", "me", "i", "we", "our", "so", "up", "out", "at", "by", "from",
    "when", "where", "how", "what", "which", "time", "thing", "stuff",
    "into", "over", "after", "before", "than", "then", "them", "they",
    "had", "have", "has", "did", "do", "does", "got", "get", "getting",
    "kept", "keep", "keeps", "all", "some", "any", "every", "one", "two",
    "back", "again", "actually", "just", "even", "still", "would", "could",
    "not", "no", "yes", "if", "as", "but", "about", "because", "while",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    toks = _TOKEN_RE.findall(text.lower())
    return [t for t in toks if len(t) >= 3 and t not in _STOPWORDS]


def score_session(query: str, doc: str) -> float:
    q_tokens = tokenize(query)
    doc_l = doc.lower()
    substring_hits = sum(1 for t in set(q_tokens) if t in doc_l)
    fuzzy = difflib.SequenceMatcher(None, query.lower(), doc_l).ratio()
    return substring_hits + 0.1 * fuzzy


def rank(query: str, corpus: Dict[str, str]) -> List[Tuple[str, float]]:
    """Rank every session id in ``corpus`` (id -> doc text) for ``query``.

    Returns ``(session_id, score)`` pairs sorted by score descending. A stable
    secondary sort on id keeps output deterministic across runs.
    """
    scored = [(sid, score_session(query, doc)) for sid, doc in corpus.items()]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored
