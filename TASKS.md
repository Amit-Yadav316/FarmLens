# FarmLens â€” Task Tracker

## Current Status
Day 1 âœ” | Day 2 âœ” | Day 3 âœ” | Day 4 âœ” | Day 5 next

---

## Today's Goal
Create the complete folder structure with empty files.
Set up pyproject.toml with uv.
Verify `uv sync` installs everything cleanly.
NO feature code today â€” structure only.

---

## Day 1 Checklist

### Environment Setup
- [x] Install uv: `pip install uv`
- [x] Create new venv: `uv venv --python 3.11`
- [x] Activate: `.venv\Scripts\activate`
- NOTE: On OneDrive, always run with `$env:UV_LINK_MODE="copy"` before `uv sync`

### Files to Create Today

#### Root files
- [x] pyproject.toml
- [x] .env (already exists with keys)
- [x] .env.example
- [x] .gitignore
- [x] CLAUDE.md (done)
- [x] TASKS.md (this file)

#### farmlens/ package
- [x] farmlens/__init__.py
- [x] farmlens/core/__init__.py
- [x] farmlens/core/config.py
- [x] farmlens/core/exceptions.py
- [x] farmlens/core/dependencies.py
- [x] farmlens/core/logging.py
- [x] farmlens/features/__init__.py
- [x] farmlens/features/asr/__init__.py
- [x] farmlens/features/asr/service.py
- [x] farmlens/features/asr/schemas.py
- [x] farmlens/features/asr/exceptions.py
- [x] farmlens/features/mandi/__init__.py
- [x] farmlens/features/mandi/service.py
- [x] farmlens/features/mandi/schemas.py
- [x] farmlens/features/mandi/exceptions.py
- [x] farmlens/features/mandi/constants.py
- [x] farmlens/features/weather/__init__.py
- [x] farmlens/features/weather/service.py
- [x] farmlens/features/weather/schemas.py
- [x] farmlens/features/weather/exceptions.py
- [x] farmlens/features/weather/constants.py
- [x] farmlens/features/rag/__init__.py
- [x] farmlens/features/rag/pipeline.py
- [x] farmlens/features/rag/ingestion.py
- [x] farmlens/features/rag/schemas.py
- [x] farmlens/features/rag/exceptions.py
- [x] farmlens/features/schemes/__init__.py
- [x] farmlens/features/schemes/service.py
- [x] farmlens/features/schemes/schemas.py
- [x] farmlens/features/schemes/data.py
- [x] farmlens/features/intent/__init__.py
- [x] farmlens/features/intent/router.py
- [x] farmlens/features/intent/schemas.py
- [x] farmlens/features/intent/constants.py
- [x] farmlens/api/__init__.py
- [x] farmlens/api/app.py
- [x] farmlens/api/middleware.py
- [x] farmlens/api/routes/__init__.py
- [x] farmlens/api/routes/chat.py
- [x] farmlens/api/routes/health.py
- [x] farmlens/api/routes/data.py
- [x] farmlens/frontend/app.py
- [x] farmlens/frontend/gradio_app.py
- [x] farmlens/scripts/ingest_pdfs.py
- [x] farmlens/scripts/prepare_kcc.py

#### tests/
- [x] tests/__init__.py
- [x] tests/conftest.py
- [x] tests/unit/__init__.py
- [x] tests/unit/test_mandi_service.py
- [x] tests/unit/test_weather_service.py
- [x] tests/unit/test_rag_pipeline.py
- [x] tests/unit/test_intent_router.py
- [x] tests/integration/__init__.py
- [x] tests/integration/test_api.py

#### data/
- [x] data/pdfs/.gitkeep
- [x] data/crop_map.json
- [x] data/location_map.json
- [x] data/schemes.json

### Verify at end of Day 1
- [x] `uv sync` runs without errors (183 packages resolved, UV_LINK_MODE=copy required for OneDrive)
- [x] `python -c "import farmlens; print('OK')"` works
- [x] `pytest tests/ --collect-only` finds all 7 test files
- [x] `git status` does NOT show .env file

---

## Day 2 Plan â€” COMPLETE âœ”
- [x] farmlens/core/config.py â€” Settings class (+ mandi_resource_id)
- [x] farmlens/core/exceptions.py â€” exception hierarchy
- [x] farmlens/features/mandi/service.py â€” MandiService class
- [x] farmlens/features/mandi/constants.py â€” multilingual CROP_MAP + LOCATION_MAP
- [x] tests/unit/test_mandi_service.py â€” 10 tests, all passing

---

## Day 3 Plan â€” COMPLETE âœ”
- [x] farmlens/features/weather/service.py â€” WeatherService (forecast + spray rules)
- [x] farmlens/features/asr/service.py â€” ASRService (lazy Whisper, BytesIO input)
- [x] tests/unit/test_weather_service.py â€” 9 tests passing
- [x] tests/unit/test_asr_service.py â€” 7 tests passing (created new file)
- Total: 26 unit tests passing across mandi + weather + asr

---

## Day 4 Plan â€” COMPLETE âœ”
- [x] farmlens/features/rag/ingestion.py â€” PDFIngestion (PyPDFLoader + RecursiveCharacterTextSplitter + ChromaDB)
- [x] farmlens/features/rag/pipeline.py â€” RAGPipeline (HuggingFaceEmbeddings + RetrievalQA + OllamaLLM)
- [x] tests/unit/test_rag_pipeline.py â€” 12 tests passing (RAGPipeline + PDFIngestion)
- [x] farmlens/scripts/ingest_pdfs.py â€” already wired, calls PDFIngestion.run()
- NOTE: Place ICAR PDFs in data/pdfs/ and run `uv run python farmlens/scripts/ingest_pdfs.py` to populate ChromaDB

---

## Day 5 Plan
- farmlens/features/intent/router.py â€” IntentRouter class
- farmlens/features/schemes/service.py â€” SchemeService class
- farmlens/api/app.py â€” FastAPI app
- farmlens/api/routes/ â€” all routes
- Goal: Full API running at localhost:8000

---

## Day 6 Plan
- farmlens/frontend/app.py â€” Streamlit UI
- End-to-end test: voice â†’ answer
- Goal: Working local demo

---

## Day 7 Plan
- Kaggle: Train EfficientNet on PlantVillage
- farmlens/features/disease/ folder
- Goal: Disease model weights downloaded

---

## Day 8 Plan
- Connect disease detection to pipeline
- Goal: Photo â†’ Hindi diagnosis

---

## Day 9 Plan
- Kaggle: Fine-tune Mistral on KCC dataset
- Load LoRA adapter
- Goal: Better Hindi farming responses

---

## Day 10 Plan
- farmlens/frontend/gradio_app.py
- HuggingFace Spaces deployment
- README with architecture diagram
- Demo video
- Goal: Public URL live

---

## Completed Days
(move items here as you finish them)

---

## Blockers
(add anything blocking you here so Claude can help)
