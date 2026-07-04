# Hard search-quality suite

This suite is a stricter companion to the compact canonical eval. It is designed
to catch ranking changes that look good on tidy sessions but fail on realistic
history:

- multiple confusable sessions in the same command family
- longer noisy sessions with retries, navigation, and failed attempts
- exact error-message queries and path/flag memory queries
- near-null queries that are lexically close to existing sessions but absent

Files:

- `hard_sessions.jsonl` - indexed corpus for the hard suite
- `hard_queries.jsonl` - answerable and null queries

Query rows may include a `kind` field:

- `intent` - vague paraphrase; should avoid literal command/flag/path leakage
- `error` - exact remembered error text is intentional
- `fragment` - remembered path, flag, endpoint, or command fragment is intentional
- `null` - no matching session should be confidently returned

The suite is not a replacement for `sessions.jsonl` / `queries.jsonl`; it is a
promotion gate for accuracy work.
