# Eval tables (auto-generated)

Corpus: 57 sessions (43 labeled + 14 distractor). Queries: 86 answerable + 10 null. Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).


## Aggregate: semantic vs keyword

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 0.547 | 0.271 | 0.181 | 0.907 | 0.953 | 0.701 | 0.746 |
| keyword | 0.372 | 0.178 | 0.119 | 0.593 | 0.709 | 0.488 | 0.492 |

## Per-topic (semantic / keyword)

| Topic | n | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|--:|---:|---:|---:|---:|---:|---:|---:|
| cron-debug (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| cron-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.13 | 0.00 |
| cron-setup (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| cron-setup (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| curl-debug (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.12 | 0.00 |
| curl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| db-migrate-down (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| db-migrate-down (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.30 | 0.32 |
| db-migrate-up (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| db-migrate-up (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| disk-cleanup (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| disk-cleanup (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.11 | 0.19 |
| dns-flush (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| dns-flush (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.26 | 0.32 |
| dns-resolve (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| dns-resolve (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| docker-cleanup (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| docker-cleanup (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| docker-compose (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| docker-compose (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| docker-networking (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| docker-networking (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| docker-volumes (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| docker-volumes (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| env-path (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| env-path (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| find-files (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| find-files (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.33 | 0.32 |
| git-history-scrub (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| git-history-scrub (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| git-merge (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.57 | 0.50 |
| git-merge (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| git-rebase (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| git-rebase (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.00 |
| git-undo (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| git-undo (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.15 | 0.00 |
| gpg-encrypt (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpg-encrypt (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| kubectl-debug (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| kubectl-debug (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-parse (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-parse (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| log-rotate (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| log-rotate (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| nginx-proxy (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.11 | 0.00 |
| nginx-proxy (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.56 | 0.50 |
| nginx-ssl (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| nginx-ssl (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-audit (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-audit (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| npm-cache (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-cache (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-deps (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-deps (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| perm-chmod (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| perm-chmod (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| perm-ownership (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| perm-ownership (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.22 | 0.25 |
| port-kill (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| port-kill (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.19 | 0.25 |
| postgres-conn (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| postgres-conn (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| python-depconflict (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| python-depconflict (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.54 | 0.50 |
| python-import (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| python-import (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.27 | 0.32 |
| python-profiling (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.13 | 0.19 |
| python-profiling (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| python-venv (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| python-venv (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.54 | 0.50 |
| rsync-sync (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| rsync-sync (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.09 | 0.00 |
| sed-replace (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| sed-replace (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| ssh-agent (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| ssh-agent (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| ssh-denied (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| ssh-denied (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| ssh-keys (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-keys (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| systemd-debug (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| systemd-debug (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| tar-archive (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| tar-archive (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| tmux (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| tmux (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |

## Per-query (answerable): semantic rank & top-3 vs keyword rank

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| that time I was replaying my commits on top of the latest upstream ... | git_rebase_conflict | 2 | git_undo_commit:0.4261<br>git_rebase_conflict:0.3156<br>git_merge_conflict:0.2893 | 10 |
| when I had to redo my branch history one commit at a time because o... | git_rebase_conflict | 4 | git_undo_commit:0.5297<br>git_merge_conflict:0.4163<br>git_large_file_purge:0.368 | 15 |
| sorting out the mess when pulling a teammate's work collided with m... | git_merge_conflict | 1 | git_merge_conflict:0.2393<br>tmux_session:0.2231<br>git_undo_commit:0.2206 | 15 |
| combining two lines of work where the same file got edited on both ... | git_merge_conflict | 7 | git_undo_commit:0.2392<br>distractor_08:0.2193<br>find_replace_sed:0.1778 | 37 |
| the time I had to walk back a change I'd already saved into the pro... | git_undo_commit | 1 | git_undo_commit:0.4216<br>db_migration_rollback:0.3408<br>db_migration_run:0.2798 | 6 |
| digging through the record of what I did to get back to an earlier ... | git_undo_commit | 1 | git_undo_commit:0.3882<br>db_migration_rollback:0.2599<br>dns_cache_flush:0.2226 | 7 |
| when I accidentally checked in something that should never have bee... | git_large_file_purge | 2 | git_undo_commit:0.4312<br>git_large_file_purge:0.3035<br>disk_space_cleanup:0.2946 | 1 |
| purging a sensitive file out of the entire project history everywhere | git_large_file_purge | 1 | git_large_file_purge:0.3996<br>gpg_encrypt_file:0.3885<br>git_undo_commit:0.3805 | 29 |
| why my container kept losing everything every time it restarted | docker_volume_mount | 5 | systemd_service_debug:0.2487<br>docker_disk_prune:0.2467<br>npm_cache_clear:0.2075 | 6 |
| making the data inside a container actually survive between runs | docker_volume_mount | 1 | docker_volume_mount:0.1732<br>docker_disk_prune:0.1664<br>ssh_permission_denied:0.159 | 1 |
| when two of my services couldn't reach each other until I wired the... | docker_network_connect | 5 | dns_cache_flush:0.1944<br>tmux_session:0.1819<br>systemd_service_debug:0.1751 | 14 |
| the container-to-container connectivity thing I had to set up | docker_network_connect | 1 | docker_network_connect:0.3119<br>docker_compose_stack:0.2838<br>ssh_permission_denied:0.2094 | 3 |
| spinning up the whole multi-service stack from a single definition | docker_compose_stack | 1 | docker_compose_stack:0.3131<br>docker_network_connect:0.1372<br>tmux_session:0.1337 | 1 |
| bringing all the pieces of the app online at once | docker_compose_stack | 2 | distractor_01:0.2775<br>docker_compose_stack:0.1905<br>rsync_transfer:0.1799 | 4 |
| reclaiming the disk space eaten up by old images and dangling layers | docker_disk_prune | 3 | find_large_old_files:0.3012<br>disk_space_cleanup:0.2958<br>docker_disk_prune:0.2454 | 1 |
| cleaning out all the leftover junk the containers piled up | docker_disk_prune | 2 | disk_space_cleanup:0.3501<br>docker_disk_prune:0.2451<br>kill_process_on_port:0.1755 | 51 |
| isolating a project's libraries so they don't pollute the whole system | python_venv_setup | 28 | disk_space_cleanup:0.2772<br>kill_process_on_port:0.2323<br>npm_audit_fix:0.2146 | 14 |
| setting up a clean sandbox for a fresh script's packages | python_venv_setup | 9 | disk_space_cleanup:0.421<br>npm_audit_fix:0.3904<br>npm_cache_clear:0.342 | 1 |
| when two libraries demanded incompatible versions of the same share... | python_dependency_conflict | 2 | npm_dependency_resolution:0.271<br>python_dependency_conflict:0.2253<br>db_migration_rollback:0.2188 | 13 |
| untangling the package version standoff that kept breaking my install | python_dependency_conflict | 4 | disk_space_cleanup:0.3588<br>npm_dependency_resolution:0.3226<br>db_migration_rollback:0.2854 | 1 |
| chasing down why the interpreter swore a package wasn't there even ... | python_import_error | 1 | python_import_error:0.3835<br>disk_space_cleanup:0.3371<br>npm_dependency_resolution:0.3069 | 2 |
| that missing-module headache when running my code from the wrong place | python_import_error | 4 | npm_cache_clear:0.297<br>python_profiling:0.2435<br>npm_audit_fix:0.2222 | 25 |
| figuring out which part of my script was dragging the whole thing down | python_profiling | 16 | log_parsing_grep:0.2456<br>disk_space_cleanup:0.2404<br>git_undo_commit:0.2355 | 31 |
| hunting the slow function that was eating all the runtime | python_profiling | 5 | disk_space_cleanup:0.2413<br>log_parsing_grep:0.2348<br>find_large_old_files:0.2262 | 1 |
| when the javascript package tree refused to install because require... | npm_dependency_resolution | 1 | npm_dependency_resolution:0.4685<br>npm_cache_clear:0.4367<br>npm_audit_fix:0.3904 | 4 |
| forcing through the node module knot where nothing agreed on versions | npm_dependency_resolution | 1 | npm_dependency_resolution:0.3762<br>npm_audit_fix:0.2814<br>npm_cache_clear:0.2775 | 1 |
| patching the flagged security holes in my node packages | npm_audit_fix | 1 | npm_audit_fix:0.4186<br>npm_dependency_resolution:0.2749<br>disk_space_cleanup:0.2594 | 1 |
| dealing with the reported vulnerabilities in my javascript dependen... | npm_audit_fix | 1 | npm_audit_fix:0.4743<br>npm_cache_clear:0.3057<br>npm_dependency_resolution:0.2918 | 4 |
| when a corrupted local package store gave me phantom build failures | npm_cache_clear | 1 | npm_cache_clear:0.3377<br>disk_space_cleanup:0.2986<br>npm_dependency_resolution:0.2552 | 1 |
| wiping the download cache to get rid of bizarre install errors | npm_cache_clear | 2 | disk_space_cleanup:0.473<br>npm_cache_clear:0.2419<br>npm_dependency_resolution:0.1706 | 2 |
| setting up passwordless login so I'd stop typing my password to con... | ssh_key_setup | 1 | ssh_key_setup:0.1718<br>distractor_07:0.1594<br>ssh_permission_denied:0.1337 | 1 |
| the time I created credentials to get into a remote machine without... | ssh_key_setup | 2 | ssh_agent_forwarding:0.2802<br>ssh_key_setup:0.2753<br>distractor_07:0.2011 | 1 |
| making my local identity usable from a jump host to reach a machine... | ssh_agent_forwarding | 1 | ssh_agent_forwarding:0.3846<br>ssh_key_setup:0.1713<br>distractor_01:0.109 | 1 |
| when I needed my key to carry through to a second server down the line | ssh_agent_forwarding | 3 | ssh_permission_denied:0.2242<br>ssh_key_setup:0.2238<br>ssh_agent_forwarding:0.19 | 54 |
| why the remote box kept rejecting me even though I had the right key | ssh_permission_denied | 2 | ssh_key_setup:0.116<br>ssh_permission_denied:0.1094<br>npm_dependency_resolution:0.0859 | 1 |
| troubleshooting getting locked out when logging into a server | ssh_permission_denied | 4 | tmux_session:0.1516<br>systemd_service_debug:0.1463<br>log_parsing_grep:0.1461 | 4 |
| scheduling a script to run on its own every night | cron_job_setup | 1 | cron_job_setup:0.4498<br>distractor_02:0.3598<br>cron_job_debug:0.3413 | 36 |
| setting something up to fire automatically on a repeating timer | cron_job_setup | 1 | cron_job_setup:0.3121<br>distractor_02:0.1799<br>cron_job_debug:0.1664 | 1 |
| why my scheduled task silently never actually ran | cron_job_debug | 2 | cron_job_setup:0.3448<br>cron_job_debug:0.2529<br>distractor_10:0.1353 | 9 |
| chasing a background timer that just refused to trigger | cron_job_debug | 2 | cron_job_setup:0.2689<br>cron_job_debug:0.2336<br>distractor_02:0.1233 | 7 |
| rolling the database structure forward to the newest version | db_migration_run | 2 | db_migration_rollback:0.4082<br>db_migration_run:0.3454<br>distractor_01:0.2537 | 2 |
| applying the pending schema changes to my tables | db_migration_run | 1 | db_migration_run:0.258<br>db_migration_rollback:0.2489<br>git_merge_conflict:0.1625 | 2 |
| undoing a structural change to the database that broke everything | db_migration_rollback | 1 | db_migration_rollback:0.4077<br>db_migration_run:0.3311<br>git_undo_commit:0.3207 | 2 |
| walking the table layout back after a bad update | db_migration_rollback | 2 | disk_space_cleanup:0.2474<br>db_migration_rollback:0.2272<br>git_undo_commit:0.1885 | 11 |
| when the system refused to run my script until I changed its access... | chmod_permission_error | 1 | chmod_permission_error:0.4633<br>cron_job_debug:0.2916<br>sudo_ownership_fix:0.208 | 1 |
| fixing the you-are-not-allowed error trying to execute a file | chmod_permission_error | 1 | chmod_permission_error:0.4491<br>npm_cache_clear:0.239<br>cron_job_debug:0.2286 | 1 |
| reclaiming a bunch of files that ended up belonging to the wrong ac... | sudo_ownership_fix | 2 | git_undo_commit:0.36<br>sudo_ownership_fix:0.353<br>gpg_encrypt_file:0.2956 | 10 |
| when everything was locked because the superuser grabbed my directory | sudo_ownership_fix | 1 | sudo_ownership_fix:0.4443<br>ssh_permission_denied:0.2341<br>gpg_encrypt_file:0.2275 | 3 |
| why a domain name just wouldn't resolve to an address on my machine | dns_debugging | 2 | dns_cache_flush:0.4362<br>dns_debugging:0.4044<br>postgres_connection_refused:0.09 | 1 |
| chasing a name-lookup failure when trying to reach a site | dns_debugging | 1 | dns_debugging:0.3534<br>dns_cache_flush:0.3432<br>db_migration_run:0.0797 | 1 |
| when an old address kept sticking around long after it had changed | dns_cache_flush | 1 | dns_cache_flush:0.2489<br>db_migration_rollback:0.1941<br>git_undo_commit:0.1803 | 41 |
| clearing the machine's memory of name lookups to pick up new records | dns_cache_flush | 1 | dns_cache_flush:0.3106<br>disk_space_cleanup:0.2461<br>find_large_old_files:0.2242 | 2 |
| that thing where the gateway wasn't picking up my configuration cha... | nginx_reverse_proxy | 12 | db_migration_rollback:0.2412<br>db_migration_run:0.2024<br>dns_cache_flush:0.1722 | 1 |
| when the front server kept routing to the old backend after I edite... | nginx_reverse_proxy | 7 | npm_audit_fix:0.28<br>npm_cache_clear:0.2752<br>db_migration_rollback:0.248 | 9 |
| renewing the expiring secure certificate so the browser lock icon s... | nginx_ssl_cert | 1 | nginx_ssl_cert:0.2512<br>npm_dependency_resolution:0.152<br>npm_cache_clear:0.1417 | 2 |
| sorting out the https warning visitors were seeing on my site | nginx_ssl_cert | 1 | nginx_ssl_cert:0.1816<br>log_parsing_grep:0.1701<br>npm_audit_fix:0.1431 | 1 |
| digging through the web server records to tally how often requests ... | log_parsing_grep | 1 | log_parsing_grep:0.3886<br>dns_cache_flush:0.1699<br>cron_job_setup:0.1571 | 25 |
| slicing a big log file to count the recurring errors | log_parsing_grep | 1 | log_parsing_grep:0.5096<br>cron_job_setup:0.3802<br>log_rotation:0.3331 | 15 |
| when runaway log files were quietly eating up all the disk | log_rotation | 2 | log_parsing_grep:0.396<br>log_rotation:0.3616<br>find_large_old_files:0.2872 | 1 |
| keeping the ever-growing application output from filling storage | log_rotation | 1 | log_rotation:0.258<br>distractor_04:0.2453<br>docker_disk_prune:0.2324 | 57 |
| tracking down what exactly was hogging all my storage when the driv... | disk_space_cleanup | 1 | disk_space_cleanup:0.3186<br>find_large_old_files:0.3097<br>log_rotation:0.3017 | 5 |
| hunting the culprit files that ate the free space on my machine | disk_space_cleanup | 1 | disk_space_cleanup:0.5137<br>find_large_old_files:0.4781<br>log_parsing_grep:0.3543 | 36 |
| why a background service kept dying right after it started at boot | systemd_service_debug | 1 | systemd_service_debug:0.3149<br>kill_process_on_port:0.2232<br>docker_compose_stack:0.1464 | 1 |
| chasing a daemon that just would not stay running | systemd_service_debug | 3 | kill_process_on_port:0.2698<br>cron_job_setup:0.2582<br>systemd_service_debug:0.1997 | 3 |
| bundling an entire folder into a single compressed file to move it ... | tar_backup | 1 | tar_backup:0.4035<br>distractor_06:0.375<br>distractor_04:0.3428 | 2 |
| packing up a directory into one archive for safekeeping | tar_backup | 1 | tar_backup:0.4721<br>find_large_old_files:0.3371<br>distractor_13:0.3287 | 1 |
| figuring out why a workload kept restarting over and over in the cl... | kubectl_pod_debug | 1 | kubectl_pod_debug:0.2503<br>systemd_service_debug:0.2052<br>log_parsing_grep:0.1765 | 1 |
| chasing a crashing container managed by the orchestrator | kubectl_pod_debug | 2 | docker_compose_stack:0.3267<br>kubectl_pod_debug:0.2334<br>kill_process_on_port:0.2223 | 1 |
| mirroring a directory up to a remote server while only sending what... | rsync_transfer | 1 | rsync_transfer:0.5335<br>distractor_08:0.3176<br>git_undo_commit:0.2386 | 8 |
| efficiently copying just the modified files over to another machine | rsync_transfer | 1 | rsync_transfer:0.4184<br>distractor_08:0.3632<br>find_replace_sed:0.2635 | 19 |
| renaming one identifier across every file in the project in a singl... | find_replace_sed | 1 | find_replace_sed:0.3702<br>distractor_13:0.2009<br>distractor_08:0.187 | 1 |
| doing a bulk text swap through a whole codebase at once | find_replace_sed | 1 | find_replace_sed:0.2569<br>distractor_08:0.1582<br>distractor_04:0.1534 | 1 |
| when a program wasn't being found until I fixed where the shell loo... | env_var_debug | 1 | env_var_debug:0.2899<br>npm_audit_fix:0.2658<br>disk_space_cleanup:0.2649 | 3 |
| getting an environment setting to stick around across new terminal ... | env_var_debug | 3 | tmux_session:0.4302<br>distractor_07:0.2363<br>env_var_debug:0.2302 | 15 |
| when my app couldn't reach the database and kept getting turned awa... | postgres_connection_refused | 4 | systemd_service_debug:0.2665<br>db_migration_rollback:0.2508<br>distractor_01:0.2278 | 17 |
| sorting out the data store refusing my local connections until I ed... | postgres_connection_refused | 1 | postgres_connection_refused:0.22<br>dns_cache_flush:0.1245<br>ssh_permission_denied:0.1124 | 17 |
| when something was already squatting on the address my server neede... | kill_process_on_port | 3 | log_rotation:0.144<br>dns_cache_flush:0.1347<br>kill_process_on_port:0.1278 | 18 |
| freeing up a busy network endpoint that a leftover process was stil... | kill_process_on_port | 1 | kill_process_on_port:0.3474<br>disk_space_cleanup:0.2202<br>tmux_session:0.1857 | 3 |
| poking at a web endpoint by hand to see what it was actually sendin... | curl_api_debug | 11 | kill_process_on_port:0.2164<br>git_undo_commit:0.1826<br>npm_audit_fix:0.162 | 11 |
| inspecting the raw reply from a remote service while it was misbeha... | curl_api_debug | 7 | git_undo_commit:0.1793<br>nginx_ssl_cert:0.1402<br>systemd_service_debug:0.1346 | 39 |
| keeping my remote work alive so it survived me getting disconnected | tmux_session | 1 | tmux_session:0.2996<br>kill_process_on_port:0.1881<br>rsync_transfer:0.1553 | 1 |
| getting back into the exact same terminal workspace after logging out | tmux_session | 1 | tmux_session:0.5081<br>git_undo_commit:0.2865<br>db_migration_rollback:0.1992 | 1 |
| locating files by how big or how old they were across a whole tree | find_large_old_files | 2 | log_parsing_grep:0.4936<br>find_large_old_files:0.4126<br>git_undo_commit:0.292 | 2 |
| tracking down specific files buried deep somewhere in a directory | find_large_old_files | 2 | log_parsing_grep:0.4462<br>find_large_old_files:0.4345<br>disk_space_cleanup:0.3534 | 6 |
| locking a sensitive document behind a passphrase before handing it off | gpg_encrypt_file | 1 | gpg_encrypt_file:0.389<br>distractor_03:0.1174<br>distractor_07:0.1168 | 1 |
| scrambling a file so only someone with the secret word could read it | gpg_encrypt_file | 1 | gpg_encrypt_file:0.4404<br>distractor_03:0.2201<br>sudo_ownership_fix:0.1935 | 1 |

## Null queries (no correct session): top-1 returned

| Query | Sem top-1 (id:score) | KW top-1 (id:score) |
|---|---|---|
| when I set up the jenkins continuous integration pipeline | docker_compose_stack:0.2398 | distractor_12:1.0046 |
| configuring terraform to provision cloud infrastructure | git_merge_conflict:0.134 | db_migration_rollback:0.0223 |
| that time I fought the rust compiler's borrow checker | npm_audit_fix:0.1387 | git_merge_conflict:0.022 |
| tuning the elasticsearch cluster shard allocation | kubectl_pod_debug:0.1754 | kubectl_pod_debug:1.002 |
| setting up the redis pub sub messaging channels | tmux_session:0.136 | docker_network_connect:1.0046 |
| writing the ansible playbook to configure the fleet | docker_compose_stack:0.2024 | sudo_ownership_fix:0.0255 |
| debugging the graphql resolver n plus one queries | dns_cache_flush:0.372 | git_undo_commit:0.0284 |
| enabling two factor authentication on my account | ssh_agent_forwarding:0.1546 | postgres_connection_refused:1.0014 |
| training the neural network on the gpu cluster | gpg_encrypt_file:0.1416 | docker_network_connect:1.0041 |
| configuring the bluetooth audio device pairing | distractor_10:0.0972 | disk_space_cleanup:0.0236 |

## Keyword-heavy queries breakout (exact tool names / flags)

*15 queries using exact keywords from target sessions (opposite of the standard eval design). Reported separately — not merged into the answerable aggregate.*

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 0.933 | 0.333 | 0.200 | 1.000 | 1.000 | 0.967 | 0.975 |
| keyword | 0.933 | 0.333 | 0.200 | 1.000 | 1.000 | 0.967 | 0.975 |

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| cProfile pstats snakeviz profiling hotspot | python_profiling | 1 | python_profiling:0.5143<br>dns_debugging:0.2341<br>kill_process_on_port:0.2064 | 1 |
| python3 -m venv activate pip install requirements.txt | python_venv_setup | 1 | python_venv_setup:0.4953<br>python_import_error:0.3857<br>python_dependency_conflict:0.363 | 1 |
| git filter-branch --force git rm --cached secrets.env reflog gc prune | git_large_file_purge | 1 | git_large_file_purge:0.6246<br>git_undo_commit:0.5699<br>git_merge_conflict:0.3733 | 1 |
| git rebase origin/main --force-with-lease conflict | git_rebase_conflict | 1 | git_rebase_conflict:0.71<br>git_merge_conflict:0.3621<br>git_undo_commit:0.3408 | 1 |
| docker volume inspect pgdata postgres persist | docker_volume_mount | 1 | docker_volume_mount:0.3895<br>ssh_permission_denied:0.3034<br>curl_api_debug:0.2821 | 1 |
| alembic upgrade head revision migrate | db_migration_run | 2 | db_migration_rollback:0.6524<br>db_migration_run:0.6472<br>git_undo_commit:0.2384 | 1 |
| alembic downgrade revision rollback | db_migration_rollback | 1 | db_migration_rollback:0.6085<br>db_migration_run:0.4387<br>git_undo_commit:0.3708 | 1 |
| crontab -e cron.d */5 scheduled job | cron_job_setup | 1 | cron_job_setup:0.5714<br>cron_job_debug:0.4159<br>distractor_02:0.2679 | 1 |
| curl -v -s jq json api endpoint response | curl_api_debug | 1 | curl_api_debug:0.3755<br>nginx_ssl_cert:0.1844<br>git_undo_commit:0.1774 | 1 |
| lsof -i kill -9 port 8080 process pid | kill_process_on_port | 1 | kill_process_on_port:0.574<br>disk_space_cleanup:0.2974<br>systemd_service_debug:0.2489 | 2 |
| tmux new-session attach-session detach | tmux_session | 1 | tmux_session:0.8072<br>ssh_permission_denied:0.1255<br>distractor_08:0.121 | 1 |
| ssh-keygen authorized_keys ssh-copy-id id_rsa | ssh_key_setup | 1 | ssh_key_setup:0.3907<br>ssh_agent_forwarding:0.3402<br>rsync_transfer:0.2995 | 1 |
| gpg --symmetric --passphrase encrypt file decrypt | gpg_encrypt_file | 1 | gpg_encrypt_file:0.6024<br>distractor_03:0.1534<br>ssh_key_setup:0.1212 | 1 |
| resolvectl flush-caches dns nameserver resolv.conf | dns_cache_flush | 1 | dns_cache_flush:0.6165<br>dns_debugging:0.5129<br>disk_space_cleanup:0.2643 | 1 |
| tar czf archive.tar.gz compress extract directory | tar_backup | 1 | tar_backup:0.608<br>distractor_01:0.3263<br>distractor_05:0.3085 | 1 |
