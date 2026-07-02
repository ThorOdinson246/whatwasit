"""Synthetic multi-topic shell-history generator for tests.

Produces realistic-looking zsh ``EXTENDED_HISTORY`` text and lists of
:class:`whatwasit.models.Command` objects, organized into distinct "topics"
(nginx, docker, postgres, git rebase, python venv, ...). Each topic is a
self-contained block of commands that starts with a ``cd`` into the
topic's working directory, so downstream session-grouping logic has
clear boundaries to find: commands within a topic are close together in
time (tens of seconds apart) while different topics are separated by a
large time jump (more than five minutes).

This module is intentionally dependency-free (stdlib only) and only
imports :class:`whatwasit.models.Command` from the main package.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence

from whatwasit.models import Command

# ---------------------------------------------------------------------------
# Topic templates
# ---------------------------------------------------------------------------
#
# Each topic is a dict with:
#   name:  short identifier, e.g. "nginx"
#   cwd:   working directory the topic's commands operate in
#   cmds:  ordered list of shell commands; the FIRST entry is always a
#          ``cd <cwd>`` so that topic boundaries are unambiguous
#   query: a natural-language query a user might type later to recall
#          this session, e.g. "when did I fix the nginx ssl config"

TOPICS: List[Dict[str, object]] = [
    {
        "name": "nginx",
        "cwd": "/etc/nginx",
        "cmds": [
            "cd /etc/nginx",
            "sudo vim sites-available/default.conf",
            "sudo nginx -t",
            "sudo openssl x509 -in /etc/ssl/certs/example.crt -noout -dates",
            "sudo vim sites-available/ssl.conf",
            "sudo nginx -t",
            "sudo systemctl reload nginx",
            "curl -vI https://example.com",
            "tail -f /var/log/nginx/error.log",
            "sudo systemctl status nginx",
        ],
        "query": "when did I fix the nginx reverse proxy ssl config",
    },
    {
        "name": "docker",
        "cwd": "~/projects/microservices",
        "cmds": [
            "cd ~/projects/microservices",
            "docker network create backend-net",
            "docker network ls",
            "docker network inspect backend-net",
            "docker build -t api-service:dev ./api",
            "docker run --network backend-net --name api -d api-service:dev",
            "docker run --network backend-net --name db -d postgres:15",
            "docker network inspect backend-net",
            "docker exec -it api ping db",
            "docker logs -f api",
        ],
        "query": "show me when I set up docker networking between containers",
    },
    {
        "name": "postgres",
        "cwd": "/var/lib/postgresql/15",
        "cmds": [
            "cd /var/lib/postgresql/15",
            "psql -U postgres -h localhost -c 'select 1'",
            "sudo vim /etc/postgresql/15/main/pg_hba.conf",
            "sudo vim /etc/postgresql/15/main/postgresql.conf",
            "sudo systemctl restart postgresql",
            "sudo systemctl status postgresql",
            "psql -U app_user -d app_db -h localhost",
            "tail -n 200 /var/log/postgresql/postgresql-15-main.log",
            "psql -U postgres -c \"select * from pg_stat_activity\"",
        ],
        "query": "find the session where I debugged the postgres connection refused error",
    },
    {
        "name": "git-rebase",
        "cwd": "~/projects/whatwasit",
        "cmds": [
            "cd ~/projects/whatwasit",
            "git fetch origin",
            "git log --oneline origin/main..HEAD",
            "git rebase -i origin/main",
            "git status",
            "git add -A",
            "git rebase --continue",
            "git diff origin/main..HEAD",
            "git push --force-with-lease origin feat/synthetic",
        ],
        "query": "what commands did I run to interactively rebase my feature branch",
    },
    {
        "name": "python-venv",
        "cwd": "~/projects/newapp",
        "cmds": [
            "cd ~/projects/newapp",
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt",
            "pip freeze > requirements.lock.txt",
            "pytest -q",
            "deactivate",
        ],
        "query": "how did I set up the python virtual environment for the new app",
    },
]

TOPIC_QUERIES: Dict[str, str] = {topic["name"]: topic["query"] for topic in TOPICS}

# Time spacing constants (seconds).
_MIN_GAP = 30
_MAX_GAP = 90
_TOPIC_GAP = 3600  # 1 hour; comfortably more than the 5-minute session cutoff


def _topics_or_default(topics: Optional[Sequence[Dict[str, object]]]) -> List[Dict[str, object]]:
    return list(topics) if topics is not None else TOPICS


def _perturb_command(cmd: str, rng: random.Random) -> str:
    """Lightly vary a command so repeated topic blocks aren't byte-identical.

    Keeps the leading ``cd`` lines untouched (so topic boundaries stay
    detectable) and otherwise only tweaks trailing flags/comments, never
    changing the command's basic shape.
    """
    if cmd.startswith("cd "):
        return cmd
    if rng.random() < 0.3:
        return cmd + "  # " + rng.choice(["retry", "again", "check", "ok"])
    return cmd


def generate_zsh_history(
    topics: Optional[Sequence[Dict[str, object]]] = None,
    seed: int = 0,
    base_ts: int = 1700000000,
) -> str:
    """Return zsh ``EXTENDED_HISTORY`` text spanning several topic sessions.

    Each line has the form ``: <epoch>:0;<command>``. Commands within a
    topic are spaced 30-90s apart; topics are separated by a gap larger
    than five minutes so each topic forms its own session.
    """
    rng = random.Random(seed)
    chosen = _topics_or_default(topics)
    lines: List[str] = []
    ts = base_ts
    for ti, topic in enumerate(chosen):
        if ti > 0:
            ts += _TOPIC_GAP
        for ci, raw_cmd in enumerate(topic["cmds"]):
            if ci > 0:
                ts += rng.randint(_MIN_GAP, _MAX_GAP)
            cmd = _perturb_command(raw_cmd, rng)
            lines.append(f": {ts}:0;{cmd}")
    return "\n".join(lines) + "\n"


def write_zsh_history(path: str, **kwargs) -> None:
    """Write :func:`generate_zsh_history` output to ``path``."""
    text = generate_zsh_history(**kwargs)
    with open(path, "w") as f:
        f.write(text)


def generate_commands(
    n: int,
    seed: int = 0,
    base_ts: int = 1700000000,
) -> List[Command]:
    """Efficiently produce ~``n`` :class:`Command` objects.

    Repeats the topic blocks (cycling through them), lightly perturbing
    each command, and advancing timestamps so each repetition of a block
    forms its own session (>5 minute gap between blocks, 30-90s within a
    block). Designed to handle ``n`` up to 100k quickly with low memory
    overhead (single pass, no intermediate large structures beyond the
    output list itself).
    """
    rng = random.Random(seed)
    topics = TOPICS
    n_topics = len(topics)
    commands: List[Command] = []
    ts = base_ts
    topic_idx = 0
    block_idx = 0
    while len(commands) < n:
        topic = topics[topic_idx % n_topics]
        cwd = topic["cwd"]
        cmds = topic["cmds"]
        if block_idx > 0:
            ts += _TOPIC_GAP
        for ci, raw_cmd in enumerate(cmds):
            if ci > 0:
                ts += rng.randint(_MIN_GAP, _MAX_GAP)
            cmd = _perturb_command(raw_cmd, rng)
            commands.append(Command(raw_cmd=cmd, ts=ts, source="zsh", cwd=cwd))
            if len(commands) >= n:
                break
        topic_idx += 1
        block_idx += 1
    return commands
