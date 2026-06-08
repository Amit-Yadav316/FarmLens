Run the full test suite for FarmLens.

Steps:
1. Run unit tests: `uv run pytest tests/unit/ -v`
2. If $ARGUMENTS contains "all", also run: `uv run pytest tests/integration/ -v`
3. Show a summary of passed/failed/skipped counts.

Do not call real external APIs — unit tests must use mocks only.
