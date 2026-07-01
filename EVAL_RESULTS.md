# hist — Search Quality Evaluation (v1)

A measured, quantified answer to *"how good is `hist`'s semantic search, really?"*
using standard IR metrics on a purpose-built labeled dataset — and a head-to-head
against a keyword/fuzzy baseline on the identical data.

- **Model under test:** `all-MiniLM-L6-v2` (384-dim ONNX), the shipping embedder.
- **Search path under test:** `hist.search.search()` — the real production code,
  not a reimplementation.
- **Everything is offline.** No API was called to generate queries, run search,
  or judge relevance.
- **Reproduce:** `python eval/run_eval.py` (regenerate the set first with
  `python eval/build_dataset.py`).

All raw numbers cited here come from `eval/summary_v1.json`,
`eval/results_raw_v1.jsonl`, `eval/metrics_summary_v1.csv`, and
`eval/tables_v1.md`. This document is the human analysis on top of those.

---

## 1. Methodology

### Dataset (durable, versioned test assets)

- **`eval/sessions.jsonl`** — 57 indexed sessions: **43 hand-authored labeled
  sessions across 43 fine-grained topics** (clustering into ~15 families) **+ 14
  "distractor" sessions** assembled from *real* commands sampled from three public
  command datasets (`hrsvrn/linux-commands-dataset`, `hotal/linux_commands`,
  `emirkaanozdemr/bash_command_data_6K`; samples saved in `eval/raw_sources/`).
  Distractors add realistic index noise; no query is meant to match them.
- **`eval/queries.jsonl`** — 96 queries: **86 answerable** (each with exactly one
  correct `session_id`) **+ 10 null** (topic deliberately absent from the corpus,
  to test false positives).
- **Confusable-by-design.** The corpus includes 4 git flavors (rebase / merge /
  undo / history-scrub), 4 docker (volumes / networking / compose / cleanup), 4
  python (venv / dep-conflict / import / profiling), 3 npm, 3 ssh, etc. The eval
  therefore measures *discrimination between near-duplicate topics*, not just
  separation of unrelated ones.

### The hard constraint that makes this meaningful

Every recall query was written **fresh** to imitate how a person vaguely recalls
a past session weeks later, and **must not reuse the literal command words/flags**
of its target session. Example:

> Session `nginx_reverse_proxy` runs `sudo systemctl reload nginx`.
> Query: *"that thing where the gateway wasn't picking up my configuration
> changes"* — no "nginx", no "reload", no "systemctl".

This is the whole point: it tests **intent-based recall**, not keyword luck. The
public datasets' own natural-language descriptions were **not** reused as queries
(they are textbook command explanations, not vague human recall).

### Metrics (`eval/metrics.py`)

One relevant document per query, so: **P@1/3/5** (relevant-in-top-k / k),
**R@5/R@10** (found in top-k?), **MRR** (1/rank), **nDCG@5** (1/log2(rank+1),
IDCG=1). Aggregated overall and per-topic.

### Baseline (`eval/baseline.py`)

Keyword/substring/fuzzy over the **same** session documents: score = (# query
content-tokens occurring as substrings in the doc) + 0.1·difflib-ratio. Stopwords
and <3-char tokens removed to give the lexical baseline its fairest shot.

---

## 2. Headline results

Aggregate over the **86 answerable** queries:

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **semantic** | **0.384** | **0.240** | **0.165** | **0.826** | **0.919** | **0.577** | **0.626** |
| keyword | 0.070 | 0.070 | 0.056 | 0.279 | 0.372 | 0.178 | 0.176 |

Interpreted (single relevant doc, so P@3·3 = top-3 hit rate, P@5·5 = R@5):

| Question | Semantic | Keyword |
|---|---:|---:|
| Correct session is the #1 result | **38.4%** | 7.0% |
| Correct session in top 3 | **72.1%** | 20.9% |
| Correct session in top 5 (R@5) | **82.6%** | 27.9% |
| Correct session in top 10 (R@10) | **91.9%** | 37.2% |
| Mean reciprocal rank | **0.577** | 0.178 |

**Semantic beats keyword by 3–5x on every metric.** On a test set explicitly
built to defeat keyword matching, this is the quantified answer to "is this
actually better than fuzzy grep": yes, decisively. The keyword baseline finds the
right session in the top 10 only 37% of the time; semantic does 92%.

### Rank distribution (answerable queries, n=86)

