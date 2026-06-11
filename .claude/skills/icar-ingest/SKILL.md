---
name: icar-ingest
description: Ingest ICAR PDFs into ChromaDB for the RAG pipeline. Use when the user wants to load, re-ingest, or refresh the document corpus.
---

# Ingest ICAR PDFs into ChromaDB

Loads the ICAR PDF corpus into the Chroma vector store that powers RAG.

## Steps

1. Confirm PDFs exist:
   - They must be in `data/pdfs/` as `*.pdf`. If the directory is empty, stop
     and tell the user — ingestion will raise `RAGException("No PDFs found")`.
2. Run ingestion:
   ```
   uv run python farmlens/scripts/ingest_pdfs.py
   ```
   - On OneDrive, prefix with `$env:UV_LINK_MODE="copy"` (PowerShell) to avoid
     hardlink errors.
3. Report the chunk count printed at the end.
   - 0 chunks = a scanned/empty PDF or wrong directory — flag it, do not treat
     as success.

## Notes

- Ingestion appends to the existing Chroma DB at the path in `CHROMA_DB_PATH`
  (default `./data/chroma_db`). To rebuild from scratch, delete that directory
  first, then re-run.
- The pipeline is PyPDFLoader + RecursiveCharacterTextSplitter (500/50) +
  HuggingFaceEmbeddings (paraphrase-multilingual-MiniLM-L12-v2) + Chroma.
  See `farmlens/features/rag/ingestion.py`.
- Tables in ICAR PDFs are not chunked well by the current splitter — this is a
  known limitation tracked under the Phase 2 RAG chunking strategy in TASKS.md.
- No external API keys are needed for ingestion; embeddings run locally.
