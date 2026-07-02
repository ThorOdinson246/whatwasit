"""Build the labeled evaluation dataset for whatwasit search-quality measurement.

This is the *authoring source* for two durable, version-controlled test assets:

  - ``eval/sessions.jsonl``  -- the corpus that gets indexed (one JSON object per
    session: a stable string ``session_id``, ``topic``, ``cwd``, ``commands``).
  - ``eval/queries.jsonl``   -- the ground truth (one JSON object per query:
    ``query``, ``correct_session_id`` or ``null``, ``topic``).

Design principles (see TASK / EVAL_RESULTS.md):

  * Sessions are hand-authored coherent command sequences using *real* command
    syntax. Public command datasets (hrsvrn/hotal/emir, sampled into
    ``eval/raw_sources/``) are used only as realistic raw material -- their
    natural-language descriptions are NOT reused as queries.
  * Queries are written fresh to simulate how a person vaguely recalls a past
    session weeks later. HARD CONSTRAINT: a query must not reuse the literal
    command words / flags of its target session (no "nginx reload" for a
    ``systemctl reload nginx`` session). This tests intent recall, not keyword
    luck.
  * Multiple sessions share a topic (4 git flavors, 4 docker, 4 python, ...) so
    the eval measures discrimination between near-duplicate topics, not just
    well-separated ones.
  * A block of "distractor" sessions is assembled from real dataset commands to
    add realistic noise to the index (potential false positives). No query is
    expected to match them.
  * Some queries have ``correct_session_id = null`` on purpose: their topic is
    absent from the corpus, so a good system should surface nothing confident.

Running this file regenerates the two JSONL assets deterministically.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
RAW_EMIR = EVAL_DIR / "raw_sources" / "emir_commands_sample.txt"

# ---------------------------------------------------------------------------
# Labeled topic sessions. Each session: id, cwd, commands, and 2-3 fresh
# intent queries that avoid the session's literal command vocabulary.
# ---------------------------------------------------------------------------

TOPIC_SESSIONS = [
    # ===================== GIT (confusable cluster) =====================
    {
        "topic": "git-rebase",
        "id": "git_rebase_conflict",
        "cwd": "~/projects/api",
        "commands": [
            "git fetch origin",
            "git rebase origin/main",
            "vim src/handlers/auth.py",
            "git add src/handlers/auth.py",
            "git rebase --continue",
            "git push --force-with-lease",
        ],
        "queries": [
            "that time I was replaying my commits on top of the latest upstream and it stopped halfway with clashes",
            "when I had to redo my branch history one commit at a time because of overlapping edits",
        ],
    },
    {
        "topic": "git-merge",
        "id": "git_merge_conflict",
        "cwd": "~/projects/api",
        "commands": [
            "git pull origin develop",
            "git status",
            "vim src/models/user.py",
            "git add src/models/user.py",
            "git commit --no-edit",
        ],
        "queries": [
            "sorting out the mess when pulling a teammate's work collided with my own changes",
            "combining two lines of work where the same file got edited on both sides",
        ],
    },
    {
        "topic": "git-undo",
        "id": "git_undo_commit",
        "cwd": "~/projects/api",
        "commands": [
            "git log --oneline -20",
            "git reflog",
            "git revert HEAD~2",
            "git status",
        ],
        "queries": [
            "the time I had to walk back a change I'd already saved into the project history",
            "digging through the record of what I did to get back to an earlier working state",
        ],
    },
    {
        "topic": "git-history-scrub",
        "id": "git_large_file_purge",
        "cwd": "~/projects/api",
        "commands": [
            "git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch secrets.env' HEAD",
            "git push origin --force --all",
            "rm -rf .git/refs/original/",
            "git reflog expire --expire=now --all",
            "git gc --prune=now",
        ],
        "queries": [
            "when I accidentally checked in something that should never have been tracked and had to scrub it from every past revision",
            "purging a sensitive file out of the entire project history everywhere",
        ],
    },
    # ===================== DOCKER (confusable cluster) =====================
    {
        "topic": "docker-volumes",
        "id": "docker_volume_mount",
        "cwd": "~/projects/webapp",
        "commands": [
            "docker run -d --name db postgres:15",
            "docker exec db ls /var/lib/postgresql/data",
            "docker rm -f db",
            "docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres:15",
            "docker volume inspect pgdata",
        ],
        "queries": [
            "why my container kept losing everything every time it restarted",
            "making the data inside a container actually survive between runs",
        ],
    },
    {
        "topic": "docker-networking",
        "id": "docker_network_connect",
        "cwd": "~/projects/webapp",
        "commands": [
            "docker network create appnet",
            "docker run -d --network appnet --name api myapi:latest",
            "docker run -d --network appnet --name cache redis:7",
            "docker exec api ping -c1 cache",
        ],
        "queries": [
            "when two of my services couldn't reach each other until I wired them together",
            "the container-to-container connectivity thing I had to set up",
        ],
    },
    {
        "topic": "docker-compose",
        "id": "docker_compose_stack",
        "cwd": "~/projects/webapp",
        "commands": [
            "docker compose config",
            "docker compose up -d",
            "docker compose ps",
            "docker compose logs -f web",
        ],
        "queries": [
            "spinning up the whole multi-service stack from a single definition",
            "bringing all the pieces of the app online at once",
        ],
    },
    {
        "topic": "docker-cleanup",
        "id": "docker_disk_prune",
        "cwd": "~/projects/webapp",
        "commands": [
            "docker system df",
            "docker image prune -a",
            "docker volume prune",
            "docker system df",
        ],
        "queries": [
            "reclaiming the disk space eaten up by old images and dangling layers",
            "cleaning out all the leftover junk the containers piled up",
        ],
    },
    # ===================== PYTHON (confusable cluster) =====================
    {
        "topic": "python-venv",
        "id": "python_venv_setup",
        "cwd": "~/projects/newtool",
        "commands": [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt",
        ],
        "queries": [
            "isolating a project's libraries so they don't pollute the whole system",
            "setting up a clean sandbox for a fresh script's packages",
        ],
    },
    {
        "topic": "python-depconflict",
        "id": "python_dependency_conflict",
        "cwd": "~/projects/newtool",
        "commands": [
            "pip install 'urllib3<2'",
            "pip check",
            "pip install --upgrade requests",
            "pip freeze | grep -E 'urllib3|requests'",
        ],
        "queries": [
            "when two libraries demanded incompatible versions of the same shared thing",
            "untangling the package version standoff that kept breaking my install",
        ],
    },
    {
        "topic": "python-import",
        "id": "python_import_error",
        "cwd": "~/projects/newtool",
        "commands": [
            "python -c 'import app'",
            "echo $PYTHONPATH",
            "pip show app",
            "pip install -e .",
            "python -c 'import app'",
        ],
        "queries": [
            "chasing down why the interpreter swore a package wasn't there even though I installed it",
            "that missing-module headache when running my code from the wrong place",
        ],
    },
    {
        "topic": "python-profiling",
        "id": "python_profiling",
        "cwd": "~/projects/newtool",
        "commands": [
            "python -m cProfile -o out.prof run.py",
            "python -m pstats out.prof",
            "snakeviz out.prof",
        ],
        "queries": [
            "figuring out which part of my script was dragging the whole thing down",
            "hunting the slow function that was eating all the runtime",
        ],
    },
    # ===================== NPM =====================
    {
        "topic": "npm-deps",
        "id": "npm_dependency_resolution",
        "cwd": "~/projects/frontend",
        "commands": [
            "npm install",
            "rm -rf node_modules package-lock.json",
            "npm install --legacy-peer-deps",
            "npm ls react",
        ],
        "queries": [
            "when the javascript package tree refused to install because requirements clashed",
            "forcing through the node module knot where nothing agreed on versions",
        ],
    },
    {
        "topic": "npm-audit",
        "id": "npm_audit_fix",
        "cwd": "~/projects/frontend",
        "commands": [
            "npm audit",
            "npm audit fix",
            "npm audit fix --force",
            "npm audit",
        ],
        "queries": [
            "patching the flagged security holes in my node packages",
            "dealing with the reported vulnerabilities in my javascript dependencies",
        ],
    },
    {
        "topic": "npm-cache",
        "id": "npm_cache_clear",
        "cwd": "~/projects/frontend",
        "commands": [
            "npm cache verify",
            "npm cache clean --force",
            "rm -rf node_modules",
            "npm install",
        ],
        "queries": [
            "when a corrupted local package store gave me phantom build failures",
            "wiping the download cache to get rid of bizarre install errors",
        ],
    },
    # ===================== SSH =====================
    {
        "topic": "ssh-keys",
        "id": "ssh_key_setup",
        "cwd": "~",
        "commands": [
            "ssh-keygen -t ed25519 -C 'laptop'",
            "ssh-copy-id user@server.example.com",
            "vim ~/.ssh/config",
            "ssh user@server.example.com",
        ],
        "queries": [
            "setting up passwordless login so I'd stop typing my password to connect to the box",
            "the time I created credentials to get into a remote machine without a prompt",
        ],
    },
    {
        "topic": "ssh-agent",
        "id": "ssh_agent_forwarding",
        "cwd": "~",
        "commands": [
            "eval $(ssh-agent)",
            "ssh-add ~/.ssh/id_ed25519",
            "ssh -A user@bastion.example.com",
            "ssh internal-host",
        ],
        "queries": [
            "making my local identity usable from a jump host to reach a machine behind it",
            "when I needed my key to carry through to a second server down the line",
        ],
    },
    {
        "topic": "ssh-denied",
        "id": "ssh_permission_denied",
        "cwd": "~",
        "commands": [
            "ssh -v user@server.example.com",
            "chmod 700 ~/.ssh",
            "chmod 600 ~/.ssh/authorized_keys",
            "ssh user@server.example.com",
        ],
        "queries": [
            "why the remote box kept rejecting me even though I had the right key",
            "troubleshooting getting locked out when logging into a server",
        ],
    },
    # ===================== CRON =====================
    {
        "topic": "cron-setup",
        "id": "cron_job_setup",
        "cwd": "~",
        "commands": [
            "crontab -e",
            "crontab -l",
            "tail -f /var/log/syslog",
        ],
        "queries": [
            "scheduling a script to run on its own every night",
            "setting something up to fire automatically on a repeating timer",
        ],
    },
    {
        "topic": "cron-debug",
        "id": "cron_job_debug",
        "cwd": "~",
        "commands": [
            "grep CRON /var/log/syslog",
            "crontab -l",
            "chmod +x /home/me/backup.sh",
            "run-parts --test /etc/cron.daily",
        ],
        "queries": [
            "why my scheduled task silently never actually ran",
            "chasing a background timer that just refused to trigger",
        ],
    },
    # ===================== DB MIGRATIONS =====================
    {
        "topic": "db-migrate-up",
        "id": "db_migration_run",
        "cwd": "~/projects/api",
        "commands": [
            "alembic current",
            "alembic history",
            "alembic upgrade head",
            "alembic current",
        ],
        "queries": [
            "rolling the database structure forward to the newest version",
            "applying the pending schema changes to my tables",
        ],
    },
    {
        "topic": "db-migrate-down",
        "id": "db_migration_rollback",
        "cwd": "~/projects/api",
        "commands": [
            "alembic history",
            "alembic downgrade -1",
            "alembic current",
        ],
        "queries": [
            "undoing a structural change to the database that broke everything",
            "walking the table layout back after a bad update",
        ],
    },
    # ===================== PERMISSIONS =====================
    {
        "topic": "perm-chmod",
        "id": "chmod_permission_error",
        "cwd": "~/scripts",
        "commands": [
            "./deploy.sh",
            "ls -l deploy.sh",
            "chmod +x deploy.sh",
            "./deploy.sh",
        ],
        "queries": [
            "when the system refused to run my script until I changed its access bits",
            "fixing the you-are-not-allowed error trying to execute a file",
        ],
    },
    {
        "topic": "perm-ownership",
        "id": "sudo_ownership_fix",
        "cwd": "~/projects",
        "commands": [
            "ls -la",
            "sudo chown -R $USER:$USER .",
            "ls -la",
        ],
        "queries": [
            "reclaiming a bunch of files that ended up belonging to the wrong account",
            "when everything was locked because the superuser grabbed my directory",
        ],
    },
    # ===================== DNS =====================
    {
        "topic": "dns-resolve",
        "id": "dns_debugging",
        "cwd": "~",
        "commands": [
            "dig example.com",
            "nslookup example.com",
            "cat /etc/resolv.conf",
            "ping -c2 example.com",
        ],
        "queries": [
            "why a domain name just wouldn't resolve to an address on my machine",
            "chasing a name-lookup failure when trying to reach a site",
        ],
    },
    {
        "topic": "dns-flush",
        "id": "dns_cache_flush",
        "cwd": "~",
        "commands": [
            "resolvectl flush-caches",
            "systemd-resolve --statistics",
            "dig fresh.example.com",
        ],
        "queries": [
            "when an old address kept sticking around long after it had changed",
            "clearing the machine's memory of name lookups to pick up new records",
        ],
    },
    # ===================== NGINX =====================
    {
        "topic": "nginx-proxy",
        "id": "nginx_reverse_proxy",
        "cwd": "/etc/nginx",
        "commands": [
            "sudo vim sites-available/app.conf",
            "sudo nginx -t",
            "sudo systemctl reload nginx",
            "curl -I http://localhost",
        ],
        "queries": [
            "that thing where the gateway wasn't picking up my configuration changes",
            "when the front server kept routing to the old backend after I edited it",
        ],
    },
    {
        "topic": "nginx-ssl",
        "id": "nginx_ssl_cert",
        "cwd": "/etc/nginx",
        "commands": [
            "sudo certbot --nginx -d example.com",
            "sudo certbot renew --dry-run",
            "sudo systemctl reload nginx",
            "curl -vI https://example.com",
        ],
        "queries": [
            "renewing the expiring secure certificate so the browser lock icon stopped complaining",
            "sorting out the https warning visitors were seeing on my site",
        ],
    },
    # ===================== LOGS =====================
    {
        "topic": "log-parse",
        "id": "log_parsing_grep",
        "cwd": "/var/log",
        "commands": [
            "grep -c ' 500 ' access.log",
            "awk '{print $9}' access.log | sort | uniq -c | sort -rn",
            "grep ' 500 ' access.log | tail -20",
        ],
        "queries": [
            "digging through the web server records to tally how often requests were failing",
            "slicing a big log file to count the recurring errors",
        ],
    },
    {
        "topic": "log-rotate",
        "id": "log_rotation",
        "cwd": "/etc/logrotate.d",
        "commands": [
            "du -sh /var/log/*",
            "sudo vim /etc/logrotate.d/myapp",
            "sudo logrotate -f /etc/logrotate.conf",
            "du -sh /var/log/*",
        ],
        "queries": [
            "when runaway log files were quietly eating up all the disk",
            "keeping the ever-growing application output from filling storage",
        ],
    },
    # ===================== DISK / SYSTEM =====================
    {
        "topic": "disk-cleanup",
        "id": "disk_space_cleanup",
        "cwd": "~",
        "commands": [
            "df -h",
            "du -sh /* 2>/dev/null | sort -rh | head",
            "sudo apt clean",
            "df -h",
        ],
        "queries": [
            "tracking down what exactly was hogging all my storage when the drive filled up",
            "hunting the culprit files that ate the free space on my machine",
        ],
    },
    {
        "topic": "systemd-debug",
        "id": "systemd_service_debug",
        "cwd": "~",
        "commands": [
            "systemctl status myapp",
            "journalctl -u myapp -n 100 --no-pager",
            "sudo systemctl restart myapp",
            "systemctl status myapp",
        ],
        "queries": [
            "why a background service kept dying right after it started at boot",
            "chasing a daemon that just would not stay running",
        ],
    },
    # ===================== MISC POWER TOOLS =====================
    {
        "topic": "tar-archive",
        "id": "tar_backup",
        "cwd": "~/projects",
        "commands": [
            "tar czf backup.tar.gz webapp/",
            "ls -lh backup.tar.gz",
            "tar tzf backup.tar.gz | head",
        ],
        "queries": [
            "bundling an entire folder into a single compressed file to move it elsewhere",
            "packing up a directory into one archive for safekeeping",
        ],
    },
    {
        "topic": "kubectl-debug",
        "id": "kubectl_pod_debug",
        "cwd": "~/projects/infra",
        "commands": [
            "kubectl get pods",
            "kubectl describe pod api-7f9",
            "kubectl logs api-7f9 --previous",
            "kubectl rollout restart deploy/api",
        ],
        "queries": [
            "figuring out why a workload kept restarting over and over in the cluster",
            "chasing a crashing container managed by the orchestrator",
        ],
    },
    {
        "topic": "rsync-sync",
        "id": "rsync_transfer",
        "cwd": "~",
        "commands": [
            "rsync -avz --dry-run ./site/ user@host:/var/www/site/",
            "rsync -avz ./site/ user@host:/var/www/site/",
            "ssh user@host ls /var/www/site",
        ],
        "queries": [
            "mirroring a directory up to a remote server while only sending what changed",
            "efficiently copying just the modified files over to another machine",
        ],
    },
    {
        "topic": "sed-replace",
        "id": "find_replace_sed",
        "cwd": "~/projects/api",
        "commands": [
            "grep -rn 'old_api_url' src/",
            "grep -rl 'old_api_url' src/ | xargs sed -i 's/old_api_url/new_api_url/g'",
            "grep -rn 'new_api_url' src/",
        ],
        "queries": [
            "renaming one identifier across every file in the project in a single sweep",
            "doing a bulk text swap through a whole codebase at once",
        ],
    },
    {
        "topic": "env-path",
        "id": "env_var_debug",
        "cwd": "~",
        "commands": [
            "which mytool",
            "echo $PATH",
            "vim ~/.bashrc",
            "source ~/.bashrc",
            "which mytool",
        ],
        "queries": [
            "when a program wasn't being found until I fixed where the shell looks for it",
            "getting an environment setting to stick around across new terminal sessions",
        ],
    },
    {
        "topic": "postgres-conn",
        "id": "postgres_connection_refused",
        "cwd": "/etc/postgresql/15/main",
        "commands": [
            "psql -U app -h localhost -d appdb",
            "sudo vim pg_hba.conf",
            "sudo systemctl restart postgresql",
            "psql -U app -h localhost -d appdb -c 'select 1'",
        ],
        "queries": [
            "when my app couldn't reach the database and kept getting turned away at the door",
            "sorting out the data store refusing my local connections until I edited who was allowed in",
        ],
    },
    {
        "topic": "port-kill",
        "id": "kill_process_on_port",
        "cwd": "~/projects/webapp",
        "commands": [
            "lsof -i :3000",
            "kill -9 48213",
            "lsof -i :3000",
            "npm run dev",
        ],
        "queries": [
            "when something was already squatting on the address my server needed and I had to evict it",
            "freeing up a busy network endpoint that a leftover process was still holding",
        ],
    },
    {
        "topic": "curl-debug",
        "id": "curl_api_debug",
        "cwd": "~/projects/api",
        "commands": [
            "curl -v https://api.example.com/health",
            "curl -s https://api.example.com/users | jq '.[0]'",
            "curl -X POST https://api.example.com/login -d '{}' -H 'Content-Type: application/json'",
        ],
        "queries": [
            "poking at a web endpoint by hand to see what it was actually sending back",
            "inspecting the raw reply from a remote service while it was misbehaving",
        ],
    },
    {
        "topic": "tmux",
        "id": "tmux_session",
        "cwd": "~",
        "commands": [
            "tmux new -s work",
            "tmux ls",
            "tmux attach -t work",
        ],
        "queries": [
            "keeping my remote work alive so it survived me getting disconnected",
            "getting back into the exact same terminal workspace after logging out",
        ],
    },
    {
        "topic": "find-files",
        "id": "find_large_old_files",
        "cwd": "~",
        "commands": [
            "find . -type f -size +100M",
            "find /var -type f -mtime +90",
            "find . -name '*.tmp' -delete",
        ],
        "queries": [
            "locating files by how big or how old they were across a whole tree",
            "tracking down specific files buried deep somewhere in a directory",
        ],
    },
    {
        "topic": "gpg-encrypt",
        "id": "gpg_encrypt_file",
        "cwd": "~/documents",
        "commands": [
            "gpg -c secret.txt",
            "shred -u secret.txt",
            "gpg -d secret.txt.gpg",
        ],
        "queries": [
            "locking a sensitive document behind a passphrase before handing it off",
            "scrambling a file so only someone with the secret word could read it",
        ],
    },
]

# ---------------------------------------------------------------------------
# Null queries: their topic is deliberately ABSENT from the corpus, so the
# correct behaviour is to surface nothing confident. Used for false-positive
# analysis (Step 4), not for precision/recall aggregates.
# ---------------------------------------------------------------------------

NULL_QUERIES = [
    ("when I set up the jenkins continuous integration pipeline", "ci-absent"),
    ("configuring terraform to provision cloud infrastructure", "iac-absent"),
    ("that time I fought the rust compiler's borrow checker", "rust-absent"),
    ("tuning the elasticsearch cluster shard allocation", "search-absent"),
    ("setting up the redis pub sub messaging channels", "redis-absent"),
    ("writing the ansible playbook to configure the fleet", "ansible-absent"),
    ("debugging the graphql resolver n plus one queries", "graphql-absent"),
    ("enabling two factor authentication on my account", "2fa-absent"),
    ("training the neural network on the gpu cluster", "ml-absent"),
    ("configuring the bluetooth audio device pairing", "bt-absent"),
]

# ---------------------------------------------------------------------------
# Distractor sessions: assembled from REAL commands sampled from the public
# datasets (eval/raw_sources), grouped under generic working directories. No
# query is expected to match these; they exist to add realistic index noise.
# ---------------------------------------------------------------------------

_DISTRACTOR_DIRS = ["~/work", "~/tmp", "~/sandbox", "/opt/app", "~/scratch"]
N_DISTRACTORS = 14


def _load_real_commands() -> list:
    if not RAW_EMIR.exists():
        return []
    lines = [ln.strip() for ln in RAW_EMIR.read_text().splitlines() if ln.strip()]
    # Keep multi-token, non-trivial commands only.
    return [ln for ln in lines if " " in ln and 4 <= len(ln) <= 120]


def build_distractors(rng: random.Random) -> list:
    pool = _load_real_commands()
    sessions = []
    if not pool:
        return sessions
    for i in range(N_DISTRACTORS):
        n = rng.randint(4, 7)
        cmds = rng.sample(pool, n)
        sessions.append(
            {
                "session_id": f"distractor_{i:02d}",
                "topic": "distractor",
                "cwd": rng.choice(_DISTRACTOR_DIRS),
                "commands": cmds,
            }
        )
    return sessions


def main() -> None:
    rng = random.Random(1234)

    sessions = []
    queries = []

    for s in TOPIC_SESSIONS:
        sessions.append(
            {
                "session_id": s["id"],
                "topic": s["topic"],
                "cwd": s["cwd"],
                "commands": s["commands"],
            }
        )
        for q in s["queries"]:
            queries.append(
                {"query": q, "correct_session_id": s["id"], "topic": s["topic"]}
            )

    # Distractor sessions (real-command noise), interleaved into the corpus.
    sessions.extend(build_distractors(rng))

    # Null / no-answer queries.
    for q, topic in NULL_QUERIES:
        queries.append({"query": q, "correct_session_id": None, "topic": topic})

    sessions_path = EVAL_DIR / "sessions.jsonl"
    queries_path = EVAL_DIR / "queries.jsonl"
    with sessions_path.open("w") as f:
        for row in sessions:
            f.write(json.dumps(row) + "\n")
    with queries_path.open("w") as f:
        for row in queries:
            f.write(json.dumps(row) + "\n")

    n_labeled = sum(1 for s in sessions if s["topic"] != "distractor")
    n_distract = sum(1 for s in sessions if s["topic"] == "distractor")
    n_answerable = sum(1 for q in queries if q["correct_session_id"] is not None)
    n_null = sum(1 for q in queries if q["correct_session_id"] is None)
    topics = sorted({s["topic"] for s in sessions if s["topic"] != "distractor"})
    print(f"sessions: {len(sessions)} ({n_labeled} labeled + {n_distract} distractor)")
    print(f"topics: {len(topics)} -> {topics}")
    print(f"queries: {len(queries)} ({n_answerable} answerable + {n_null} null)")
    print(f"wrote {sessions_path}")
    print(f"wrote {queries_path}")


if __name__ == "__main__":
    main()