| Rank of correct session | Semantic | Keyword |
|---|---:|---:|
| 1 | 33 | 6 |
| 2–3 | 29 | 12 |
| 4–5 | 9 | 6 |
| 6–10 | 8 | 8 |
| >10 (effectively not found) | 7 | 54 |

Semantic puts the answer on a 5-item screen for 72/86 queries and a 10-item
screen for 79/86. Keyword buries it past rank 10 for 54/86.

Per-topic numbers (all 43 topics, both methods) are in `eval/tables_v1.md` and
`eval/metrics_summary_v1.csv`. Topics where semantic scores a perfect MRR=1.0:
`gpg-encrypt`, `log-parse`, `log-rotate`, `nginx-ssl`, `npm-audit`, `perm-chmod`,
`ssh-denied`. Topics where it struggles (MRR < 0.2): `python-venv`,
`python-profiling`, `git-rebase`, `cron-setup` — analyzed below.

---

## 3. Full per-query results (semantic)

Every answerable query, its expected session, the semantic rank of the correct
answer, the semantic top-3 (id:score), and the keyword rank for comparison.
(`NF` = not found in ranking.)

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| that time I was replaying my commits on top of the latest upstream ... | git_rebase_conflict | 6 | git_undo_commit:0.42<br>git_large_file_purge:0.34<br>db_migration_rollback:0.28 | 5 |
| when I had to redo my branch history one commit at a time ... | git_rebase_conflict | 6 | git_large_file_purge:0.40<br>git_undo_commit:0.40<br>git_merge_conflict:0.36 | 21 |
| sorting out the mess when pulling a teammate's work collided ... | git_merge_conflict | 2 | distractor_08:0.22<br>git_merge_conflict:0.21<br>tmux_session:0.19 | 19 |
| combining two lines of work where the same file got edited ... | git_merge_conflict | 15 | distractor_09:0.34<br>distractor_08:0.28<br>distractor_00:0.26 | 50 |
| the time I had to walk back a change I'd already saved ... | git_undo_commit | 3 | db_migration_rollback:0.35<br>db_migration_run:0.33<br>git_undo_commit:0.29 | 23 |
| digging through the record of what I did to get back to an earlier ... | git_undo_commit | 4 | db_migration_rollback:0.31<br>db_migration_run:0.29<br>systemd_service_debug:0.27 | 2 |
| when I accidentally checked in something that should never ... | git_large_file_purge | 5 | npm_audit_fix:0.31<br>db_migration_rollback:0.30<br>git_undo_commit:0.28 | 57 |
| purging a sensitive file out of the entire project history everywhere | git_large_file_purge | 2 | find_large_old_files:0.45<br>git_large_file_purge:0.42<br>gpg_encrypt_file:0.41 | 56 |
| why my container kept losing everything every time it restarted | docker_volume_mount | 3 | systemd_service_debug:0.33<br>docker_disk_prune:0.26<br>docker_volume_mount:0.26 | 56 |
| making the data inside a container actually survive between runs | docker_volume_mount | 1 | docker_volume_mount:0.23<br>distractor_12:0.22<br>docker_disk_prune:0.18 | 3 |
| when two of my services couldn't reach each other ... | docker_network_connect | 3 | dns_cache_flush:0.23<br>systemd_service_debug:0.19<br>docker_network_connect:0.16 | 25 |
| the container-to-container connectivity thing I had to set up | docker_network_connect | 1 | docker_network_connect:0.35<br>docker_compose_stack:0.32<br>docker_volume_mount:0.26 | 32 |
| spinning up the whole multi-service stack from a single definition | docker_compose_stack | 2 | docker_network_connect:0.20<br>docker_compose_stack:0.13<br>dns_cache_flush:0.13 | 33 |
| bringing all the pieces of the app online at once | docker_compose_stack | 6 | distractor_01:0.28<br>distractor_12:0.24<br>docker_network_connect:0.23 | 4 |
| reclaiming the disk space eaten up by old images ... | docker_disk_prune | 2 | find_large_old_files:0.32<br>docker_disk_prune:0.31<br>disk_space_cleanup:0.27 | 20 |
| cleaning out all the leftover junk the containers piled up | docker_disk_prune | 2 | disk_space_cleanup:0.29<br>docker_disk_prune:0.28<br>docker_volume_mount:0.26 | 7 |
| isolating a project's libraries so they don't pollute the whole system | python_venv_setup | 39 | sudo_ownership_fix:0.23<br>disk_space_cleanup:0.21<br>distractor_13:0.20 | 37 |
| setting up a clean sandbox for a fresh script's packages | python_venv_setup | 15 | distractor_00:0.36<br>npm_cache_clear:0.33<br>npm_dependency_resolution:0.31 | 27 |
| when two libraries demanded incompatible versions ... | python_dependency_conflict | 3 | db_migration_rollback:0.23<br>db_migration_run:0.21<br>python_dependency_conflict:0.20 | 20 |
| untangling the package version standoff that kept breaking my install | python_dependency_conflict | 5 | db_migration_rollback:0.29<br>disk_space_cleanup:0.23<br>npm_dependency_resolution:0.22 | 5 |
| chasing down why the interpreter swore a package wasn't there ... | python_import_error | 1 | python_import_error:0.35<br>npm_dependency_resolution:0.32<br>python_dependency_conflict:0.31 | 10 |
| that missing-module headache when running my code from the wrong place | python_import_error | 3 | npm_cache_clear:0.33<br>python_profiling:0.28<br>python_import_error:0.21 | 27 |
| figuring out which part of my script was dragging the whole thing down | python_profiling | 17 | chmod_permission_error:0.27<br>log_parsing_grep:0.22<br>env_var_debug:0.21 | 9 |
| hunting the slow function that was eating all the runtime | python_profiling | 9 | find_large_old_files:0.28<br>disk_space_cleanup:0.23<br>log_rotation:0.21 | 24 |
| when the javascript package tree refused to install ... | npm_dependency_resolution | 1 | npm_dependency_resolution:0.40<br>npm_cache_clear:0.34<br>npm_audit_fix:0.20 | 2 |
| forcing through the node module knot where nothing agreed on versions | npm_dependency_resolution | 2 | npm_cache_clear:0.36<br>npm_dependency_resolution:0.33<br>npm_audit_fix:0.27 | 1 |
| patching the flagged security holes in my node packages | npm_audit_fix | 1 | npm_audit_fix:0.36<br>npm_dependency_resolution:0.33<br>npm_cache_clear:0.31 | 20 |
| dealing with the reported vulnerabilities in my javascript ... | npm_audit_fix | 1 | npm_audit_fix:0.28<br>npm_dependency_resolution:0.22<br>npm_cache_clear:0.20 | 28 |
| when a corrupted local package store gave me phantom build failures | npm_cache_clear | 1 | npm_cache_clear:0.32<br>npm_dependency_resolution:0.28<br>systemd_service_debug:0.24 | 11 |
| wiping the download cache to get rid of bizarre install errors | npm_cache_clear | 2 | disk_space_cleanup:0.34<br>npm_cache_clear:0.28<br>dns_cache_flush:0.23 | 1 |
| setting up passwordless login so I'd stop typing my password ... | ssh_key_setup | 2 | distractor_07:0.24<br>ssh_key_setup:0.14<br>ssh_permission_denied:0.13 | 11 |
| the time I created credentials to get into a remote machine ... | ssh_key_setup | 1 | ssh_key_setup:0.32<br>distractor_07:0.30<br>ssh_permission_denied:0.29 | 44 |
| making my local identity usable from a jump host ... | ssh_agent_forwarding | 1 | ssh_agent_forwarding:0.22<br>ssh_key_setup:0.22<br>distractor_01:0.13 | 3 |
| when I needed my key to carry through to a second server ... | ssh_agent_forwarding | 4 | ssh_permission_denied:0.36<br>ssh_key_setup:0.35<br>distractor_08:0.17 | 22 |
| why the remote box kept rejecting me even though I had the right key | ssh_permission_denied | 1 | ssh_permission_denied:0.22<br>ssh_key_setup:0.19<br>nginx_ssl_cert:0.12 | 1 |
| troubleshooting getting locked out when logging into a server | ssh_permission_denied | 1 | ssh_permission_denied:0.15<br>systemd_service_debug:0.15<br>ssh_key_setup:0.13 | 2 |
| scheduling a script to run on its own every night | cron_job_setup | 8 | distractor_02:0.58<br>distractor_07:0.41<br>cron_job_debug:0.40 | 32 |
| setting something up to fire automatically on a repeating timer | cron_job_setup | 12 | distractor_02:0.28<br>distractor_11:0.23<br>distractor_07:0.22 | 13 |
| why my scheduled task silently never actually ran | cron_job_debug | 1 | cron_job_debug:0.35<br>distractor_02:0.25<br>distractor_07:0.21 | 31 |
| chasing a background timer that just refused to trigger | cron_job_debug | 2 | distractor_11:0.23<br>cron_job_debug:0.23<br>distractor_02:0.21 | 7 |
| rolling the database structure forward to the newest version | db_migration_run | 2 | distractor_01:0.30<br>db_migration_run:0.25<br>db_migration_rollback:0.24 | 24 |
| applying the pending schema changes to my tables | db_migration_run | 3 | distractor_08:0.16<br>git_merge_conflict:0.14<br>db_migration_run:0.13 | 26 |
| undoing a structural change to the database that broke everything | db_migration_rollback | 2 | docker_volume_mount:0.25<br>db_migration_rollback:0.24<br>distractor_01:0.21 | 35 |
| walking the table layout back after a bad update | db_migration_rollback | 3 | disk_space_cleanup:0.19<br>systemd_service_debug:0.16<br>db_migration_rollback:0.15 | 11 |
| when the system refused to run my script until I changed its access ... | chmod_permission_error | 1 | chmod_permission_error:0.36<br>distractor_02:0.33<br>kill_process_on_port:0.23 | 5 |
| fixing the you-are-not-allowed error trying to execute a file | chmod_permission_error | 1 | chmod_permission_error:0.36<br>gpg_encrypt_file:0.24<br>distractor_06:0.23 | 27 |
| reclaiming a bunch of files that ended up belonging to the wrong ... | sudo_ownership_fix | 4 | gpg_encrypt_file:0.34<br>git_undo_commit:0.27<br>find_large_old_files:0.26 | 24 |
| when everything was locked because the superuser grabbed my directory | sudo_ownership_fix | 1 | sudo_ownership_fix:0.39<br>distractor_03:0.28<br>chmod_permission_error:0.26 | 3 |
| why a domain name just wouldn't resolve to an address on my machine | dns_debugging | 2 | dns_cache_flush:0.39<br>dns_debugging:0.36<br>nginx_ssl_cert:0.16 | 18 |
| chasing a name-lookup failure when trying to reach a site | dns_debugging | 2 | dns_cache_flush:0.31<br>dns_debugging:0.29<br>nginx_reverse_proxy:0.11 | 1 |
| when an old address kept sticking around long after it had changed | dns_cache_flush | 1 | dns_cache_flush:0.27<br>db_migration_run:0.25<br>db_migration_rollback:0.24 | 13 |
| clearing the machine's memory of name lookups to pick up new records | dns_cache_flush | 2 | find_large_old_files:0.29<br>dns_cache_flush:0.21<br>disk_space_cleanup:0.20 | 32 |
| that thing where the gateway wasn't picking up my configuration ... | nginx_reverse_proxy | 4 | dns_cache_flush:0.24<br>db_migration_rollback:0.15<br>systemd_service_debug:0.14 | 4 |
| when the front server kept routing to the old backend after I edited ... | nginx_reverse_proxy | 1 | nginx_reverse_proxy:0.24<br>dns_cache_flush:0.24<br>npm_cache_clear:0.24 | 33 |
| renewing the expiring secure certificate so the browser lock icon ... | nginx_ssl_cert | 1 | nginx_ssl_cert:0.44<br>dns_cache_flush:0.16<br>npm_cache_clear:0.15 | 36 |
| sorting out the https warning visitors were seeing on my site | nginx_ssl_cert | 1 | nginx_ssl_cert:0.31<br>log_parsing_grep:0.15<br>dns_cache_flush:0.12 | 2 |
| digging through the web server records to tally how often requests ... | log_parsing_grep | 1 | log_parsing_grep:0.36<br>dns_cache_flush:0.29<br>python_dependency_conflict:0.16 | 41 |
| slicing a big log file to count the recurring errors | log_parsing_grep | 1 | log_parsing_grep:0.51<br>distractor_00:0.42<br>log_rotation:0.39 | 10 |
| when runaway log files were quietly eating up all the disk | log_rotation | 1 | log_rotation:0.45<br>log_parsing_grep:0.36<br>cron_job_setup:0.33 | 3 |
| keeping the ever-growing application output from filling storage | log_rotation | 1 | log_rotation:0.30<br>distractor_04:0.24<br>docker_disk_prune:0.23 | 29 |
| tracking down what exactly was hogging all my storage ... | disk_space_cleanup | 1 | disk_space_cleanup:0.33<br>log_rotation:0.32<br>find_large_old_files:0.32 | 4 |
| hunting the culprit files that ate the free space on my machine | disk_space_cleanup | 2 | find_large_old_files:0.53<br>disk_space_cleanup:0.46<br>log_rotation:0.35 | 35 |
| why a background service kept dying right after it started at boot | systemd_service_debug | 1 | systemd_service_debug:0.25<br>kill_process_on_port:0.24<br>dns_cache_flush:0.23 | 3 |
| chasing a daemon that just would not stay running | systemd_service_debug | 22 | distractor_02:0.32<br>distractor_11:0.32<br>python_profiling:0.26 | 28 |
| bundling an entire folder into a single compressed file to move it ... | tar_backup | 7 | distractor_06:0.49<br>distractor_05:0.44<br>distractor_04:0.43 | 23 |
| packing up a directory into one archive for safekeeping | tar_backup | 3 | distractor_13:0.52<br>distractor_05:0.47<br>tar_backup:0.43 | 27 |
| figuring out why a workload kept restarting over and over in the ... | kubectl_pod_debug | 1 | kubectl_pod_debug:0.27<br>log_rotation:0.20<br>dns_cache_flush:0.18 | 10 |
| chasing a crashing container managed by the orchestrator | kubectl_pod_debug | 5 | docker_compose_stack:0.27<br>docker_disk_prune:0.27<br>docker_volume_mount:0.26 | 21 |
| mirroring a directory up to a remote server while only sending ... | rsync_transfer | 1 | rsync_transfer:0.45<br>distractor_08:0.42<br>distractor_02:0.33 | 37 |
| efficiently copying just the modified files over to another machine | rsync_transfer | 3 | distractor_08:0.46<br>distractor_09:0.38<br>rsync_transfer:0.36 | 33 |
| renaming one identifier across every file in the project in a single ... | find_replace_sed | 4 | distractor_13:0.30<br>distractor_09:0.26<br>distractor_00:0.26 | 35 |
| doing a bulk text swap through a whole codebase at once | find_replace_sed | 14 | distractor_04:0.21<br>distractor_09:0.21<br>distractor_07:0.17 | 14 |
| when a program wasn't being found until I fixed where the shell ... | env_var_debug | 1 | env_var_debug:0.32<br>docker_volume_mount:0.32<br>python_import_error:0.29 | 10 |
| getting an environment setting to stick around across new terminal ... | env_var_debug | 2 | distractor_07:0.34<br>env_var_debug:0.26<br>distractor_00:0.22 | 44 |
| when my app couldn't reach the database and kept getting turned away ... | postgres_connection_refused | 2 | systemd_service_debug:0.35<br>postgres_connection_refused:0.30<br>docker_volume_mount:0.26 | 3 |
| sorting out the data store refusing my local connections ... | postgres_connection_refused | 1 | postgres_connection_refused:0.25<br>dns_cache_flush:0.19<br>docker_volume_mount:0.17 | 3 |
| when something was already squatting on the address my server needed ... | kill_process_on_port | 5 | log_rotation:0.22<br>dns_cache_flush:0.20<br>nginx_ssl_cert:0.18 | 42 |
| freeing up a busy network endpoint that a leftover process was holding | kill_process_on_port | 1 | kill_process_on_port:0.26<br>find_large_old_files:0.19<br>disk_space_cleanup:0.17 | 24 |
| poking at a web endpoint by hand to see what it was actually sending ... | curl_api_debug | 2 | dns_cache_flush:0.16<br>curl_api_debug:0.16<br>kill_process_on_port:0.15 | 42 |
| inspecting the raw reply from a remote service while it was ... | curl_api_debug | 7 | dns_cache_flush:0.21<br>git_undo_commit:0.16<br>nginx_ssl_cert:0.16 | 37 |
| keeping my remote work alive so it survived me getting disconnected | tmux_session | 6 | distractor_07:0.22<br>distractor_11:0.22<br>distractor_02:0.17 | 1 |
| getting back into the exact same terminal workspace after logging out | tmux_session | 2 | distractor_07:0.28<br>tmux_session:0.27<br>git_undo_commit:0.24 | 2 |
| locating files by how big or how old they were across a whole tree | find_large_old_files | 2 | log_parsing_grep:0.49<br>find_large_old_files:0.42<br>distractor_00:0.27 | 31 |
| tracking down specific files buried deep somewhere in a directory | find_large_old_files | 1 | find_large_old_files:0.46<br>log_parsing_grep:0.44<br>gpg_encrypt_file:0.38 | 21 |
| locking a sensitive document behind a passphrase before handing it off | gpg_encrypt_file | 1 | gpg_encrypt_file:0.29<br>distractor_07:0.18<br>distractor_03:0.14 | 1 |
| scrambling a file so only someone with the secret word could read it | gpg_encrypt_file | 1 | gpg_encrypt_file:0.45<br>distractor_06:0.27<br>distractor_03:0.26 | 7 |

