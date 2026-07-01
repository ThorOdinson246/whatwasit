# Eval tables (auto-generated)

Corpus: 57 sessions (43 labeled + 14 distractor). Queries: 86 answerable + 10 null. Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim).


## Aggregate: semantic vs keyword

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 0.384 | 0.240 | 0.165 | 0.826 | 0.919 | 0.577 | 0.626 |
| keyword | 0.070 | 0.070 | 0.056 | 0.279 | 0.372 | 0.178 | 0.176 |

## Per-topic (semantic / keyword)

| Topic | n | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|--:|---:|---:|---:|---:|---:|---:|---:|
| cron-debug (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| cron-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.09 | 0.00 |
| cron-setup (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.10 | 0.00 |
| cron-setup (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| curl-debug (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.32 | 0.32 |
| curl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| db-migrate-down (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| db-migrate-down (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| db-migrate-up (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| db-migrate-up (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| disk-cleanup (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| disk-cleanup (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| dns-flush (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| dns-flush (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| dns-resolve (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| dns-resolve (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.53 | 0.50 |
| docker-cleanup (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.50 | 0.63 |
| docker-cleanup (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.10 | 0.00 |
| docker-compose (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.33 | 0.32 |
| docker-compose (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| docker-networking (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| docker-networking (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| docker-volumes (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| docker-volumes (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| env-path (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| env-path (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.06 | 0.00 |
| find-files (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| find-files (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| git-history-scrub (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.35 | 0.51 |
| git-history-scrub (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | 0.00 |
| git-merge (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.28 | 0.32 |
| git-merge (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| git-rebase (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.17 | 0.00 |
| git-rebase (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.12 | 0.19 |
| git-undo (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.29 | 0.47 |
| git-undo (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.27 | 0.32 |
| gpg-encrypt (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpg-encrypt (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.57 | 0.50 |
| kubectl-debug (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| kubectl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| log-parse (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-parse (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.06 | 0.00 |
| log-rotate (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-rotate (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| nginx-proxy (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
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
| perm-ownership (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| perm-ownership (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.19 | 0.25 |
| port-kill (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| port-kill (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| postgres-conn (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| postgres-conn (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.33 | 0.50 |
| python-depconflict (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.27 | 0.44 |
| python-depconflict (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.12 | 0.19 |
| python-import (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| python-import (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| python-profiling (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.00 |
| python-profiling (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.00 |
| python-venv (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| python-venv (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| rsync-sync (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| rsync-sync (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| sed-replace (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.16 | 0.22 |
| sed-replace (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| ssh-agent (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| ssh-agent (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.19 | 0.25 |
| ssh-denied (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| ssh-denied (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-keys (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-keys (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| systemd-debug (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| systemd-debug (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| tar-archive (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.24 | 0.25 |
| tar-archive (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| tmux (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.33 | 0.32 |
| tmux (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |

## Per-query (answerable): semantic rank & top-3 vs keyword rank

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| that time I was replaying my commits on top of the latest upstream ... | git_rebase_conflict | 6 | git_undo_commit:0.4184<br>git_large_file_purge:0.3362<br>db_migration_rollback:0.2784 | 5 |
| when I had to redo my branch history one commit at a time because o... | git_rebase_conflict | 6 | git_large_file_purge:0.4048<br>git_undo_commit:0.4025<br>git_merge_conflict:0.364 | 21 |
| sorting out the mess when pulling a teammate's work collided with m... | git_merge_conflict | 2 | distractor_08:0.2157<br>git_merge_conflict:0.2092<br>tmux_session:0.1938 | 19 |
| combining two lines of work where the same file got edited on both ... | git_merge_conflict | 15 | distractor_09:0.3384<br>distractor_08:0.2768<br>distractor_00:0.2579 | 50 |
| the time I had to walk back a change I'd already saved into the pro... | git_undo_commit | 3 | db_migration_rollback:0.3469<br>db_migration_run:0.3338<br>git_undo_commit:0.2886 | 23 |
| digging through the record of what I did to get back to an earlier ... | git_undo_commit | 4 | db_migration_rollback:0.3138<br>db_migration_run:0.2914<br>systemd_service_debug:0.2656 | 2 |
| when I accidentally checked in something that should never have bee... | git_large_file_purge | 5 | npm_audit_fix:0.3111<br>db_migration_rollback:0.2967<br>git_undo_commit:0.2808 | 57 |
| purging a sensitive file out of the entire project history everywhere | git_large_file_purge | 2 | find_large_old_files:0.449<br>git_large_file_purge:0.4204<br>gpg_encrypt_file:0.4117 | 56 |
| why my container kept losing everything every time it restarted | docker_volume_mount | 3 | systemd_service_debug:0.3271<br>docker_disk_prune:0.2628<br>docker_volume_mount:0.2558 | 56 |
| making the data inside a container actually survive between runs | docker_volume_mount | 1 | docker_volume_mount:0.2289<br>distractor_12:0.2154<br>docker_disk_prune:0.1832 | 3 |
| when two of my services couldn't reach each other until I wired the... | docker_network_connect | 3 | dns_cache_flush:0.2345<br>systemd_service_debug:0.1852<br>docker_network_connect:0.1579 | 25 |
| the container-to-container connectivity thing I had to set up | docker_network_connect | 1 | docker_network_connect:0.3541<br>docker_compose_stack:0.3205<br>docker_volume_mount:0.2574 | 32 |
| spinning up the whole multi-service stack from a single definition | docker_compose_stack | 2 | docker_network_connect:0.2002<br>docker_compose_stack:0.132<br>dns_cache_flush:0.1297 | 33 |
| bringing all the pieces of the app online at once | docker_compose_stack | 6 | distractor_01:0.2843<br>distractor_12:0.242<br>docker_network_connect:0.2304 | 4 |
| reclaiming the disk space eaten up by old images and dangling layers | docker_disk_prune | 2 | find_large_old_files:0.3185<br>docker_disk_prune:0.3072<br>disk_space_cleanup:0.2673 | 20 |
| cleaning out all the leftover junk the containers piled up | docker_disk_prune | 2 | disk_space_cleanup:0.2866<br>docker_disk_prune:0.2838<br>docker_volume_mount:0.2632 | 7 |
| isolating a project's libraries so they don't pollute the whole system | python_venv_setup | 39 | sudo_ownership_fix:0.2309<br>disk_space_cleanup:0.208<br>distractor_13:0.198 | 37 |
| setting up a clean sandbox for a fresh script's packages | python_venv_setup | 15 | distractor_00:0.3564<br>npm_cache_clear:0.3315<br>npm_dependency_resolution:0.3112 | 27 |
| when two libraries demanded incompatible versions of the same share... | python_dependency_conflict | 3 | db_migration_rollback:0.2257<br>db_migration_run:0.2105<br>python_dependency_conflict:0.1957 | 20 |
| untangling the package version standoff that kept breaking my install | python_dependency_conflict | 5 | db_migration_rollback:0.2887<br>disk_space_cleanup:0.2258<br>npm_dependency_resolution:0.219 | 5 |
| chasing down why the interpreter swore a package wasn't there even ... | python_import_error | 1 | python_import_error:0.3549<br>npm_dependency_resolution:0.3171<br>python_dependency_conflict:0.313 | 10 |
| that missing-module headache when running my code from the wrong place | python_import_error | 3 | npm_cache_clear:0.3272<br>python_profiling:0.2781<br>python_import_error:0.2101 | 27 |
| figuring out which part of my script was dragging the whole thing down | python_profiling | 17 | chmod_permission_error:0.2658<br>log_parsing_grep:0.2216<br>env_var_debug:0.2051 | 9 |
| hunting the slow function that was eating all the runtime | python_profiling | 9 | find_large_old_files:0.2794<br>disk_space_cleanup:0.2284<br>log_rotation:0.2086 | 24 |
| when the javascript package tree refused to install because require... | npm_dependency_resolution | 1 | npm_dependency_resolution:0.4011<br>npm_cache_clear:0.3368<br>npm_audit_fix:0.195 | 2 |
| forcing through the node module knot where nothing agreed on versions | npm_dependency_resolution | 2 | npm_cache_clear:0.3584<br>npm_dependency_resolution:0.3337<br>npm_audit_fix:0.2668 | 1 |
| patching the flagged security holes in my node packages | npm_audit_fix | 1 | npm_audit_fix:0.3588<br>npm_dependency_resolution:0.3347<br>npm_cache_clear:0.3149 | 20 |
| dealing with the reported vulnerabilities in my javascript dependen... | npm_audit_fix | 1 | npm_audit_fix:0.2837<br>npm_dependency_resolution:0.2213<br>npm_cache_clear:0.2001 | 28 |
| when a corrupted local package store gave me phantom build failures | npm_cache_clear | 1 | npm_cache_clear:0.3185<br>npm_dependency_resolution:0.284<br>systemd_service_debug:0.236 | 11 |
| wiping the download cache to get rid of bizarre install errors | npm_cache_clear | 2 | disk_space_cleanup:0.3448<br>npm_cache_clear:0.277<br>dns_cache_flush:0.2348 | 1 |
| setting up passwordless login so I'd stop typing my password to con... | ssh_key_setup | 2 | distractor_07:0.2406<br>ssh_key_setup:0.142<br>ssh_permission_denied:0.1339 | 11 |
| the time I created credentials to get into a remote machine without... | ssh_key_setup | 1 | ssh_key_setup:0.3196<br>distractor_07:0.2962<br>ssh_permission_denied:0.289 | 44 |
| making my local identity usable from a jump host to reach a machine... | ssh_agent_forwarding | 1 | ssh_agent_forwarding:0.2235<br>ssh_key_setup:0.2225<br>distractor_01:0.1269 | 3 |
| when I needed my key to carry through to a second server down the line | ssh_agent_forwarding | 4 | ssh_permission_denied:0.3567<br>ssh_key_setup:0.3481<br>distractor_08:0.1701 | 22 |
| why the remote box kept rejecting me even though I had the right key | ssh_permission_denied | 1 | ssh_permission_denied:0.2191<br>ssh_key_setup:0.1949<br>nginx_ssl_cert:0.1175 | 1 |
| troubleshooting getting locked out when logging into a server | ssh_permission_denied | 1 | ssh_permission_denied:0.1545<br>systemd_service_debug:0.1468<br>ssh_key_setup:0.1343 | 2 |
| scheduling a script to run on its own every night | cron_job_setup | 8 | distractor_02:0.5794<br>distractor_07:0.4135<br>cron_job_debug:0.3985 | 32 |
| setting something up to fire automatically on a repeating timer | cron_job_setup | 12 | distractor_02:0.2807<br>distractor_11:0.2349<br>distractor_07:0.2248 | 13 |
| why my scheduled task silently never actually ran | cron_job_debug | 1 | cron_job_debug:0.346<br>distractor_02:0.2476<br>distractor_07:0.2082 | 31 |
| chasing a background timer that just refused to trigger | cron_job_debug | 2 | distractor_11:0.2342<br>cron_job_debug:0.2292<br>distractor_02:0.2131 | 7 |
| rolling the database structure forward to the newest version | db_migration_run | 2 | distractor_01:0.304<br>db_migration_run:0.2459<br>db_migration_rollback:0.2399 | 24 |
| applying the pending schema changes to my tables | db_migration_run | 3 | distractor_08:0.1627<br>git_merge_conflict:0.1421<br>db_migration_run:0.1316 | 26 |
| undoing a structural change to the database that broke everything | db_migration_rollback | 2 | docker_volume_mount:0.2476<br>db_migration_rollback:0.2406<br>distractor_01:0.208 | 35 |
| walking the table layout back after a bad update | db_migration_rollback | 3 | disk_space_cleanup:0.1912<br>systemd_service_debug:0.1553<br>db_migration_rollback:0.147 | 11 |
| when the system refused to run my script until I changed its access... | chmod_permission_error | 1 | chmod_permission_error:0.3565<br>distractor_02:0.3292<br>kill_process_on_port:0.2305 | 5 |
| fixing the you-are-not-allowed error trying to execute a file | chmod_permission_error | 1 | chmod_permission_error:0.3569<br>gpg_encrypt_file:0.2357<br>distractor_06:0.2268 | 27 |
| reclaiming a bunch of files that ended up belonging to the wrong ac... | sudo_ownership_fix | 4 | gpg_encrypt_file:0.336<br>git_undo_commit:0.2708<br>find_large_old_files:0.2649 | 24 |
| when everything was locked because the superuser grabbed my directory | sudo_ownership_fix | 1 | sudo_ownership_fix:0.3918<br>distractor_03:0.2806<br>chmod_permission_error:0.2589 | 3 |
| why a domain name just wouldn't resolve to an address on my machine | dns_debugging | 2 | dns_cache_flush:0.3917<br>dns_debugging:0.3649<br>nginx_ssl_cert:0.1627 | 18 |
| chasing a name-lookup failure when trying to reach a site | dns_debugging | 2 | dns_cache_flush:0.307<br>dns_debugging:0.2887<br>nginx_reverse_proxy:0.1105 | 1 |
| when an old address kept sticking around long after it had changed | dns_cache_flush | 1 | dns_cache_flush:0.2724<br>db_migration_run:0.2497<br>db_migration_rollback:0.2435 | 13 |
| clearing the machine's memory of name lookups to pick up new records | dns_cache_flush | 2 | find_large_old_files:0.2922<br>dns_cache_flush:0.206<br>disk_space_cleanup:0.2025 | 32 |
| that thing where the gateway wasn't picking up my configuration cha... | nginx_reverse_proxy | 4 | dns_cache_flush:0.2392<br>db_migration_rollback:0.1496<br>systemd_service_debug:0.144 | 4 |
| when the front server kept routing to the old backend after I edite... | nginx_reverse_proxy | 1 | nginx_reverse_proxy:0.2393<br>dns_cache_flush:0.239<br>npm_cache_clear:0.2372 | 33 |
| renewing the expiring secure certificate so the browser lock icon s... | nginx_ssl_cert | 1 | nginx_ssl_cert:0.4395<br>dns_cache_flush:0.1598<br>npm_cache_clear:0.1544 | 36 |
| sorting out the https warning visitors were seeing on my site | nginx_ssl_cert | 1 | nginx_ssl_cert:0.3058<br>log_parsing_grep:0.1515<br>dns_cache_flush:0.1243 | 2 |
| digging through the web server records to tally how often requests ... | log_parsing_grep | 1 | log_parsing_grep:0.3593<br>dns_cache_flush:0.2857<br>python_dependency_conflict:0.1631 | 41 |
| slicing a big log file to count the recurring errors | log_parsing_grep | 1 | log_parsing_grep:0.5117<br>distractor_00:0.4199<br>log_rotation:0.3937 | 10 |
| when runaway log files were quietly eating up all the disk | log_rotation | 1 | log_rotation:0.446<br>log_parsing_grep:0.3645<br>cron_job_setup:0.3321 | 3 |
| keeping the ever-growing application output from filling storage | log_rotation | 1 | log_rotation:0.3044<br>distractor_04:0.2441<br>docker_disk_prune:0.2332 | 29 |
| tracking down what exactly was hogging all my storage when the driv... | disk_space_cleanup | 1 | disk_space_cleanup:0.3333<br>log_rotation:0.3221<br>find_large_old_files:0.3215 | 4 |
| hunting the culprit files that ate the free space on my machine | disk_space_cleanup | 2 | find_large_old_files:0.5272<br>disk_space_cleanup:0.4609<br>log_rotation:0.3488 | 35 |
| why a background service kept dying right after it started at boot | systemd_service_debug | 1 | systemd_service_debug:0.2502<br>kill_process_on_port:0.2426<br>dns_cache_flush:0.2289 | 3 |
| chasing a daemon that just would not stay running | systemd_service_debug | 22 | distractor_02:0.3223<br>distractor_11:0.3167<br>python_profiling:0.2628 | 28 |
| bundling an entire folder into a single compressed file to move it ... | tar_backup | 7 | distractor_06:0.4906<br>distractor_05:0.4424<br>distractor_04:0.4348 | 23 |
| packing up a directory into one archive for safekeeping | tar_backup | 3 | distractor_13:0.5201<br>distractor_05:0.4655<br>tar_backup:0.4317 | 27 |
| figuring out why a workload kept restarting over and over in the cl... | kubectl_pod_debug | 1 | kubectl_pod_debug:0.2661<br>log_rotation:0.1983<br>dns_cache_flush:0.1835 | 10 |
| chasing a crashing container managed by the orchestrator | kubectl_pod_debug | 5 | docker_compose_stack:0.2728<br>docker_disk_prune:0.269<br>docker_volume_mount:0.2609 | 21 |
| mirroring a directory up to a remote server while only sending what... | rsync_transfer | 1 | rsync_transfer:0.4515<br>distractor_08:0.4186<br>distractor_02:0.3336 | 37 |
| efficiently copying just the modified files over to another machine | rsync_transfer | 3 | distractor_08:0.4649<br>distractor_09:0.3767<br>rsync_transfer:0.3644 | 33 |
| renaming one identifier across every file in the project in a singl... | find_replace_sed | 4 | distractor_13:0.3004<br>distractor_09:0.2598<br>distractor_00:0.2587 | 35 |
| doing a bulk text swap through a whole codebase at once | find_replace_sed | 14 | distractor_04:0.2107<br>distractor_09:0.2058<br>distractor_07:0.1731 | 14 |
| when a program wasn't being found until I fixed where the shell loo... | env_var_debug | 1 | env_var_debug:0.3224<br>docker_volume_mount:0.3191<br>python_import_error:0.2942 | 10 |
| getting an environment setting to stick around across new terminal ... | env_var_debug | 2 | distractor_07:0.3404<br>env_var_debug:0.2575<br>distractor_00:0.218 | 44 |
| when my app couldn't reach the database and kept getting turned awa... | postgres_connection_refused | 2 | systemd_service_debug:0.3515<br>postgres_connection_refused:0.3036<br>docker_volume_mount:0.2561 | 3 |
| sorting out the data store refusing my local connections until I ed... | postgres_connection_refused | 1 | postgres_connection_refused:0.2524<br>dns_cache_flush:0.1914<br>docker_volume_mount:0.1664 | 3 |
| when something was already squatting on the address my server neede... | kill_process_on_port | 5 | log_rotation:0.2165<br>dns_cache_flush:0.2012<br>nginx_ssl_cert:0.1818 | 42 |
| freeing up a busy network endpoint that a leftover process was stil... | kill_process_on_port | 1 | kill_process_on_port:0.2647<br>find_large_old_files:0.1858<br>disk_space_cleanup:0.1707 | 24 |
| poking at a web endpoint by hand to see what it was actually sendin... | curl_api_debug | 2 | dns_cache_flush:0.1623<br>curl_api_debug:0.1577<br>kill_process_on_port:0.1548 | 42 |
| inspecting the raw reply from a remote service while it was misbeha... | curl_api_debug | 7 | dns_cache_flush:0.2052<br>git_undo_commit:0.1645<br>nginx_ssl_cert:0.1555 | 37 |
| keeping my remote work alive so it survived me getting disconnected | tmux_session | 6 | distractor_07:0.2171<br>distractor_11:0.2171<br>distractor_02:0.1748 | 1 |
| getting back into the exact same terminal workspace after logging out | tmux_session | 2 | distractor_07:0.2775<br>tmux_session:0.2739<br>git_undo_commit:0.2432 | 2 |
| locating files by how big or how old they were across a whole tree | find_large_old_files | 2 | log_parsing_grep:0.4937<br>find_large_old_files:0.4209<br>distractor_00:0.2707 | 31 |
| tracking down specific files buried deep somewhere in a directory | find_large_old_files | 1 | find_large_old_files:0.4572<br>log_parsing_grep:0.4395<br>gpg_encrypt_file:0.3799 | 21 |
| locking a sensitive document behind a passphrase before handing it off | gpg_encrypt_file | 1 | gpg_encrypt_file:0.2882<br>distractor_07:0.177<br>distractor_03:0.1387 | 1 |
| scrambling a file so only someone with the secret word could read it | gpg_encrypt_file | 1 | gpg_encrypt_file:0.4528<br>distractor_06:0.2664<br>distractor_03:0.2647 | 7 |

## Null queries (no correct session): top-1 returned

| Query | Sem top-1 (id:score) | KW top-1 (id:score) |
|---|---|---|
| when I set up the jenkins continuous integration pipeline | docker_compose_stack:0.2722 | distractor_12:1.0036 |
| configuring terraform to provision cloud infrastructure | docker_network_connect:0.1756 | npm_dependency_resolution:0.0298 |
| that time I fought the rust compiler's borrow checker | distractor_13:0.1276 | python_profiling:0.0301 |
| tuning the elasticsearch cluster shard allocation | docker_disk_prune:0.1616 | sudo_ownership_fix:0.0327 |
| setting up the redis pub sub messaging channels | docker_network_connect:0.204 | docker_network_connect:1.0216 |
| writing the ansible playbook to configure the fleet | distractor_13:0.2013 | sudo_ownership_fix:0.0304 |
| debugging the graphql resolver n plus one queries | dns_cache_flush:0.3867 | git_undo_commit:0.032 |
| enabling two factor authentication on my account | ssh_permission_denied:0.1532 | db_migration_run:0.0351 |
| training the neural network on the gpu cluster | gpg_encrypt_file:0.1534 | docker_network_connect:1.0217 |
| configuring the bluetooth audio device pairing | distractor_10:0.1466 | gpg_encrypt_file:0.0317 |
