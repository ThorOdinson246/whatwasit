# Eval tables (auto-generated)

Corpus: 57 sessions (43 labeled + 14 distractor). Queries: 86 answerable + 10 null. Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).


## Aggregate: semantic vs keyword

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 0.279 | 0.198 | 0.163 | 0.814 | 0.930 | 0.480 | 0.545 |
| keyword | 0.291 | 0.155 | 0.112 | 0.558 | 0.698 | 0.415 | 0.427 |

## Per-topic (semantic / keyword)

| Topic | n | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|--:|---:|---:|---:|---:|---:|---:|---:|
| cron-debug (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| cron-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.15 | 0.00 |
| cron-setup (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.15 | 0.00 |
| cron-setup (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| curl-debug (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.25 | 0.25 |
| curl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| db-migrate-down (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| db-migrate-down (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.31 | 0.32 |
| db-migrate-up (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.29 | 0.47 |
| db-migrate-up (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| disk-cleanup (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| disk-cleanup (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| dns-flush (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| dns-flush (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.55 | 0.50 |
| dns-resolve (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| dns-resolve (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| docker-cleanup (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 1.00 | 0.21 | 0.22 |
| docker-cleanup (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| docker-compose (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| docker-compose (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| docker-networking (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.25 | 0.25 |
| docker-networking (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| docker-volumes (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.33 | 0.50 |
| docker-volumes (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| env-path (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| env-path (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.00 |
| find-files (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.29 | 0.32 |
| find-files (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| git-history-scrub (sem) | 2 | 0.00 | 0.00 | 0.20 | 1.00 | 1.00 | 0.23 | 0.41 |
| git-history-scrub (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.53 | 0.50 |
| git-merge (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.19 |
| git-merge (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| git-rebase (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.21 | 0.25 |
| git-rebase (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| git-undo (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| git-undo (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| gpg-encrypt (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| gpg-encrypt (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| kubectl-debug (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| kubectl-debug (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-parse (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| log-parse (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| log-rotate (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| log-rotate (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.53 | 0.50 |
| nginx-proxy (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 1.00 | 0.17 | 0.19 |
| nginx-proxy (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| nginx-ssl (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| nginx-ssl (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| npm-audit (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-audit (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| npm-cache (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-cache (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| npm-deps (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-deps (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| perm-chmod (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.33 | 0.50 |
| perm-chmod (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| perm-ownership (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.29 | 0.47 |
| perm-ownership (kw) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.27 | 0.44 |
| port-kill (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| port-kill (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| postgres-conn (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| postgres-conn (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| python-depconflict (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| python-depconflict (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.27 | 0.32 |
| python-import (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| python-import (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| python-profiling (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.15 | 0.22 |
| python-profiling (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| python-venv (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| python-venv (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.26 | 0.32 |
| rsync-sync (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.15 | 0.19 |
| rsync-sync (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| sed-replace (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| sed-replace (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-agent (sem) | 2 | 0.00 | 0.00 | 0.20 | 1.00 | 1.00 | 0.23 | 0.41 |
| ssh-agent (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| ssh-denied (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.56 | 0.50 |
| ssh-denied (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 1.00 | 0.17 | 0.19 |
| ssh-keys (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.27 | 0.44 |
| ssh-keys (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| systemd-debug (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| systemd-debug (kw) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| tar-archive (sem) | 2 | 0.00 | 0.00 | 0.20 | 1.00 | 1.00 | 0.20 | 0.39 |
| tar-archive (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| tmux (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| tmux (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |

## Per-query (answerable): semantic rank & top-3 vs keyword rank

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| that time I was replaying my commits on top of the latest upstream ... | git_rebase_conflict | 3 | git_undo_commit:0.0296<br>db_migration_rollback:0.0291<br>git_rebase_conflict:0.0287 | 10 |
| when I had to redo my branch history one commit at a time because o... | git_rebase_conflict | 11 | distractor_04:0.0301<br>distractor_07:0.0293<br>git_undo_commit:0.0292 | 29 |
| sorting out the mess when pulling a teammate's work collided with m... | git_merge_conflict | 5 | tmux_session:0.0318<br>distractor_03:0.0311<br>distractor_08:0.0301 | 16 |
| combining two lines of work where the same file got edited on both ... | git_merge_conflict | 13 | distractor_08:0.0318<br>distractor_03:0.0313<br>distractor_06:0.0302 | 41 |
| the time I had to walk back a change I'd already saved into the pro... | git_undo_commit | 2 | db_migration_rollback:0.0295<br>git_undo_commit:0.0294<br>db_migration_run:0.029 | 3 |
| digging through the record of what I did to get back to an earlier ... | git_undo_commit | 1 | git_undo_commit:0.0296<br>distractor_03:0.0296<br>db_migration_rollback:0.0291 | 17 |
| when I accidentally checked in something that should never have bee... | git_large_file_purge | 5 | git_undo_commit:0.0297<br>npm_audit_fix:0.0293<br>db_migration_rollback:0.0289 | 1 |
| purging a sensitive file out of the entire project history everywhere | git_large_file_purge | 4 | distractor_04:0.0299<br>find_large_old_files:0.0294<br>distractor_03:0.0292 | 18 |
| why my container kept losing everything every time it restarted | docker_volume_mount | 3 | docker_disk_prune:0.3347<br>systemd_service_debug:0.3222<br>docker_volume_mount:0.2923 | 5 |
| making the data inside a container actually survive between runs | docker_volume_mount | 3 | distractor_12:0.0315<br>distractor_02:0.0299<br>docker_volume_mount:0.0296 | 1 |
| when two of my services couldn't reach each other until I wired the... | docker_network_connect | 6 | dns_cache_flush:0.2214<br>systemd_service_debug:0.2125<br>docker_compose_stack:0.1899 | 30 |
| the container-to-container connectivity thing I had to set up | docker_network_connect | 3 | docker_compose_stack:0.0318<br>distractor_12:0.0306<br>docker_network_connect:0.0296 | 3 |
| spinning up the whole multi-service stack from a single definition | docker_compose_stack | 1 | docker_compose_stack:0.032<br>kill_process_on_port:0.0293<br>docker_network_connect:0.0289 | 1 |
| bringing all the pieces of the app online at once | docker_compose_stack | 6 | distractor_01:0.032<br>distractor_03:0.0303<br>distractor_12:0.0301 | 4 |
| reclaiming the disk space eaten up by old images and dangling layers | docker_disk_prune | 6 | distractor_12:0.0307<br>find_large_old_files:0.0296<br>disk_space_cleanup:0.0291 | 1 |
| cleaning out all the leftover junk the containers piled up | docker_disk_prune | 4 | docker_compose_stack:0.0313<br>distractor_12:0.0298<br>disk_space_cleanup:0.0296 | 53 |
| isolating a project's libraries so they don't pollute the whole system | python_venv_setup | 30 | distractor_13:0.0305<br>distractor_05:0.03<br>docker_disk_prune:0.0297 | 41 |
| setting up a clean sandbox for a fresh script's packages | python_venv_setup | 10 | npm_cache_clear:0.032<br>disk_space_cleanup:0.0311<br>distractor_13:0.0301 | 2 |
| when two libraries demanded incompatible versions of the same share... | python_dependency_conflict | 2 | npm_dependency_resolution:0.0297<br>python_dependency_conflict:0.0293<br>distractor_13:0.0293 | 27 |
| untangling the package version standoff that kept breaking my install | python_dependency_conflict | 2 | npm_dependency_resolution:0.0328<br>python_dependency_conflict:0.0315<br>python_venv_setup:0.0308 | 2 |
| chasing down why the interpreter swore a package wasn't there even ... | python_import_error | 1 | python_import_error:0.0297<br>npm_dependency_resolution:0.0293<br>python_dependency_conflict:0.0289 | 3 |
| that missing-module headache when running my code from the wrong place | python_import_error | 2 | npm_cache_clear:0.3472<br>python_import_error:0.2549<br>env_var_debug:0.244 | 16 |
| figuring out which part of my script was dragging the whole thing down | python_profiling | 24 | env_var_debug:0.0315<br>disk_space_cleanup:0.0293<br>log_parsing_grep:0.0289 | 53 |
| hunting the slow function that was eating all the runtime | python_profiling | 4 | find_large_old_files:0.0297<br>disk_space_cleanup:0.0293<br>kill_process_on_port:0.0289 | 1 |
| when the javascript package tree refused to install because require... | npm_dependency_resolution | 1 | npm_dependency_resolution:0.032<br>npm_cache_clear:0.0313<br>python_dependency_conflict:0.0301 | 6 |
| forcing through the node module knot where nothing agreed on versions | npm_dependency_resolution | 1 | npm_dependency_resolution:0.4422<br>npm_audit_fix:0.3463<br>npm_cache_clear:0.3387 | 1 |
| patching the flagged security holes in my node packages | npm_audit_fix | 2 | distractor_05:0.0304<br>npm_audit_fix:0.0297<br>npm_dependency_resolution:0.0293 | 1 |
| dealing with the reported vulnerabilities in my javascript dependen... | npm_audit_fix | 1 | npm_audit_fix:0.0297<br>npm_cache_clear:0.0293<br>npm_dependency_resolution:0.0289 | 3 |
| when a corrupted local package store gave me phantom build failures | npm_cache_clear | 1 | npm_cache_clear:0.3893<br>disk_space_cleanup:0.2907<br>npm_dependency_resolution:0.2879 | 4 |
| wiping the download cache to get rid of bizarre install errors | npm_cache_clear | 1 | npm_cache_clear:0.0325<br>distractor_01:0.0297<br>npm_dependency_resolution:0.0293 | 1 |
| setting up passwordless login so I'd stop typing my password to con... | ssh_key_setup | 5 | distractor_07:0.0323<br>distractor_04:0.032<br>distractor_11:0.0308 | 1 |
| the time I created credentials to get into a remote machine without... | ssh_key_setup | 3 | distractor_07:0.0303<br>distractor_08:0.0302<br>ssh_key_setup:0.0296 | 6 |
| making my local identity usable from a jump host to reach a machine... | ssh_agent_forwarding | 4 | distractor_01:0.0313<br>distractor_12:0.0305<br>distractor_08:0.0299 | 1 |
| when I needed my key to carry through to a second server down the line | ssh_agent_forwarding | 5 | distractor_08:0.031<br>ssh_permission_denied:0.0297<br>ssh_key_setup:0.0293 | 26 |
| why the remote box kept rejecting me even though I had the right key | ssh_permission_denied | 1 | ssh_permission_denied:0.0296<br>ssh_key_setup:0.0291<br>npm_cache_clear:0.0287 | 7 |
| troubleshooting getting locked out when logging into a server | ssh_permission_denied | 8 | systemd_service_debug:0.0297<br>postgres_connection_refused:0.0293<br>tmux_session:0.0289 | 5 |
| scheduling a script to run on its own every night | cron_job_setup | 7 | distractor_02:0.0308<br>distractor_07:0.0306<br>distractor_11:0.0306 | 32 |
| setting something up to fire automatically on a repeating timer | cron_job_setup | 6 | distractor_02:0.0302<br>distractor_07:0.0299<br>distractor_10:0.0299 | 1 |
| why my scheduled task silently never actually ran | cron_job_debug | 2 | cron_job_setup:0.4418<br>cron_job_debug:0.3206<br>distractor_02:0.1655 | 7 |
| chasing a background timer that just refused to trigger | cron_job_debug | 4 | distractor_07:0.0303<br>cron_job_setup:0.0297<br>distractor_11:0.0296 | 6 |
| rolling the database structure forward to the newest version | db_migration_run | 4 | distractor_01:0.0323<br>distractor_08:0.0311<br>db_migration_rollback:0.0297 | 3 |
| applying the pending schema changes to my tables | db_migration_run | 3 | distractor_08:0.0312<br>distractor_01:0.0299<br>db_migration_run:0.0297 | 2 |
| undoing a structural change to the database that broke everything | db_migration_rollback | 2 | distractor_01:0.0298<br>db_migration_rollback:0.0297<br>db_migration_run:0.0293 | 2 |
| walking the table layout back after a bad update | db_migration_rollback | 1 | db_migration_rollback:0.0297<br>disk_space_cleanup:0.0293<br>db_migration_run:0.0289 | 8 |
| when the system refused to run my script until I changed its access... | chmod_permission_error | 3 | distractor_02:0.0305<br>kill_process_on_port:0.0297<br>chmod_permission_error:0.0291 | 1 |
| fixing the you-are-not-allowed error trying to execute a file | chmod_permission_error | 3 | distractor_06:0.0306<br>distractor_03:0.0301<br>chmod_permission_error:0.0297 | 1 |
| reclaiming a bunch of files that ended up belonging to the wrong ac... | sudo_ownership_fix | 4 | distractor_03:0.0305<br>distractor_08:0.0301<br>git_undo_commit:0.0296 | 5 |
| when everything was locked because the superuser grabbed my directory | sudo_ownership_fix | 3 | chmod_permission_error:0.0313<br>distractor_03:0.031<br>sudo_ownership_fix:0.0309 | 3 |
| why a domain name just wouldn't resolve to an address on my machine | dns_debugging | 2 | dns_cache_flush:0.0297<br>dns_debugging:0.0293<br>postgres_connection_refused:0.0289 | 1 |
| chasing a name-lookup failure when trying to reach a site | dns_debugging | 2 | dns_cache_flush:0.0296<br>dns_debugging:0.0291<br>db_migration_rollback:0.0287 | 1 |
| when an old address kept sticking around long after it had changed | dns_cache_flush | 1 | dns_cache_flush:0.3253<br>db_migration_rollback:0.3142<br>db_migration_run:0.2761 | 10 |
| clearing the machine's memory of name lookups to pick up new records | dns_cache_flush | 2 | find_large_old_files:0.0292<br>dns_cache_flush:0.0288<br>distractor_01:0.0286 | 1 |
| that thing where the gateway wasn't picking up my configuration cha... | nginx_reverse_proxy | 5 | db_migration_rollback:0.2624<br>dns_cache_flush:0.214<br>db_migration_run:0.2079 | 45 |
| when the front server kept routing to the old backend after I edite... | nginx_reverse_proxy | 7 | db_migration_rollback:0.0297<br>npm_audit_fix:0.0293<br>npm_cache_clear:0.0289 | 32 |
| renewing the expiring secure certificate so the browser lock icon s... | nginx_ssl_cert | 1 | nginx_ssl_cert:0.3846<br>npm_cache_clear:0.2087<br>npm_audit_fix:0.1826 | 3 |
| sorting out the https warning visitors were seeing on my site | nginx_ssl_cert | 1 | nginx_ssl_cert:0.2683<br>npm_audit_fix:0.2009<br>log_parsing_grep:0.168 | 2 |
| digging through the web server records to tally how often requests ... | log_parsing_grep | 1 | log_parsing_grep:0.0294<br>dns_cache_flush:0.0289<br>cron_job_setup:0.0285 | 32 |
| slicing a big log file to count the recurring errors | log_parsing_grep | 4 | distractor_04:0.0315<br>distractor_00:0.0308<br>cron_job_setup:0.0296 | 16 |
| when runaway log files were quietly eating up all the disk | log_rotation | 1 | log_rotation:0.0313<br>cron_job_setup:0.0313<br>log_parsing_grep:0.0308 | 1 |
| keeping the ever-growing application output from filling storage | log_rotation | 3 | distractor_04:0.0315<br>distractor_12:0.0307<br>log_rotation:0.0296 | 20 |
| tracking down what exactly was hogging all my storage when the driv... | disk_space_cleanup | 1 | disk_space_cleanup:0.427<br>log_rotation:0.3951<br>find_large_old_files:0.3913 | 4 |
| hunting the culprit files that ate the free space on my machine | disk_space_cleanup | 2 | find_large_old_files:0.6416<br>disk_space_cleanup:0.5905<br>log_rotation:0.419 | 38 |
| why a background service kept dying right after it started at boot | systemd_service_debug | 1 | systemd_service_debug:0.388<br>kill_process_on_port:0.3383<br>nginx_reverse_proxy:0.2491 | 4 |
| chasing a daemon that just would not stay running | systemd_service_debug | 6 | kill_process_on_port:0.3134<br>cron_job_setup:0.2524<br>disk_space_cleanup:0.2282 | 2 |
| bundling an entire folder into a single compressed file to move it ... | tar_backup | 5 | distractor_06:0.0323<br>distractor_08:0.0311<br>distractor_04:0.0308 | 6 |
| packing up a directory into one archive for safekeeping | tar_backup | 5 | distractor_13:0.0315<br>distractor_06:0.031<br>distractor_05:0.0304 | 1 |
| figuring out why a workload kept restarting over and over in the cl... | kubectl_pod_debug | 1 | kubectl_pod_debug:0.0297<br>systemd_service_debug:0.0293<br>kill_process_on_port:0.0289 | 1 |
| chasing a crashing container managed by the orchestrator | kubectl_pod_debug | 3 | distractor_12:0.0298<br>docker_compose_stack:0.0297<br>kubectl_pod_debug:0.0293 | 1 |
| mirroring a directory up to a remote server while only sending what... | rsync_transfer | 11 | distractor_06:0.0323<br>distractor_08:0.0323<br>distractor_01:0.0308 | 4 |
| efficiently copying just the modified files over to another machine | rsync_transfer | 5 | distractor_08:0.0315<br>distractor_03:0.0313<br>distractor_06:0.0313 | 26 |
| renaming one identifier across every file in the project in a singl... | find_replace_sed | 5 | distractor_13:0.0323<br>distractor_04:0.0323<br>distractor_06:0.0303 | 2 |
| doing a bulk text swap through a whole codebase at once | find_replace_sed | 1 | find_replace_sed:0.2746<br>distractor_04:0.1938<br>db_migration_run:0.1618 | 1 |
| when a program wasn't being found until I fixed where the shell loo... | env_var_debug | 1 | env_var_debug:0.0297<br>python_import_error:0.0293<br>disk_space_cleanup:0.0289 | 8 |
| getting an environment setting to stick around across new terminal ... | env_var_debug | 3 | tmux_session:0.0325<br>distractor_07:0.0304<br>env_var_debug:0.0293 | 37 |
| when my app couldn't reach the database and kept getting turned awa... | postgres_connection_refused | 2 | distractor_01:0.0311<br>postgres_connection_refused:0.0298<br>systemd_service_debug:0.0294 | 21 |
| sorting out the data store refusing my local connections until I ed... | postgres_connection_refused | 3 | distractor_03:0.0306<br>docker_volume_mount:0.0302<br>postgres_connection_refused:0.0296 | 13 |
| when something was already squatting on the address my server neede... | kill_process_on_port | 5 | log_rotation:0.0297<br>npm_audit_fix:0.0293<br>distractor_12:0.029 | 15 |
| freeing up a busy network endpoint that a leftover process was stil... | kill_process_on_port | 1 | kill_process_on_port:0.4303<br>find_large_old_files:0.2261<br>disk_space_cleanup:0.2187 | 3 |
| poking at a web endpoint by hand to see what it was actually sendin... | curl_api_debug | 3 | kill_process_on_port:0.0296<br>nginx_reverse_proxy:0.0291<br>curl_api_debug:0.0287 | 8 |
| inspecting the raw reply from a remote service while it was misbeha... | curl_api_debug | 6 | nginx_reverse_proxy:0.0297<br>git_undo_commit:0.0293<br>kill_process_on_port:0.0289 | 46 |
| keeping my remote work alive so it survived me getting disconnected | tmux_session | 1 | tmux_session:0.0328<br>distractor_08:0.0308<br>distractor_07:0.0304 | 1 |
| getting back into the exact same terminal workspace after logging out | tmux_session | 1 | tmux_session:0.5695<br>git_undo_commit:0.2865<br>db_migration_rollback:0.2384 | 1 |
| locating files by how big or how old they were across a whole tree | find_large_old_files | 2 | log_parsing_grep:0.5476<br>find_large_old_files:0.5122<br>git_undo_commit:0.292 | 28 |
| tracking down specific files buried deep somewhere in a directory | find_large_old_files | 12 | distractor_04:0.0298<br>env_var_debug:0.0296<br>npm_audit_fix:0.0294 | 10 |
| locking a sensitive document behind a passphrase before handing it off | gpg_encrypt_file | 1 | gpg_encrypt_file:0.4467<br>distractor_07:0.1283<br>distractor_03:0.1227 | 1 |
| scrambling a file so only someone with the secret word could read it | gpg_encrypt_file | 5 | distractor_03:0.0323<br>distractor_08:0.0313<br>distractor_06:0.0312 | 1 |

## Null queries (no correct session): top-1 returned

| Query | Sem top-1 (id:score) | KW top-1 (id:score) |
|---|---|---|
| when I set up the jenkins continuous integration pipeline | docker_compose_stack:0.0328 | distractor_12:1.0036 |
| configuring terraform to provision cloud infrastructure | docker_compose_stack:0.149 | tmux_session:0.0258 |
| that time I fought the rust compiler's borrow checker | npm_audit_fix:0.2098 | kubectl_pod_debug:0.0295 |
| tuning the elasticsearch cluster shard allocation | kubectl_pod_debug:0.1729 | kubectl_pod_debug:1.0258 |
| setting up the redis pub sub messaging channels | docker_network_connect:0.0325 | docker_network_connect:1.0064 |
| writing the ansible playbook to configure the fleet | distractor_03:0.0323 | db_migration_run:0.027 |
| debugging the graphql resolver n plus one queries | dns_cache_flush:0.4019 | git_undo_commit:0.0284 |
| enabling two factor authentication on my account | ssh_key_setup:0.1857 | ssh_key_setup:1.0015 |
| training the neural network on the gpu cluster | gpg_encrypt_file:0.1778 | kubectl_pod_debug:1.0183 |
| configuring the bluetooth audio device pairing | distractor_10:0.0922 | env_var_debug:0.0254 |

## Keyword-heavy queries breakout (exact tool names / flags)

*15 queries using exact keywords from target sessions (opposite of the standard eval design). Reported separately — not merged into the answerable aggregate.*

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 1.000 | 0.333 | 0.200 | 1.000 | 1.000 | 1.000 | 1.000 |
| keyword | 0.933 | 0.333 | 0.200 | 1.000 | 1.000 | 0.967 | 0.975 |

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| cProfile pstats snakeviz profiling hotspot | python_profiling | 1 | python_profiling:0.0328<br>kill_process_on_port:0.0323<br>dns_debugging:0.0317 | 1 |
| python3 -m venv activate pip install requirements.txt | python_venv_setup | 1 | python_venv_setup:0.0328<br>python_dependency_conflict:0.032<br>python_import_error:0.032 | 1 |
| git filter-branch --force git rm --cached secrets.env reflog gc prune | git_large_file_purge | 1 | git_large_file_purge:0.0328<br>git_undo_commit:0.0323<br>git_merge_conflict:0.0306 | 1 |
| git rebase origin/main --force-with-lease conflict | git_rebase_conflict | 1 | git_rebase_conflict:0.0328<br>git_merge_conflict:0.0323<br>git_undo_commit:0.0315 | 1 |
| docker volume inspect pgdata postgres persist | docker_volume_mount | 1 | docker_volume_mount:0.0328<br>docker_disk_prune:0.032<br>postgres_connection_refused:0.0313 | 1 |
| alembic upgrade head revision migrate | db_migration_run | 1 | db_migration_run:0.0328<br>db_migration_rollback:0.0323<br>git_undo_commit:0.0315 | 1 |
| alembic downgrade revision rollback | db_migration_rollback | 1 | db_migration_rollback:0.0328<br>db_migration_run:0.0323<br>git_undo_commit:0.0317 | 1 |
| crontab -e cron.d */5 scheduled job | cron_job_setup | 1 | cron_job_setup:0.0328<br>cron_job_debug:0.0318<br>distractor_07:0.0306 | 1 |
| curl -v -s jq json api endpoint response | curl_api_debug | 1 | curl_api_debug:0.0328<br>nginx_reverse_proxy:0.0311<br>git_undo_commit:0.0305 | 1 |
| lsof -i kill -9 port 8080 process pid | kill_process_on_port | 1 | kill_process_on_port:0.0328<br>nginx_reverse_proxy:0.0315<br>disk_space_cleanup:0.0313 | 2 |
| tmux new-session attach-session detach | tmux_session | 1 | tmux_session:0.0328<br>find_large_old_files:0.0323<br>distractor_08:0.0317 | 1 |
| ssh-keygen authorized_keys ssh-copy-id id_rsa | ssh_key_setup | 1 | ssh_key_setup:0.0328<br>ssh_permission_denied:0.0323<br>ssh_agent_forwarding:0.0315 | 1 |
| gpg --symmetric --passphrase encrypt file decrypt | gpg_encrypt_file | 1 | gpg_encrypt_file:0.0328<br>distractor_03:0.0323<br>distractor_06:0.031 | 1 |
| resolvectl flush-caches dns nameserver resolv.conf | dns_cache_flush | 1 | dns_cache_flush:0.0328<br>dns_debugging:0.0323<br>disk_space_cleanup:0.0317 | 1 |
| tar czf archive.tar.gz compress extract directory | tar_backup | 1 | tar_backup:0.0328<br>distractor_01:0.032<br>gpg_encrypt_file:0.0288 | 1 |
