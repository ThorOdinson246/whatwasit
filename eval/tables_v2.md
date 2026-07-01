# Eval tables (auto-generated)

Corpus: 57 sessions (43 labeled + 14 distractor). Queries: 86 answerable + 10 null. Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).


## Aggregate: semantic vs keyword

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 0.442 | 0.260 | 0.165 | 0.826 | 0.930 | 0.615 | 0.654 |
| keyword | 0.070 | 0.070 | 0.056 | 0.279 | 0.372 | 0.178 | 0.176 |

## Per-topic (semantic / keyword)

| Topic | n | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|--:|---:|---:|---:|---:|---:|---:|---:|
| cron-debug (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| cron-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.09 | 0.00 |
| cron-setup (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.23 | 0.25 |
| cron-setup (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| curl-debug (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.15 | 0.19 |
| curl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| db-migrate-down (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| db-migrate-down (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| db-migrate-up (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| db-migrate-up (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| disk-cleanup (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| disk-cleanup (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| dns-flush (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| dns-flush (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| dns-resolve (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| dns-resolve (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.53 | 0.50 |
| docker-cleanup (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| docker-cleanup (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.10 | 0.00 |
| docker-compose (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.29 | 0.47 |
| docker-compose (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| docker-networking (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| docker-networking (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| docker-volumes (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.33 | 0.32 |
| docker-volumes (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| env-path (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| env-path (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.06 | 0.00 |
| find-files (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| find-files (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| git-history-scrub (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 1.00 | 0.17 | 0.22 |
| git-history-scrub (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | 0.00 |
| git-merge (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.29 | 0.32 |
| git-merge (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| git-rebase (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.15 | 0.00 |
| git-rebase (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.12 | 0.19 |
| git-undo (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.33 | 0.50 |
| git-undo (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.27 | 0.32 |
| gpg-encrypt (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpg-encrypt (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.57 | 0.50 |
| kubectl-debug (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.57 | 0.50 |
| kubectl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| log-parse (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-parse (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.06 | 0.00 |
| log-rotate (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-rotate (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| nginx-proxy (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.33 | 0.50 |
| nginx-proxy (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| nginx-ssl (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| nginx-ssl (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.26 | 0.32 |
| npm-audit (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-audit (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| npm-cache (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-cache (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.55 | 0.50 |
| npm-deps (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-deps (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| perm-chmod (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| perm-chmod (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.12 | 0.19 |
| perm-ownership (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| perm-ownership (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.19 | 0.25 |
| port-kill (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| port-kill (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| postgres-conn (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| postgres-conn (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.33 | 0.50 |
| python-depconflict (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.25 | 0.25 |
| python-depconflict (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.12 | 0.19 |
| python-import (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| python-import (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| python-profiling (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.09 | 0.00 |
| python-profiling (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.00 |
| python-venv (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.06 | 0.00 |
| python-venv (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| rsync-sync (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| rsync-sync (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| sed-replace (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.29 | 0.32 |
| sed-replace (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| ssh-agent (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| ssh-agent (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.19 | 0.25 |
| ssh-denied (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| ssh-denied (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-keys (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-keys (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| systemd-debug (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.19 | 0.25 |
| systemd-debug (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| tar-archive (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| tar-archive (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| tmux (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| tmux (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |

## Per-query (answerable): semantic rank & top-3 vs keyword rank

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| that time I was replaying my commits on top of the latest upstream ... | git_rebase_conflict | 8 | git_undo_commit:0.5408<br>db_migration_rollback:0.3696<br>db_migration_run:0.3185 | 5 |
| when I had to redo my branch history one commit at a time because o... | git_rebase_conflict | 6 | git_undo_commit:0.5202<br>git_merge_conflict:0.4163<br>db_migration_rollback:0.4129 | 21 |
| sorting out the mess when pulling a teammate's work collided with m... | git_merge_conflict | 2 | tmux_session:0.2653<br>git_merge_conflict:0.2393<br>git_undo_commit:0.226 | 19 |
| combining two lines of work where the same file got edited on both ... | git_merge_conflict | 12 | git_undo_commit:0.2723<br>distractor_08:0.2331<br>log_parsing_grep:0.216 | 50 |
| the time I had to walk back a change I'd already saved into the pro... | git_undo_commit | 3 | db_migration_rollback:0.4606<br>db_migration_run:0.4227<br>git_undo_commit:0.373 | 23 |
| digging through the record of what I did to get back to an earlier ... | git_undo_commit | 3 | db_migration_rollback:0.4167<br>db_migration_run:0.369<br>git_undo_commit:0.3316 | 2 |
| when I accidentally checked in something that should never have bee... | git_large_file_purge | 10 | npm_audit_fix:0.4032<br>db_migration_rollback:0.394<br>git_undo_commit:0.363 | 57 |
| purging a sensitive file out of the entire project history everywhere | git_large_file_purge | 4 | find_large_old_files:0.5464<br>gpg_encrypt_file:0.5259<br>sudo_ownership_fix:0.3988 | 56 |
| why my container kept losing everything every time it restarted | docker_volume_mount | 6 | systemd_service_debug:0.3693<br>docker_disk_prune:0.3235<br>log_rotation:0.2793 | 56 |
| making the data inside a container actually survive between runs | docker_volume_mount | 2 | docker_disk_prune:0.2254<br>docker_volume_mount:0.2111<br>docker_network_connect:0.1659 | 3 |
| when two of my services couldn't reach each other until I wired the... | docker_network_connect | 3 | dns_cache_flush:0.2935<br>systemd_service_debug:0.2091<br>docker_network_connect:0.1547 | 25 |
| the container-to-container connectivity thing I had to set up | docker_network_connect | 2 | docker_compose_stack:0.3816<br>docker_network_connect:0.347<br>docker_disk_prune:0.302 | 32 |
| spinning up the whole multi-service stack from a single definition | docker_compose_stack | 3 | docker_network_connect:0.1962<br>dns_cache_flush:0.1624<br>docker_compose_stack:0.1572 | 33 |
| bringing all the pieces of the app online at once | docker_compose_stack | 4 | distractor_01:0.247<br>tar_backup:0.2383<br>docker_network_connect:0.2257 | 4 |
| reclaiming the disk space eaten up by old images and dangling layers | docker_disk_prune | 2 | find_large_old_files:0.3876<br>docker_disk_prune:0.3781<br>disk_space_cleanup:0.3425 | 20 |
| cleaning out all the leftover junk the containers piled up | docker_disk_prune | 2 | disk_space_cleanup:0.3672<br>docker_disk_prune:0.3492<br>find_large_old_files:0.2636 | 7 |
| isolating a project's libraries so they don't pollute the whole system | python_venv_setup | 39 | sudo_ownership_fix:0.3123<br>disk_space_cleanup:0.2665<br>find_large_old_files:0.2346 | 37 |
| setting up a clean sandbox for a fresh script's packages | python_venv_setup | 10 | npm_cache_clear:0.4091<br>chmod_permission_error:0.3858<br>disk_space_cleanup:0.3646 | 27 |
| when two libraries demanded incompatible versions of the same share... | python_dependency_conflict | 3 | db_migration_rollback:0.2997<br>db_migration_run:0.2666<br>python_dependency_conflict:0.2221 | 20 |
| untangling the package version standoff that kept breaking my install | python_dependency_conflict | 6 | db_migration_rollback:0.3834<br>disk_space_cleanup:0.2892<br>npm_dependency_resolution:0.2552 | 5 |
| chasing down why the interpreter swore a package wasn't there even ... | python_import_error | 1 | python_import_error:0.4157<br>npm_dependency_resolution:0.3694<br>python_dependency_conflict:0.3552 | 10 |
| that missing-module headache when running my code from the wrong place | python_import_error | 3 | npm_cache_clear:0.4038<br>python_profiling:0.3356<br>python_import_error:0.2461 | 27 |
| figuring out which part of my script was dragging the whole thing down | python_profiling | 16 | chmod_permission_error:0.3426<br>env_var_debug:0.262<br>git_undo_commit:0.2572 | 9 |
| hunting the slow function that was eating all the runtime | python_profiling | 9 | find_large_old_files:0.34<br>disk_space_cleanup:0.2926<br>kill_process_on_port:0.2473 | 24 |
| when the javascript package tree refused to install because require... | npm_dependency_resolution | 1 | npm_dependency_resolution:0.4674<br>npm_cache_clear:0.4156<br>npm_audit_fix:0.2528 | 2 |
| forcing through the node module knot where nothing agreed on versions | npm_dependency_resolution | 2 | npm_cache_clear:0.4423<br>npm_dependency_resolution:0.3887<br>npm_audit_fix:0.3458 | 1 |
| patching the flagged security holes in my node packages | npm_audit_fix | 1 | npm_audit_fix:0.4651<br>npm_dependency_resolution:0.3899<br>npm_cache_clear:0.3886 | 20 |
| dealing with the reported vulnerabilities in my javascript dependen... | npm_audit_fix | 1 | npm_audit_fix:0.3677<br>npm_dependency_resolution:0.2579<br>npm_cache_clear:0.2469 | 28 |
| when a corrupted local package store gave me phantom build failures | npm_cache_clear | 1 | npm_cache_clear:0.393<br>npm_dependency_resolution:0.3309<br>disk_space_cleanup:0.2907 | 11 |
| wiping the download cache to get rid of bizarre install errors | npm_cache_clear | 2 | disk_space_cleanup:0.4417<br>npm_cache_clear:0.3419<br>dns_cache_flush:0.2939 | 1 |
| setting up passwordless login so I'd stop typing my password to con... | ssh_key_setup | 2 | distractor_07:0.1745<br>ssh_key_setup:0.1591<br>ssh_permission_denied:0.1528 | 11 |
| the time I created credentials to get into a remote machine without... | ssh_key_setup | 1 | ssh_key_setup:0.358<br>ssh_permission_denied:0.3297<br>ssh_agent_forwarding:0.2671 | 44 |
| making my local identity usable from a jump host to reach a machine... | ssh_agent_forwarding | 1 | ssh_agent_forwarding:0.2653<br>ssh_key_setup:0.2492<br>distractor_01:0.1103 | 3 |
| when I needed my key to carry through to a second server down the line | ssh_agent_forwarding | 3 | ssh_permission_denied:0.4069<br>ssh_key_setup:0.39<br>ssh_agent_forwarding:0.1777 | 22 |
| why the remote box kept rejecting me even though I had the right key | ssh_permission_denied | 1 | ssh_permission_denied:0.25<br>ssh_key_setup:0.2184<br>nginx_ssl_cert:0.1284 | 1 |
| troubleshooting getting locked out when logging into a server | ssh_permission_denied | 1 | ssh_permission_denied:0.1762<br>systemd_service_debug:0.1658<br>ssh_key_setup:0.1504 | 2 |
| scheduling a script to run on its own every night | cron_job_setup | 3 | cron_job_debug:0.468<br>distractor_02:0.3873<br>cron_job_setup:0.3035 | 32 |
| setting something up to fire automatically on a repeating timer | cron_job_setup | 8 | distractor_02:0.1876<br>distractor_07:0.1629<br>cron_job_debug:0.1574 | 13 |
| why my scheduled task silently never actually ran | cron_job_debug | 1 | cron_job_debug:0.4064<br>cron_job_setup:0.2445<br>distractor_02:0.1655 | 31 |
| chasing a background timer that just refused to trigger | cron_job_debug | 1 | cron_job_debug:0.2692<br>cron_job_setup:0.162<br>python_profiling:0.1544 | 7 |
| rolling the database structure forward to the newest version | db_migration_run | 2 | db_migration_rollback:0.3185<br>db_migration_run:0.3114<br>distractor_01:0.2641 | 24 |
| applying the pending schema changes to my tables | db_migration_run | 1 | db_migration_run:0.1666<br>git_merge_conflict:0.1625<br>chmod_permission_error:0.1429 | 26 |
| undoing a structural change to the database that broke everything | db_migration_rollback | 1 | db_migration_rollback:0.3194<br>git_undo_commit:0.2455<br>db_migration_run:0.2293 | 35 |
| walking the table layout back after a bad update | db_migration_rollback | 2 | disk_space_cleanup:0.2449<br>db_migration_rollback:0.1951<br>systemd_service_debug:0.1753 | 11 |
| when the system refused to run my script until I changed its access... | chmod_permission_error | 1 | chmod_permission_error:0.4594<br>kill_process_on_port:0.3024<br>npm_audit_fix:0.2699 | 5 |
| fixing the you-are-not-allowed error trying to execute a file | chmod_permission_error | 1 | chmod_permission_error:0.4599<br>gpg_encrypt_file:0.3011<br>kill_process_on_port:0.2673 | 27 |
| reclaiming a bunch of files that ended up belonging to the wrong ac... | sudo_ownership_fix | 3 | gpg_encrypt_file:0.4292<br>git_undo_commit:0.35<br>sudo_ownership_fix:0.3358 | 24 |
| when everything was locked because the superuser grabbed my directory | sudo_ownership_fix | 1 | sudo_ownership_fix:0.5299<br>chmod_permission_error:0.3337<br>gpg_encrypt_file:0.3019 | 3 |
| why a domain name just wouldn't resolve to an address on my machine | dns_debugging | 2 | dns_cache_flush:0.4903<br>dns_debugging:0.4516<br>nginx_ssl_cert:0.1777 | 18 |
| chasing a name-lookup failure when trying to reach a site | dns_debugging | 2 | dns_cache_flush:0.3843<br>dns_debugging:0.3572<br>kill_process_on_port:0.1338 | 1 |
| when an old address kept sticking around long after it had changed | dns_cache_flush | 1 | dns_cache_flush:0.341<br>db_migration_rollback:0.3233<br>db_migration_run:0.3162 | 13 |
| clearing the machine's memory of name lookups to pick up new records | dns_cache_flush | 3 | find_large_old_files:0.3556<br>disk_space_cleanup:0.2595<br>dns_cache_flush:0.2579 | 32 |
| that thing where the gateway wasn't picking up my configuration cha... | nginx_reverse_proxy | 3 | dns_cache_flush:0.2994<br>db_migration_rollback:0.1986<br>nginx_reverse_proxy:0.1629 | 4 |
| when the front server kept routing to the old backend after I edite... | nginx_reverse_proxy | 3 | dns_cache_flush:0.2992<br>npm_cache_clear:0.2927<br>nginx_reverse_proxy:0.2758 | 33 |
| renewing the expiring secure certificate so the browser lock icon s... | nginx_ssl_cert | 1 | nginx_ssl_cert:0.4801<br>dns_cache_flush:0.2<br>npm_cache_clear:0.1906 | 36 |
| sorting out the https warning visitors were seeing on my site | nginx_ssl_cert | 1 | nginx_ssl_cert:0.3341<br>log_parsing_grep:0.168<br>dns_cache_flush:0.1556 | 2 |
| digging through the web server records to tally how often requests ... | log_parsing_grep | 1 | log_parsing_grep:0.3984<br>dns_cache_flush:0.3576<br>kill_process_on_port:0.1971 | 41 |
| slicing a big log file to count the recurring errors | log_parsing_grep | 1 | log_parsing_grep:0.5674<br>cron_job_setup:0.5112<br>log_rotation:0.4411 | 10 |
| when runaway log files were quietly eating up all the disk | log_rotation | 1 | log_rotation:0.4997<br>cron_job_setup:0.4533<br>log_parsing_grep:0.4043 | 3 |
| keeping the ever-growing application output from filling storage | log_rotation | 1 | log_rotation:0.341<br>docker_disk_prune:0.287<br>disk_space_cleanup:0.2574 | 29 |
| tracking down what exactly was hogging all my storage when the driv... | disk_space_cleanup | 1 | disk_space_cleanup:0.427<br>find_large_old_files:0.3913<br>log_rotation:0.3608 | 4 |
| hunting the culprit files that ate the free space on my machine | disk_space_cleanup | 2 | find_large_old_files:0.6416<br>disk_space_cleanup:0.5905<br>kill_process_on_port:0.4305 | 35 |
| why a background service kept dying right after it started at boot | systemd_service_debug | 3 | kill_process_on_port:0.3183<br>dns_cache_flush:0.2865<br>systemd_service_debug:0.2825 | 3 |
| chasing a daemon that just would not stay running | systemd_service_debug | 19 | python_profiling:0.3172<br>cron_job_debug:0.2955<br>kill_process_on_port:0.2783 | 28 |
| bundling an entire folder into a single compressed file to move it ... | tar_backup | 1 | tar_backup:0.4199<br>distractor_06:0.4172<br>distractor_04:0.4 | 23 |
| packing up a directory into one archive for safekeeping | tar_backup | 1 | tar_backup:0.5225<br>find_large_old_files:0.4479<br>gpg_encrypt_file:0.3911 | 27 |
| figuring out why a workload kept restarting over and over in the cl... | kubectl_pod_debug | 1 | kubectl_pod_debug:0.2974<br>kill_process_on_port:0.2381<br>dns_cache_flush:0.2297 | 10 |
| chasing a crashing container managed by the orchestrator | kubectl_pod_debug | 7 | docker_disk_prune:0.331<br>docker_compose_stack:0.3248<br>docker_volume_mount:0.2405 | 21 |
| mirroring a directory up to a remote server while only sending what... | rsync_transfer | 1 | rsync_transfer:0.4895<br>distractor_08:0.3526<br>git_undo_commit:0.335 | 37 |
| efficiently copying just the modified files over to another machine | rsync_transfer | 1 | rsync_transfer:0.3951<br>distractor_08:0.3915<br>find_large_old_files:0.3559 | 33 |
| renaming one identifier across every file in the project in a singl... | find_replace_sed | 2 | gpg_encrypt_file:0.2691<br>find_replace_sed:0.2558<br>distractor_04:0.2159 | 35 |
| doing a bulk text swap through a whole codebase at once | find_replace_sed | 12 | distractor_04:0.1938<br>distractor_08:0.1452<br>distractor_03:0.1449 | 14 |
| when a program wasn't being found until I fixed where the shell loo... | env_var_debug | 1 | env_var_debug:0.4118<br>chmod_permission_error:0.3774<br>kill_process_on_port:0.345 | 10 |
| getting an environment setting to stick around across new terminal ... | env_var_debug | 1 | env_var_debug:0.329<br>tmux_session:0.2586<br>distractor_07:0.2468 | 44 |
| when my app couldn't reach the database and kept getting turned awa... | postgres_connection_refused | 2 | systemd_service_debug:0.3969<br>postgres_connection_refused:0.3204<br>dns_cache_flush:0.2424 | 3 |
| sorting out the data store refusing my local connections until I ed... | postgres_connection_refused | 1 | postgres_connection_refused:0.2664<br>dns_cache_flush:0.2396<br>docker_volume_mount:0.1534 | 3 |
| when something was already squatting on the address my server neede... | kill_process_on_port | 4 | dns_cache_flush:0.2519<br>log_rotation:0.2425<br>nginx_ssl_cert:0.1986 | 42 |
| freeing up a busy network endpoint that a leftover process was stil... | kill_process_on_port | 1 | kill_process_on_port:0.3472<br>find_large_old_files:0.2261<br>disk_space_cleanup:0.2187 | 24 |
| poking at a web endpoint by hand to see what it was actually sendin... | curl_api_debug | 5 | dns_cache_flush:0.2032<br>kill_process_on_port:0.2031<br>dns_debugging:0.1654 | 42 |
| inspecting the raw reply from a remote service while it was misbeha... | curl_api_debug | 11 | dns_cache_flush:0.2568<br>git_undo_commit:0.2126<br>nginx_ssl_cert:0.1699 | 37 |
| keeping my remote work alive so it survived me getting disconnected | tmux_session | 1 | tmux_session:0.1893<br>kill_process_on_port:0.1719<br>ssh_key_setup:0.1673 | 1 |
| getting back into the exact same terminal workspace after logging out | tmux_session | 1 | tmux_session:0.3751<br>git_undo_commit:0.3143<br>sudo_ownership_fix:0.2555 | 2 |
| locating files by how big or how old they were across a whole tree | find_large_old_files | 2 | log_parsing_grep:0.5476<br>find_large_old_files:0.5122<br>cron_job_setup:0.3309 | 31 |
| tracking down specific files buried deep somewhere in a directory | find_large_old_files | 1 | find_large_old_files:0.5564<br>log_parsing_grep:0.4874<br>gpg_encrypt_file:0.4853 | 21 |
| locking a sensitive document behind a passphrase before handing it off | gpg_encrypt_file | 1 | gpg_encrypt_file:0.3682<br>distractor_07:0.1283<br>distractor_03:0.1227 | 1 |
| scrambling a file so only someone with the secret word could read it | gpg_encrypt_file | 1 | gpg_encrypt_file:0.5784<br>distractor_03:0.2342<br>distractor_04:0.23 | 7 |

## Null queries (no correct session): top-1 returned

| Query | Sem top-1 (id:score) | KW top-1 (id:score) |
|---|---|---|
| when I set up the jenkins continuous integration pipeline | docker_compose_stack:0.3241 | distractor_12:1.0036 |
| configuring terraform to provision cloud infrastructure | docker_network_connect:0.1721 | npm_dependency_resolution:0.0298 |
| that time I fought the rust compiler's borrow checker | npm_audit_fix:0.153 | python_profiling:0.0301 |
| tuning the elasticsearch cluster shard allocation | docker_disk_prune:0.1988 | sudo_ownership_fix:0.0327 |
| setting up the redis pub sub messaging channels | db_migration_rollback:0.2071 | docker_network_connect:1.0216 |
| writing the ansible playbook to configure the fleet | postgres_connection_refused:0.204 | sudo_ownership_fix:0.0304 |
| debugging the graphql resolver n plus one queries | dns_cache_flush:0.4841 | git_undo_commit:0.032 |
| enabling two factor authentication on my account | ssh_permission_denied:0.1748 | db_migration_run:0.0351 |
| training the neural network on the gpu cluster | gpg_encrypt_file:0.1959 | docker_network_connect:1.0217 |
| configuring the bluetooth audio device pairing | distractor_10:0.0998 | gpg_encrypt_file:0.0317 |
