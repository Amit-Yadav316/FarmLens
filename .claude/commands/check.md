Run a full pre-commit health check on FarmLens before pushing.

Steps:
1. Lint: `uv run ruff check farmlens/`
2. Format: `uv run ruff format --check farmlens/`
3. Type check: `uv run mypy farmlens/`
4. Unit tests: `uv run pytest tests/unit/ -v --tb=short`
5. Print a final PASS/FAIL summary.

Stop and report immediately if any step fails — do not continue to the next step.
This is the gate before any git push or PR creation.
