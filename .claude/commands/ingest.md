Run the PDF ingestion pipeline to load ICAR documents into ChromaDB.

Steps:
1. Check that `data/pdfs/` exists and contains at least one PDF file.
2. Run: `uv run python scripts/ingest_pdfs.py`
3. Report how many chunks were created and confirm ChromaDB was updated at `$CHROMA_DB_PATH`.

Warn the user if `data/pdfs/` is empty or missing before running.