---

## 4. Error analysis — every top-3 miss

24 of 86 answerable queries (28%) did not land the correct session in the top 3.
Here is every one, what was returned at #1 instead, and the diagnosed failure mode.

| # | Query (short) | Expected | Rank | Returned #1 | Mode |
|--:|---|---|--:|---|---|
| 1 | replaying my commits on top of upstream, stopped halfway | git_rebase_conflict | 6 | git_undo_commit | B |
| 2 | redo my branch history one commit at a time | git_rebase_conflict | 6 | git_large_file_purge | B |
| 3 | pulling teammate's work collided with mine | git_merge_conflict | 15 | distractor_09 | A |
| 4 | walk back a change I'd already saved | git_undo_commit | 4 | db_migration_rollback | B |
| 5 | accidentally checked in something that shouldn't be tracked | git_large_file_purge | 5 | npm_audit_fix | C |
| 6 | bringing all the pieces of the app online at once | docker_compose_stack | 6 | distractor_01 | A |
| 7 | isolating a project's libraries from the system | python_venv_setup | 39 | sudo_ownership_fix | C |
| 8 | clean sandbox for a fresh script's packages | python_venv_setup | 15 | distractor_00 | A/C |
| 9 | package version standoff breaking my install | python_dependency_conflict | 5 | db_migration_rollback | B |
| 10 | which part of my script was dragging it down | python_profiling | 17 | chmod_permission_error | C |
| 11 | hunting the slow function eating the runtime | python_profiling | 9 | find_large_old_files | C |
| 12 | my key to carry through to a second server | ssh_agent_forwarding | 4 | ssh_permission_denied | B |
| 13 | schedule a script to run every night | cron_job_setup | 8 | distractor_02 | A |
| 14 | fire automatically on a repeating timer | cron_job_setup | 12 | distractor_02 | A |
| 15 | files that ended up belonging to the wrong account | sudo_ownership_fix | 4 | gpg_encrypt_file | C |
| 16 | gateway wasn't picking up my config changes | nginx_reverse_proxy | 4 | dns_cache_flush | B |
| 17 | a daemon that would not stay running | systemd_service_debug | 22 | distractor_02 | A |
| 18 | bundle a folder into a single compressed file | tar_backup | 7 | distractor_06 | A |
| 19 | crashing container managed by the orchestrator | kubectl_pod_debug | 5 | docker_compose_stack | B |
| 20 | rename one identifier across every file | find_replace_sed | 4 | distractor_13 | A |
| 21 | bulk text swap through a whole codebase | find_replace_sed | 14 | distractor_04 | A |
| 22 | something squatting on the address my server needed | kill_process_on_port | 5 | log_rotation | C |
| 23 | inspecting the raw reply from a remote service | curl_api_debug | 7 | dns_cache_flush | C |
| 24 | keeping my remote work alive after disconnect | tmux_session | 6 | distractor_07 | A |

