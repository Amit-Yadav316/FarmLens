Start the FarmLens FastAPI development server.

Steps:
1. Verify `.env` exists. If not, tell the user to copy `.env.example` to `.env` and fill in their API keys.
2. Start the server: `uv run uvicorn farmlens.api.app:app --reload --host 0.0.0.0 --port 8000`
3. The API docs will be available at http://localhost:8000/docs

If $ARGUMENTS contains "ui", also start the Streamlit frontend in a second terminal:
`uv run streamlit run farmlens/frontend/app.py`
