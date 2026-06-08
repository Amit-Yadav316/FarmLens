# FarmLens — Task Tracker

## Current Status
Day 1 of 10 — Project skeleton

---

## Today's Goal
Create the complete folder structure with empty files.
Set up pyproject.toml with uv.
Verify `uv sync` installs everything cleanly.
NO feature code today — structure only.

---

## Day 1 Checklist

### Environment Setup
- [ ] Install uv: `pip install uv`
- [ ] Delete old venv: `Remove-Item -Recurse -Force .venv`
- [ ] Create new venv: `uv venv --python 3.11`
- [ ] Activate: `.venv\Scripts\activate`

### Files to Create Today

#### Root files
- [ ] pyproject.toml
- [ ] .env (copy from .env.example, fill in keys)
- [ ] .env.example
- [ ] .gitignore
- [ ] CLAUDE.md (done)
- [ ] TASKS.md (this file)

#### farmlens/ package
- [ ] farmlens/__init__.py
- [ ] farmlens/core/__init__.py
- [ ] farmlens/core/config.py
- [ ] farmlens/core/exceptions.py
- [ ] farmlens/core/dependencies.py
- [ ] farmlens/core/logging.py
- [ ] farmlens/features/__init__.py
- [ ] farmlens/features/asr/__init__.py
- [ ] farmlens/features/asr/service.py
- [ ] farmlens/features/asr/schemas.py
- [ ] farmlens/features/asr/exceptions.py
- [ ] farmlens/features/mandi/__init__.py
- [ ] farmlens/features/mandi/service.py
- [ ] farmlens/features/mandi/schemas.py
- [ ] farmlens/features/mandi/exceptions.py
- [ ] farmlens/features/mandi/constants.py
- [ ] farmlens/features/weather/__init__.py
- [ ] farmlens/features/weather/service.py
- [ ] farmlens/features/weather/schemas.py
- [ ] farmlens/features/weather/exceptions.py
- [ ] farmlens/features/weather/constants.py
- [ ] farmlens/features/rag/__init__.py
- [ ] farmlens/features/rag/pipeline.py
- [ ] farmlens/features/rag/ingestion.py
- [ ] farmlens/features/rag/schemas.py
- [ ] farmlens/features/rag/exceptions.py
- [ ] farmlens/features/schemes/__init__.py
- [ ] farmlens/features/schemes/service.py
- [ ] farmlens/features/schemes/schemas.py
- [ ] farmlens/features/schemes/data.py
- [ ] farmlens/features/intent/__init__.py
- [ ] farmlens/features/intent/router.py
- [ ] farmlens/features/intent/schemas.py
- [ ] farmlens/features/intent/constants.py
- [ ] farmlens/api/__init__.py
- [ ] farmlens/api/app.py
- [ ] farmlens/api/middleware.py
- [ ] farmlens/api/routes/__init__.py
- [ ] farmlens/api/routes/chat.py
- [ ] farmlens/api/routes/health.py
- [ ] farmlens/api/routes/data.py
- [ ] farmlens/frontend/app.py
- [ ] farmlens/frontend/gradio_app.py
- [ ] farmlens/scripts/ingest_pdfs.py
- [ ] farmlens/scripts/prepare_kcc.py

#### tests/
- [ ] tests/__init__.py
- [ ] tests/conftest.py
- [ ] tests/unit/__init__.py
- [ ] tests/unit/test_mandi_service.py
- [ ] tests/unit/test_weather_service.py
- [ ] tests/unit/test_rag_pipeline.py
- [ ] tests/unit/test_intent_router.py
- [ ] tests/integration/__init__.py
- [ ] tests/integration/test_api.py

#### data/
- [ ] data/pdfs/.gitkeep
- [ ] data/crop_map.json
- [ ] data/location_map.json
- [ ] data/schemes.json

### Verify at end of Day 1
- [ ] `uv sync` runs without errors
- [ ] `python -c "import farmlens; print('OK')"` works
- [ ] `pytest tests/ --collect-only` finds all test files
- [ ] `git status` does NOT show .env file

---

## Day 2 Plan (tomorrow)
- farmlens/core/config.py — Settings class
- farmlens/core/exceptions.py — exception hierarchy
- farmlens/features/mandi/service.py — MandiService class
- farmlens/features/mandi/constants.py — crop_map, location_map
- tests/unit/test_mandi_service.py
- Goal: `pytest tests/unit/test_mandi_service.py` all passing

---

## Day 3 Plan
- farmlens/features/weather/service.py — WeatherService class
- farmlens/features/asr/service.py — ASRService class
- Tests for both
- Goal: mandi + weather + asr all tested

---

## Day 4 Plan
- farmlens/features/rag/pipeline.py — RAGPipeline class
- farmlens/features/rag/ingestion.py — PDFIngestion class
- farmlens/scripts/ingest_pdfs.py
- Download ICAR PDFs
- Goal: ChromaDB populated, RAG answers working

---

## Day 5 Plan
- farmlens/features/intent/router.py — IntentRouter class
- farmlens/features/schemes/service.py — SchemeService class
- farmlens/api/app.py — FastAPI app
- farmlens/api/routes/ — all routes
- Goal: Full API running at localhost:8000

---

## Day 6 Plan
- farmlens/frontend/app.py — Streamlit UI
- End-to-end test: voice → answer
- Goal: Working local demo

---

## Day 7 Plan
- Kaggle: Train EfficientNet on PlantVillage
- farmlens/features/disease/ folder
- Goal: Disease model weights downloaded

---

## Day 8 Plan
- Connect disease detection to pipeline
- Goal: Photo → Hindi diagnosis

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
