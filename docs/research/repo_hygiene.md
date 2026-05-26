# Repo Hygiene Audit

## Purpose

The Post-Unicorn Finance repo has several local automations that can create legitimate working-tree churn. Evidence CSVs, local exports, learning queues, packet files, and code changes should not be treated the same way.

`scripts/repo_hygiene.py` has two modes:

- audit mode categorizes dirty files and writes a local report,
- autonomous cleanup mode runs promotion/validation, creates category-separated commits, and can push to GitHub.

## Command

```powershell
python scripts/repo_hygiene.py
```

Optional ignored-file visibility:

```powershell
python scripts/repo_hygiene.py --include-ignored
```

Autonomous dry-run:

```powershell
python scripts/repo_hygiene.py autonomous-cleanup --promotion-limit 10 --push --dry-run
```

Autonomous cleanup and push:

```powershell
python scripts/repo_hygiene.py autonomous-cleanup --promotion-limit 10 --push
```

## Outputs

Reports are written under ignored exports:

- `data/exports/repo_hygiene_status.json`
- `data/exports/repo_hygiene_status.md`

## Categories

- `evidence_csv_churn`: tracked atlas evidence changes under `data/evidence`.
- `publish_site`: public packet files under `site`.
- `code`: script changes.
- `tests`: test changes.
- `docs_or_repo_config`: docs, README, or repo config changes.
- `github_workflow`: GitHub workflow/config changes.
- `local_exports`: local generated exports.
- `local_runtime_or_learning`: local run state, learning queues, and runtime artifacts.
- `local_database`: SQLite files.
- `ignored_generated`: ignored caches and generated files.
- `other_dirty`: anything that needs manual classification.

## Autonomous Cleanup Policy

Autonomous cleanup:

- acquires the shared automation lock,
- fetches `origin`,
- fast-forwards only when the local branch is behind,
- runs intake promotion before committing evidence,
- validates evidence, SQLite, and tests before committing,
- refuses pre-staged changes,
- refuses unknown dirty files,
- creates separate commits for evidence, site, and repo changes,
- pushes to `origin/main` only when `--push` is passed.

Autonomous cleanup never deletes, resets, stashes, rebases, force-pushes, or commits ignored generated outputs.

Evidence files are research artifacts, not disposable cache. A future destructive cleanup policy should only apply to clearly ignored generated files, such as caches, and should still leave an audit report.

## Recommended Workflow

1. Run the hygiene audit.
2. Run evidence and SQLite validation.
3. For autonomous cleanup, dry-run first if the category mix changed.
4. Commit evidence snapshots separately from code/docs/test changes.
5. Publish `site/` only through the guarded publisher or this hygiene command after validation.
6. Leave generated exports, runtime files, SQLite files, and learning queue outputs ignored.