### Mode A — distractor/noise domination (10 of 24)

The single biggest failure source. In 10 misses the #1 result is a **distractor
session** built from random real commands. These distractors are longer and more
lexically diverse than the tight 3–5 command target sessions, so they present a
larger semantic "surface" that catches vague queries. Worst example: *"schedule a
script to run every night"* → `distractor_02` at **0.58**, far above the true
`cron_job_debug` sibling at 0.40 and the true `cron_job_setup` down at rank 8.

**Hypothesis:** this is partly an artifact of the eval (real production history
has noise too, but not 25% synthetic-noise density), and partly a real signal that
**short, generic target sessions are out-competed by longer noisy ones**. A richer
`Session.to_document()` (see §7) would raise the target's own signal. It also
suggests document length normalization is worth investigating.

### Mode B — near-duplicate topic conflation (7 of 24)

The model retrieves a *semantically adjacent sibling* instead of the exact
session, because the intent genuinely overlaps:

- *"walk back a change I'd already saved"* → **`db_migration_rollback`** instead
  of `git_undo_commit`. "Undo" and "rollback" are near-synonyms; the model is
  arguably *correct about the intent* and wrong only about the tool.
- *"my key to carry through to a second server"* → `ssh_permission_denied` instead
  of `ssh_agent_forwarding` (both ssh-auth).
