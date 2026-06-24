# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Read-only(+ targeted write) CLI scripts for querying and managing Okta via the Admin API: group membership, app assignment, single-user lookup, group intersections, removing/adding users to groups, and cross-checking Google Workspace CSV exports against Okta. All comments/docs are in Korean; preserve that convention.

## Commands

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in OKTA_DOMAIN, OKTA_API_TOKEN

python check_data.py group "<group-name>"
python check_data.py app "<app-label>"
python check_data.py user <email>
python group_intersection.py "<group-a>" "<group-b>"
python remove_from_group.py --remove-from "<group>" --keep-in "<group>" [--apply]
python migrate_group.py --emails-file <file> --add-to "<group>" --remove-from "<group>" ... [--apply]
python check_us_subsidiary_okta.py <google_export.csv>
```

No test suite or linter configured.

## Architecture

All scripts share `okta_client.py`'s `OktaClient` — a thin wrapper over the Okta REST API (`/api/v1`) using `SSWS` token auth, loaded from `.env` via `python-dotenv`. Group name lookups (`find_group_by_name`) match case-insensitively because Okta's `q` search is a prefix match and real group names don't always match the casing a caller types.

Each top-level script is a single-purpose CLI built on `OktaClient`:
- `check_data.py` — ad-hoc single lookups (group members / app users / one user)
- `group_intersection.py` — read-only set intersection of two groups' members
- `remove_from_group.py` / `migrate_group.py` — **mutating** operations. Both default to a dry-run preview and only write when `--apply` is passed. `migrate_group.py` is the more general form: add a list of users (by email, one per line in a file) to one group and remove them from a list of other groups, used e.g. for consolidating `app-atl-confluence-partner`/`-user` access into `-subsidiary`.
- `check_us_subsidiary_okta.py` — cross-references a Google Workspace Admin user-list CSV export against Okta by assuming the email local-part (before `@`) is identical between Google (`@oliveyoung.co.kr`) and Okta (`@oliveyoung.co.kr` or `@cj.net`); Google and Okta are not otherwise integrated.

**Any new script that writes to Okta (group membership, user creation/removal) must follow the dry-run-by-default + `--apply` pattern** established in `remove_from_group.py` and `migrate_group.py` — this is a deliberate safety convention for this repo, not incidental.

Real personnel data (CSV exports, `*_emails.txt` lists) is gitignored — never commit it.

## Working principles

**Think before coding.** State assumptions explicitly (e.g. which group, which environment, which OU/domain a request implies). If a request is ambiguous — which accounts count as "these people", whether a removal should also touch a related group — ask rather than guessing, especially before any mutating operation.

**Simplicity first.** Write the minimal script/function that solves the stated request. Don't add config options, abstractions, or error handling for cases that aren't in play. If it looks like something a senior engineer would call overcomplicated for what was asked, simplify it.

**Surgical changes.** When editing an existing script, touch only what the task requires — don't reformat or "improve" unrelated code, don't change style in untouched lines. Only delete code that your own change made dead.

**Goal-driven, verify before declaring done.** For data checks or mutations, prefer a verification step (e.g. re-run `group_intersection.py` after a removal) over assuming the API call succeeded. Treat mutating Okta operations as requiring explicit user confirmation before `--apply`, even if a dry-run was already shown.
