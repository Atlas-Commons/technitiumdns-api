# Branch protection for `main`

Merging to `main` requires passing CI and a pull request. Configuration lives in
this repository so it can be reviewed and re-applied consistently.

## What runs on every PR and push to `main`

Workflow: [`.github/workflows/ci.yml`](workflows/ci.yml)

| Job | Purpose |
|-----|---------|
| **Lint (ruff + mypy)** | Style, imports, static types |
| **Test (Python 3.11–3.13)** | Unit tests + coverage |
| **Build sdist & wheel** | Package builds and passes `twine check` |
| **Required checks** | Gate job — fails if any job above failed |

The ruleset requires the **Required checks** status to be green before merge.

Release tags (`v*`) use [`.github/workflows/release.yml`](workflows/release.yml),
which runs the same quality checks before publishing to PyPI.

## Apply the ruleset (one-time, after creating the GitHub repo)

GitHub rulesets are configured on the repository, not via git push. Use the
included script:

```bash
chmod +x .github/scripts/apply-main-ruleset.sh
./.github/scripts/apply-main-ruleset.sh Amateur-God technitiumdns-api
```

Or manually in the GitHub UI:

1. **Settings → Rules → Rulesets → New ruleset → New branch ruleset**
2. **Ruleset name:** `Protect main`
3. **Enforcement:** Active
4. **Bypass list:** leave empty (or add org admins only)
5. **Target branches:** `main`
6. Enable rules:
   - **Require a pull request before merging** (0 approvals is fine for solo work)
   - **Require status checks to pass** → add **`Required checks`**
   - **Require branches to be up to date before merging**
   - **Block force pushes**
   - **Restrict deletions**
7. Save

### Important: check name must exist first

GitHub only lets you select status checks that have run at least once. After the
repo exists:

1. Push a branch and open a PR against `main`, **or**
2. Push to `main` once before enabling the ruleset

Then apply the ruleset (script or UI).

## Ruleset definition (as code)

See [`.github/rulesets/main.json`](rulesets/main.json):

- Pull requests required before merge to `main`
- **`Required checks`** must pass (strict: branch must be up to date)
- Force-push blocked
- Deleting `main` blocked

## Optional: require approval

For team repos, edit `.github/rulesets/main.json`:

```json
"required_approving_review_count": 1
```

Re-run `apply-main-ruleset.sh`.

## Local checks before opening a PR

```bash
pip install -e ".[dev]"
ruff check src tests
ruff format --check src tests
mypy src
pytest
python -m build && twine check dist/*
```
