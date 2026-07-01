# Eval tables (auto-generated)

Corpus: 57 sessions (43 labeled + 14 distractor). Queries: 86 answerable + 10 null. Model: `BAAI/bge-small-en-v1.5` (384-dim).


## Aggregate: semantic vs keyword

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 0.465 | 0.240 | 0.156 | 0.779 | 0.884 | 0.613 | 0.638 |
| keyword | 0.291 | 0.155 | 0.112 | 0.558 | 0.698 | 0.415 | 0.427 |

## Per-topic (semantic / keyword)

| Topic | n | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|--:|---:|---:|---:|---:|---:|---:|---:|
| cron-debug (sem) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| cron-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.15 | 0.00 |
| cron-setup (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| cron-setup (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| curl-debug (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| curl-debug (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| db-migrate-down (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| db-migrate-down (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.31 | 0.32 |
| db-migrate-up (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| db-migrate-up (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| disk-cleanup (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.09 | 0.00 |
| disk-cleanup (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| dns-flush (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| dns-flush (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.55 | 0.50 |
| dns-resolve (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| dns-resolve (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| docker-cleanup (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| docker-cleanup (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| docker-compose (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| docker-compose (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| docker-networking (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| docker-networking (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.18 | 0.25 |
| docker-volumes (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| docker-volumes (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| env-path (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| env-path (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.00 |
| find-files (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.24 | 0.25 |
| find-files (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| git-history-scrub (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| git-history-scrub (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.53 | 0.50 |
| git-merge (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.27 | 0.32 |
| git-merge (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| git-rebase (sem) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 1.00 | 0.18 | 0.19 |
| git-rebase (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.07 | 0.00 |
| git-undo (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| git-undo (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| gpg-encrypt (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| gpg-encrypt (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| kubectl-debug (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| kubectl-debug (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| log-parse (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.21 | 0.25 |
| log-parse (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 |
| log-rotate (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| log-rotate (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.53 | 0.50 |
| nginx-proxy (sem) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.12 | 0.00 |
| nginx-proxy (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 |
| nginx-ssl (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| nginx-ssl (kw) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| npm-audit (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-audit (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.67 | 0.75 |
| npm-cache (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| npm-cache (kw) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| npm-deps (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| npm-deps (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| perm-chmod (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| perm-chmod (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| perm-ownership (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.29 | 0.32 |
| perm-ownership (kw) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.27 | 0.44 |
| port-kill (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.56 | 0.50 |
| port-kill (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| postgres-conn (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.60 | 0.69 |
| postgres-conn (kw) | 2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 |
| python-depconflict (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| python-depconflict (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.27 | 0.32 |
| python-import (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.31 | 0.32 |
| python-import (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| python-profiling (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 1.00 | 0.24 | 0.25 |
| python-profiling (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.51 | 0.50 |
| python-venv (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.20 | 0.25 |
| python-venv (kw) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.26 | 0.32 |
| rsync-sync (sem) | 2 | 0.50 | 0.17 | 0.20 | 1.00 | 1.00 | 0.62 | 0.72 |
| rsync-sync (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 0.50 | 0.14 | 0.22 |
| sed-replace (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| sed-replace (kw) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| ssh-agent (sem) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| ssh-agent (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 0.50 | 0.52 | 0.50 |
| ssh-denied (sem) | 2 | 0.00 | 0.17 | 0.10 | 0.50 | 0.50 | 0.29 | 0.32 |
| ssh-denied (kw) | 2 | 0.00 | 0.00 | 0.10 | 0.50 | 1.00 | 0.17 | 0.19 |
| ssh-keys (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| ssh-keys (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| systemd-debug (sem) | 2 | 0.50 | 0.33 | 0.20 | 1.00 | 1.00 | 0.75 | 0.82 |
| systemd-debug (kw) | 2 | 0.00 | 0.17 | 0.20 | 1.00 | 1.00 | 0.38 | 0.53 |
| tar-archive (sem) | 2 | 0.00 | 0.33 | 0.20 | 1.00 | 1.00 | 0.42 | 0.57 |
| tar-archive (kw) | 2 | 0.50 | 0.17 | 0.10 | 0.50 | 1.00 | 0.58 | 0.50 |
| tmux (sem) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |
| tmux (kw) | 2 | 1.00 | 0.33 | 0.20 | 1.00 | 1.00 | 1.00 | 1.00 |

## Per-query (answerable): semantic rank & top-3 vs keyword rank

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| that time I was replaying my commits on top of the latest upstream ... | git_rebase_conflict | 5 | git_undo_commit:0.6189<br>tmux_session:0.5659<br>git_large_file_purge:0.5511 | 10 |
| when I had to redo my branch history one commit at a time because o... | git_rebase_conflict | 6 | git_undo_commit:0.5886<br>db_migration_rollback:0.5771<br>git_merge_conflict:0.5385 | 29 |
| sorting out the mess when pulling a teammate's work collided with m... | git_merge_conflict | 2 | git_undo_commit:0.5021<br>git_merge_conflict:0.5017<br>distractor_07:0.4625 | 16 |
| combining two lines of work where the same file got edited on both ... | git_merge_conflict | 26 | find_replace_sed:0.5296<br>distractor_08:0.4862<br>git_undo_commit:0.484 | 41 |
| the time I had to walk back a change I'd already saved into the pro... | git_undo_commit | 1 | git_undo_commit:0.5569<br>db_migration_rollback:0.5331<br>db_migration_run:0.5032 | 3 |
| digging through the record of what I did to get back to an earlier ... | git_undo_commit | 1 | git_undo_commit:0.5861<br>db_migration_rollback:0.5296<br>dns_cache_flush:0.5106 | 17 |
| when I accidentally checked in something that should never have bee... | git_large_file_purge | 2 | git_undo_commit:0.5829<br>git_large_file_purge:0.5637<br>npm_audit_fix:0.5224 | 1 |
| purging a sensitive file out of the entire project history everywhere | git_large_file_purge | 1 | git_large_file_purge:0.6249<br>distractor_05:0.6105<br>gpg_encrypt_file:0.6051 | 18 |
| why my container kept losing everything every time it restarted | docker_volume_mount | 2 | docker_disk_prune:0.5938<br>docker_volume_mount:0.5761<br>distractor_09:0.5468 | 5 |
| making the data inside a container actually survive between runs | docker_volume_mount | 1 | docker_volume_mount:0.632<br>distractor_09:0.6149<br>docker_disk_prune:0.5869 | 1 |
| when two of my services couldn't reach each other until I wired the... | docker_network_connect | 2 | tmux_session:0.4903<br>docker_network_connect:0.4774<br>docker_compose_stack:0.4732 | 30 |
| the container-to-container connectivity thing I had to set up | docker_network_connect | 1 | docker_network_connect:0.6139<br>docker_compose_stack:0.596<br>distractor_12:0.5914 | 3 |
| spinning up the whole multi-service stack from a single definition | docker_compose_stack | 1 | docker_compose_stack:0.6352<br>docker_network_connect:0.5158<br>dns_cache_flush:0.5096 | 1 |
| bringing all the pieces of the app online at once | docker_compose_stack | 3 | docker_network_connect:0.5417<br>distractor_01:0.5316<br>docker_compose_stack:0.5205 | 4 |
| reclaiming the disk space eaten up by old images and dangling layers | docker_disk_prune | 1 | docker_disk_prune:0.6416<br>tar_backup:0.5894<br>gpg_encrypt_file:0.5872 | 1 |
| cleaning out all the leftover junk the containers piled up | docker_disk_prune | 1 | docker_disk_prune:0.5203<br>distractor_00:0.4927<br>disk_space_cleanup:0.4914 | 53 |
| isolating a project's libraries so they don't pollute the whole system | python_venv_setup | 14 | tar_backup:0.5954<br>sudo_ownership_fix:0.5658<br>distractor_05:0.5507 | 41 |
| setting up a clean sandbox for a fresh script's packages | python_venv_setup | 3 | distractor_00:0.6637<br>distractor_09:0.6393<br>python_venv_setup:0.6102 | 2 |
| when two libraries demanded incompatible versions of the same share... | python_dependency_conflict | 1 | python_dependency_conflict:0.576<br>npm_dependency_resolution:0.5623<br>db_migration_rollback:0.5471 | 27 |
| untangling the package version standoff that kept breaking my install | python_dependency_conflict | 1 | python_dependency_conflict:0.6566<br>npm_dependency_resolution:0.6331<br>db_migration_rollback:0.6167 | 2 |
| chasing down why the interpreter swore a package wasn't there even ... | python_import_error | 2 | python_dependency_conflict:0.5256<br>python_import_error:0.5227<br>db_migration_rollback:0.5156 | 3 |
| that missing-module headache when running my code from the wrong place | python_import_error | 9 | npm_audit_fix:0.6139<br>git_undo_commit:0.5793<br>npm_cache_clear:0.5689 | 16 |
| figuring out which part of my script was dragging the whole thing down | python_profiling | 7 | git_undo_commit:0.5499<br>find_replace_sed:0.5209<br>db_migration_rollback:0.5122 | 53 |
| hunting the slow function that was eating all the runtime | python_profiling | 3 | find_large_old_files:0.5621<br>kill_process_on_port:0.5534<br>python_profiling:0.5446 | 1 |
| when the javascript package tree refused to install because require... | npm_dependency_resolution | 1 | npm_dependency_resolution:0.651<br>npm_audit_fix:0.619<br>python_dependency_conflict:0.5884 | 6 |
| forcing through the node module knot where nothing agreed on versions | npm_dependency_resolution | 1 | npm_dependency_resolution:0.6397<br>python_dependency_conflict:0.6357<br>npm_cache_clear:0.6115 | 1 |
| patching the flagged security holes in my node packages | npm_audit_fix | 1 | npm_audit_fix:0.7125<br>npm_dependency_resolution:0.6176<br>npm_cache_clear:0.6153 | 1 |
| dealing with the reported vulnerabilities in my javascript dependen... | npm_audit_fix | 1 | npm_audit_fix:0.6766<br>npm_cache_clear:0.5739<br>npm_dependency_resolution:0.57 | 3 |
| when a corrupted local package store gave me phantom build failures | npm_cache_clear | 2 | npm_audit_fix:0.6019<br>npm_cache_clear:0.5984<br>db_migration_rollback:0.5903 | 4 |
| wiping the download cache to get rid of bizarre install errors | npm_cache_clear | 1 | npm_cache_clear:0.6614<br>dns_cache_flush:0.629<br>disk_space_cleanup:0.6251 | 1 |
| setting up passwordless login so I'd stop typing my password to con... | ssh_key_setup | 1 | ssh_key_setup:0.5501<br>postgres_connection_refused:0.5084<br>nginx_ssl_cert:0.4762 | 1 |
| the time I created credentials to get into a remote machine without... | ssh_key_setup | 1 | ssh_key_setup:0.6287<br>distractor_02:0.5642<br>nginx_ssl_cert:0.5572 | 6 |
| making my local identity usable from a jump host to reach a machine... | ssh_agent_forwarding | 1 | ssh_agent_forwarding:0.6019<br>dns_debugging:0.5591<br>ssh_key_setup:0.5513 | 1 |
| when I needed my key to carry through to a second server down the line | ssh_agent_forwarding | 29 | ssh_key_setup:0.5095<br>db_migration_rollback:0.5027<br>ssh_permission_denied:0.495 | 26 |
| why the remote box kept rejecting me even though I had the right key | ssh_permission_denied | 2 | git_large_file_purge:0.5164<br>ssh_permission_denied:0.5062<br>ssh_key_setup:0.5033 | 7 |
| troubleshooting getting locked out when logging into a server | ssh_permission_denied | 14 | npm_audit_fix:0.5824<br>kill_process_on_port:0.5698<br>systemd_service_debug:0.567 | 5 |
| scheduling a script to run on its own every night | cron_job_setup | 1 | cron_job_setup:0.625<br>cron_job_debug:0.6146<br>distractor_09:0.5899 | 32 |
| setting something up to fire automatically on a repeating timer | cron_job_setup | 1 | cron_job_setup:0.6213<br>cron_job_debug:0.5616<br>distractor_09:0.5133 | 1 |
| why my scheduled task silently never actually ran | cron_job_debug | 2 | cron_job_setup:0.5976<br>cron_job_debug:0.5814<br>kill_process_on_port:0.5459 | 7 |
| chasing a background timer that just refused to trigger | cron_job_debug | 4 | postgres_connection_refused:0.5597<br>cron_job_setup:0.5505<br>kill_process_on_port:0.5497 | 6 |
| rolling the database structure forward to the newest version | db_migration_run | 2 | db_migration_rollback:0.656<br>db_migration_run:0.628<br>dns_cache_flush:0.5682 | 3 |
| applying the pending schema changes to my tables | db_migration_run | 1 | db_migration_run:0.6466<br>db_migration_rollback:0.5887<br>dns_cache_flush:0.5307 | 2 |
| undoing a structural change to the database that broke everything | db_migration_rollback | 1 | db_migration_rollback:0.6101<br>db_migration_run:0.5732<br>find_replace_sed:0.5469 | 2 |
| walking the table layout back after a bad update | db_migration_rollback | 1 | db_migration_rollback:0.6098<br>git_undo_commit:0.5654<br>db_migration_run:0.5516 | 8 |
| when the system refused to run my script until I changed its access... | chmod_permission_error | 1 | chmod_permission_error:0.6782<br>cron_job_debug:0.6429<br>ssh_permission_denied:0.6129 | 1 |
| fixing the you-are-not-allowed error trying to execute a file | chmod_permission_error | 1 | chmod_permission_error:0.6669<br>ssh_permission_denied:0.6113<br>kill_process_on_port:0.5883 | 1 |
| reclaiming a bunch of files that ended up belonging to the wrong ac... | sudo_ownership_fix | 13 | distractor_08:0.6071<br>distractor_06:0.5968<br>gpg_encrypt_file:0.5967 | 5 |
| when everything was locked because the superuser grabbed my directory | sudo_ownership_fix | 2 | ssh_permission_denied:0.6431<br>sudo_ownership_fix:0.6086<br>distractor_02:0.5788 | 3 |
| why a domain name just wouldn't resolve to an address on my machine | dns_debugging | 1 | dns_debugging:0.6721<br>dns_cache_flush:0.5982<br>docker_network_connect:0.5011 | 1 |
| chasing a name-lookup failure when trying to reach a site | dns_debugging | 1 | dns_debugging:0.668<br>dns_cache_flush:0.6318<br>docker_network_connect:0.5665 | 1 |
| when an old address kept sticking around long after it had changed | dns_cache_flush | 6 | dns_debugging:0.5026<br>find_replace_sed:0.498<br>db_migration_rollback:0.4821 | 10 |
| clearing the machine's memory of name lookups to pick up new records | dns_cache_flush | 1 | dns_cache_flush:0.6407<br>find_large_old_files:0.5635<br>find_replace_sed:0.5441 | 1 |
| that thing where the gateway wasn't picking up my configuration cha... | nginx_reverse_proxy | 7 | git_undo_commit:0.5557<br>dns_debugging:0.5327<br>git_large_file_purge:0.5278 | 45 |
| when the front server kept routing to the old backend after I edite... | nginx_reverse_proxy | 11 | npm_cache_clear:0.5651<br>npm_audit_fix:0.5599<br>git_undo_commit:0.5586 | 32 |
| renewing the expiring secure certificate so the browser lock icon s... | nginx_ssl_cert | 1 | nginx_ssl_cert:0.6086<br>git_large_file_purge:0.5285<br>systemd_service_debug:0.5237 | 3 |
| sorting out the https warning visitors were seeing on my site | nginx_ssl_cert | 6 | ssh_key_setup:0.534<br>ssh_agent_forwarding:0.5291<br>curl_api_debug:0.5276 | 2 |
| digging through the web server records to tally how often requests ... | log_parsing_grep | 11 | dns_cache_flush:0.6535<br>git_undo_commit:0.5907<br>dns_debugging:0.5707 | 32 |
| slicing a big log file to count the recurring errors | log_parsing_grep | 3 | cron_job_setup:0.6141<br>git_undo_commit:0.6036<br>log_parsing_grep:0.6004 | 16 |
| when runaway log files were quietly eating up all the disk | log_rotation | 1 | log_rotation:0.5938<br>git_undo_commit:0.5508<br>distractor_04:0.5328 | 1 |
| keeping the ever-growing application output from filling storage | log_rotation | 4 | distractor_09:0.6256<br>docker_disk_prune:0.6195<br>distractor_04:0.6085 | 20 |
| tracking down what exactly was hogging all my storage when the driv... | disk_space_cleanup | 24 | log_rotation:0.5695<br>dns_cache_flush:0.5535<br>gpg_encrypt_file:0.5504 | 4 |
| hunting the culprit files that ate the free space on my machine | disk_space_cleanup | 7 | log_rotation:0.6066<br>find_large_old_files:0.5809<br>gpg_encrypt_file:0.5624 | 38 |
| why a background service kept dying right after it started at boot | systemd_service_debug | 1 | systemd_service_debug:0.6328<br>postgres_connection_refused:0.6019<br>kill_process_on_port:0.6004 | 4 |
| chasing a daemon that just would not stay running | systemd_service_debug | 2 | postgres_connection_refused:0.5659<br>systemd_service_debug:0.5452<br>kill_process_on_port:0.5366 | 2 |
| bundling an entire folder into a single compressed file to move it ... | tar_backup | 3 | distractor_04:0.6563<br>distractor_05:0.6309<br>tar_backup:0.6186 | 6 |
| packing up a directory into one archive for safekeeping | tar_backup | 2 | distractor_05:0.6798<br>tar_backup:0.6764<br>gpg_encrypt_file:0.6623 | 1 |
| figuring out why a workload kept restarting over and over in the cl... | kubectl_pod_debug | 2 | systemd_service_debug:0.5617<br>kubectl_pod_debug:0.5517<br>distractor_09:0.5517 | 1 |
| chasing a crashing container managed by the orchestrator | kubectl_pod_debug | 3 | docker_compose_stack:0.5977<br>kill_process_on_port:0.5948<br>kubectl_pod_debug:0.5817 | 1 |
| mirroring a directory up to a remote server while only sending what... | rsync_transfer | 1 | rsync_transfer:0.7152<br>distractor_02:0.659<br>distractor_08:0.6517 | 4 |
| efficiently copying just the modified files over to another machine | rsync_transfer | 4 | distractor_08:0.644<br>distractor_01:0.6232<br>distractor_06:0.6104 | 26 |
| renaming one identifier across every file in the project in a singl... | find_replace_sed | 1 | find_replace_sed:0.6158<br>distractor_10:0.5878<br>distractor_08:0.5869 | 2 |
| doing a bulk text swap through a whole codebase at once | find_replace_sed | 1 | find_replace_sed:0.6242<br>db_migration_rollback:0.5617<br>distractor_04:0.5602 | 1 |
| when a program wasn't being found until I fixed where the shell loo... | env_var_debug | 15 | dns_debugging:0.5561<br>distractor_09:0.556<br>dns_cache_flush:0.5501 | 8 |
| getting an environment setting to stick around across new terminal ... | env_var_debug | 47 | tmux_session:0.6585<br>distractor_09:0.6021<br>distractor_00:0.5971 | 37 |
| when my app couldn't reach the database and kept getting turned awa... | postgres_connection_refused | 1 | postgres_connection_refused:0.55<br>db_migration_rollback:0.5105<br>systemd_service_debug:0.4768 | 21 |
| sorting out the data store refusing my local connections until I ed... | postgres_connection_refused | 5 | ssh_permission_denied:0.5774<br>disk_space_cleanup:0.564<br>dns_cache_flush:0.5598 | 13 |
| when something was already squatting on the address my server neede... | kill_process_on_port | 8 | dns_debugging:0.5593<br>dns_cache_flush:0.5502<br>log_rotation:0.5143 | 15 |
| freeing up a busy network endpoint that a leftover process was stil... | kill_process_on_port | 1 | kill_process_on_port:0.6067<br>distractor_09:0.5879<br>distractor_02:0.5705 | 3 |
| poking at a web endpoint by hand to see what it was actually sendin... | curl_api_debug | 2 | git_undo_commit:0.5812<br>curl_api_debug:0.5764<br>nginx_ssl_cert:0.5617 | 8 |
| inspecting the raw reply from a remote service while it was misbeha... | curl_api_debug | 3 | git_undo_commit:0.5575<br>dns_cache_flush:0.5327<br>curl_api_debug:0.5178 | 46 |
| keeping my remote work alive so it survived me getting disconnected | tmux_session | 1 | tmux_session:0.5968<br>systemd_service_debug:0.5355<br>rsync_transfer:0.5254 | 1 |
| getting back into the exact same terminal workspace after logging out | tmux_session | 1 | tmux_session:0.6574<br>git_undo_commit:0.5979<br>distractor_09:0.5621 | 1 |
| locating files by how big or how old they were across a whole tree | find_large_old_files | 3 | find_replace_sed:0.5897<br>distractor_00:0.566<br>find_large_old_files:0.5652 | 28 |
| tracking down specific files buried deep somewhere in a directory | find_large_old_files | 7 | gpg_encrypt_file:0.667<br>dns_cache_flush:0.6271<br>distractor_05:0.6158 | 10 |
| locking a sensitive document behind a passphrase before handing it off | gpg_encrypt_file | 1 | gpg_encrypt_file:0.6676<br>cron_job_debug:0.5228<br>ssh_key_setup:0.5188 | 1 |
| scrambling a file so only someone with the secret word could read it | gpg_encrypt_file | 1 | gpg_encrypt_file:0.645<br>ssh_permission_denied:0.5427<br>distractor_06:0.5351 | 1 |

## Null queries (no correct session): top-1 returned

| Query | Sem top-1 (id:score) | KW top-1 (id:score) |
|---|---|---|
| when I set up the jenkins continuous integration pipeline | kubectl_pod_debug:0.5574 | distractor_12:1.0036 |
| configuring terraform to provision cloud infrastructure | dns_cache_flush:0.5499 | tmux_session:0.0258 |
| that time I fought the rust compiler's borrow checker | npm_audit_fix:0.5203 | kubectl_pod_debug:0.0295 |
| tuning the elasticsearch cluster shard allocation | kubectl_pod_debug:0.5669 | kubectl_pod_debug:1.0258 |
| setting up the redis pub sub messaging channels | docker_network_connect:0.5622 | docker_network_connect:1.0064 |
| writing the ansible playbook to configure the fleet | distractor_09:0.5471 | db_migration_run:0.027 |
| debugging the graphql resolver n plus one queries | dns_cache_flush:0.6368 | git_undo_commit:0.0284 |
| enabling two factor authentication on my account | ssh_key_setup:0.5051 | ssh_key_setup:1.0015 |
| training the neural network on the gpu cluster | python_profiling:0.4917 | kubectl_pod_debug:1.0183 |
| configuring the bluetooth audio device pairing | npm_dependency_resolution:0.483 | env_var_debug:0.0254 |

## Keyword-heavy queries breakout (exact tool names / flags)

*15 queries using exact keywords from target sessions (opposite of the standard eval design). Reported separately — not merged into the answerable aggregate.*

| Method | P@1 | P@3 | P@5 | R@5 | R@10 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic | 1.000 | 0.333 | 0.200 | 1.000 | 1.000 | 1.000 | 1.000 |
| keyword | 0.933 | 0.333 | 0.200 | 1.000 | 1.000 | 0.967 | 0.975 |

| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |
|---|---|--:|---|--:|
| cProfile pstats snakeviz profiling hotspot | python_profiling | 1 | python_profiling:0.0328<br>kill_process_on_port:0.0323<br>rsync_transfer:0.0317 | 1 |
| python3 -m venv activate pip install requirements.txt | python_venv_setup | 1 | python_venv_setup:0.0328<br>python_dependency_conflict:0.0323<br>python_import_error:0.0317 | 1 |
| git filter-branch --force git rm --cached secrets.env reflog gc prune | git_large_file_purge | 1 | git_large_file_purge:0.0328<br>git_undo_commit:0.0323<br>npm_cache_clear:0.0315 | 1 |
| git rebase origin/main --force-with-lease conflict | git_rebase_conflict | 1 | git_rebase_conflict:0.0328<br>git_large_file_purge:0.032<br>git_merge_conflict:0.0318 | 1 |
| docker volume inspect pgdata postgres persist | docker_volume_mount | 1 | docker_volume_mount:0.0328<br>docker_disk_prune:0.0323<br>docker_compose_stack:0.031 | 1 |
| alembic upgrade head revision migrate | db_migration_run | 1 | db_migration_run:0.0328<br>db_migration_rollback:0.0323<br>git_undo_commit:0.0315 | 1 |
| alembic downgrade revision rollback | db_migration_rollback | 1 | db_migration_rollback:0.0328<br>db_migration_run:0.0323<br>git_undo_commit:0.0317 | 1 |
| crontab -e cron.d */5 scheduled job | cron_job_setup | 1 | cron_job_setup:0.7574<br>cron_job_debug:0.7428<br>distractor_09:0.656 | 1 |
| curl -v -s jq json api endpoint response | curl_api_debug | 1 | curl_api_debug:0.0328<br>nginx_reverse_proxy:0.0311<br>db_migration_rollback:0.0308 | 1 |
| lsof -i kill -9 port 8080 process pid | kill_process_on_port | 1 | kill_process_on_port:0.0328<br>nginx_reverse_proxy:0.032<br>disk_space_cleanup:0.031 | 2 |
| tmux new-session attach-session detach | tmux_session | 1 | tmux_session:0.8219<br>git_undo_commit:0.516<br>kill_process_on_port:0.5101 | 1 |
| ssh-keygen authorized_keys ssh-copy-id id_rsa | ssh_key_setup | 1 | ssh_key_setup:0.7914<br>ssh_permission_denied:0.6357<br>distractor_02:0.6325 | 1 |
| gpg --symmetric --passphrase encrypt file decrypt | gpg_encrypt_file | 1 | gpg_encrypt_file:0.7749<br>distractor_04:0.5593<br>cron_job_debug:0.5545 | 1 |
| resolvectl flush-caches dns nameserver resolv.conf | dns_cache_flush | 1 | dns_cache_flush:0.0328<br>dns_debugging:0.0323<br>docker_network_connect:0.0317 | 1 |
| tar czf archive.tar.gz compress extract directory | tar_backup | 1 | tar_backup:0.0328<br>distractor_01:0.0317<br>distractor_05:0.0291 | 1 |
