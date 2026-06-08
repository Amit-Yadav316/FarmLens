Run code quality checks on the FarmLens codebase.

Steps:
1. Ruff lint: `uv run ruff check farmlens/`
2. Ruff format check: `uv run ruff format --check farmlens/`
3. Type check: `uv run mypy farmlens/`

If $ARGUMENTS contains "fix", also run:
- `uv run ruff check --fix farmlens/`
- `uv run ruff format farmlens/`

Report any errors clearly. Do not auto-fix unless "fix" is passed.