- *"crashing container managed by the orchestrator"* → `docker_compose_stack`
  instead of `kubectl_pod_debug` (both container orchestration).
- git rebase ↔ git undo ↔ git history-scrub cross-fire (#1, #2).

**Hypothesis:** MiniLM captures the *family* correctly but lacks the resolution to
separate fine-grained siblings that share vocabulary and intent. This is the
classic case an instruction-tuned asymmetric model (e5/bge) is designed to improve,
and where per-command vectors could disambiguate.

### Mode C — sparse / generic target document (7 of 24)

The target session's commands are so terse or generic that they carry little
semantic signal, and *everything* scores low (note the low absolute top scores):

- `python_venv_setup` (rank **39**): commands are `python3 -m venv .venv` /
  `source .venv/bin/activate` / `pip install` — generic setup with no distinctive
  intent tokens. The query "isolating libraries from the system" has essentially
  nothing to latch onto. This is the single worst query in the set.
- `python_profiling` (ranks 17, 9): `cProfile` / `pstats` / `snakeviz` are opaque
  tool names; "slow function dragging it down" doesn't embed near them.
- `curl_api_debug`, `kill_process_on_port`: short, and their vague queries
  ("inspecting the raw reply", "squatting on the address") are abstract.

**Hypothesis:** short command-only documents underperform. Enriching the embedded
document (expanded command names, man-page one-liners, inferred tags) would
directly help — a data problem more than a model problem.

---

## 5. False-positive analysis (null queries)

The 10 null queries have no correct session; a good system should return nothing
*confident*. `hist.search` always returns a ranked list (no abstain), so we analyze
the **top-1 score**.

| Null query | Semantic top-1 (id:score) | Keyword top-1 (id:score) |
|---|---|---|
| jenkins continuous integration pipeline | docker_compose_stack:0.27 | distractor_12:**1.00** |
| terraform provision cloud infrastructure | docker_network_connect:0.18 | npm_dependency_resolution:0.03 |
| rust compiler's borrow checker | distractor_13:0.13 | python_profiling:0.03 |
| elasticsearch cluster shard allocation | docker_disk_prune:0.16 | sudo_ownership_fix:0.03 |
| redis pub sub messaging channels | docker_network_connect:0.20 | docker_network_connect:**1.02** |
| ansible playbook to configure the fleet | distractor_13:0.20 | sudo_ownership_fix:0.03 |
| graphql resolver n plus one queries | dns_cache_flush:**0.39** | git_undo_commit:0.03 |
| two factor authentication on my account | ssh_permission_denied:0.15 | db_migration_run:0.04 |
| training the neural network on gpu cluster | gpg_encrypt_file:0.15 | docker_network_connect:**1.02** |
| bluetooth audio device pairing | distractor_10:0.15 | gpg_encrypt_file:0.03 |

**Semantic score distributions:** correct@1 answers have mean top-1 score **0.330**
(median 0.322); null queries have mean top-1 **0.198** (median 0.169). There is
useful separation, but it is **not clean** — one null query (graphql →
`dns_cache_flush`, 0.39) scores *above* the median correct answer.

**Threshold sweep** (semantic) — abstain if top-1 < T:

| T | Null false-positive rate | Legit correct@1 suppressed |
|--:|--:|--:|
| 0.25 | 20% | 15% |
| 0.30 | 10% | 36% |
| 0.35 | 10% | 58% |
| 0.40 | 0% | 79% |

**Takeaway:** no fixed similarity threshold cleanly separates real hits from
false positives — killing the last false positive (T≈0.40) would suppress ~79% of
genuine correct answers. A confidence gate is therefore *not* a free win at this
model's score resolution; it would need calibration or a better-separated model.

Interestingly the **keyword baseline is more dangerously overconfident**: a single
lexical collision produces a top-1 "score" >1.0 (e.g. "redis pub sub" → the
`docker_network_connect` session, which literally contains `redis:7`; "jenkins" →
a distractor). Keyword returns confident *wrong* answers; semantic at least keeps
null-query scores low in absolute terms.

---

## 6. Timing (captured, not the focus)

Per-query component timings (throttled dev CPU; see `BENCHMARKS.md` for the
hardware caveat):

| Stage | mean | p50 | p95 |
|---|--:|--:|--:|
| Query embed (encode_one) | 7.3 ms | 6.8 ms | 13.9 ms |
| ANN search (57 vectors) | 0.37 ms | 0.27 ms | 0.53 ms |
| Full `search()` call | 2303 ms | 2253 ms | 2880 ms |

The full-call figure is **not** representative of production: the eval calls
`search(k=57)` to obtain a complete ranking for R@10/MRR, which makes the
highlight step re-embed the commands of *all 57 returned sessions* every query, on
a thermally-throttled CPU. Real usage (`k=10`) embeds far fewer, and `BENCHMARKS.md`
measures the real query path at 153 ms avg on representative hardware. The
meaningful, size-independent costs here are the query embed (~7 ms) and ANN
(~0.3 ms).

---

## 7. Recommendation (Step 5 — recommend, don't decide)

### Is quality good enough to call the MVP "working as intended"? — **Yes.**

- Against a test set built specifically to defeat keyword matching, semantic search
  puts the right session **in the top 5 for 83%** and **top 10 for 92%** of
  queries, with **MRR 0.58**. The keyword baseline manages R@10 of 37% and MRR
  0.18. The core premise — *search your history by intent, not by remembering the
  command* — is validated with a **3–5x measured advantage** on every metric.
- `hist`'s UX shows a ranked list of sessions with highlighted commands, so the
  operative question is "is the right session on screen?", and the answer is
  yes 83–92% of the time. For an MVP, that is genuinely useful and honest to ship.

### Does it justify the e5/bge asymmetric-model swap flagged in FUTURE_IDEAS? — **Yes, as the #1 post-MVP experiment — but I recommend not building it yet, per your instruction.**

The evidence specifically points at what an asymmetric, instruction-tuned model is
built to fix:

- **P@1 is only 38%** and MRR 0.58 — the ceiling on both is set by Mode-B sibling
  conflation (rebase vs undo vs scrub; venv vs dep-conflict). Query/passage models
  with prefixes are designed to sharpen exactly this vague-query-vs-terse-document
  asymmetry.
- The score distributions overlap enough that **no reliable abstain threshold
  exists** today; a model with better-separated similarities would make a
  confidence gate viable and directly cut false positives.

**However**, two of the three failure modes are *not* model problems and are
cheaper to fix first:

1. **Mode C (sparse docs, 7 misses)** — enrich `Session.to_document()` (expanded
   command names / man-page one-liners / inferred tags). A data change, no model
   swap.
2. **Mode A (noise domination, 10 misses)** — investigate document-length
   normalization; partly a synthetic-eval artifact but worth confirming on real
   history.

### Recommended sequence (for your approval — nothing built yet)

1. **Ship the MVP as-is.** MiniLM clears the bar; the numbers are documented.
2. **First quality experiment:** the e5/bge swap (one-class change behind the
   `Embedder` ABC), measured by **re-running this exact harness** and comparing
   `metrics_summary_v2.csv` to v1. This is the clean, apples-to-apples payoff of
   having built the eval.
3. **In parallel, cheap wins:** richer session documents (Mode C) and
   length-normalization (Mode A), each re-scored against this set.

I have **not** implemented the model swap or any of the above changes, per your
instruction. Awaiting your go-ahead on which to pursue.

---

## 8. Artifacts (durable, versioned)

| File | Contents |
|---|---|
| `eval/queries.jsonl` | Ground truth: query, correct_session_id (or null), topic |
| `eval/sessions.jsonl` | The 57-session corpus (43 labeled + 14 distractor) |
| `eval/build_dataset.py` | Authoring source that regenerates the two JSONL assets |
| `eval/metrics.py` | IR metric implementations |
| `eval/baseline.py` | Keyword/substring/fuzzy baseline |
| `eval/run_eval.py` | Harness: index → run both methods → score → log |
| `eval/results_raw_v1.jsonl` | Full ranked list **with scores** + timings, every query, both methods |
| `eval/metrics_summary_v1.csv` | Aggregate + per-topic metrics, both methods |
| `eval/summary_v1.json` | Everything above in one structured file (for plots/reports) |
| `eval/tables_v1.md` | Auto-generated aggregate + per-topic + per-query tables |
| `eval/raw_sources/` | Samples of the three public command datasets (raw material) |

Re-running `python eval/run_eval.py` writes `*_v2.*` without overwriting v1, so
runs are comparable over time (e.g. after a model swap).
