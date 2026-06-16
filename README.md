---
title: FarmLens
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# FarmLens 

**A multilingual, voice-first AI advisory for Indian farmers.** Ask about crop
practices, mandi prices, weather, and government schemes — and get a clear answer
in Hindi.

**Live demo:** https://huggingface.co/spaces/amity838/farmlens
*(Free CPU tier — tool tabs respond instantly; the first chat answer is slow
while the model loads, then ~30–60s each.)*

---

## The problem

India's small and marginal farmers often have low literacy and limited access to
timely, trustworthy agricultural advice. Generic chatbots **hallucinate** — and a
wrong fertilizer dose or spray window can cost a season's crop.

## Core principle: never hallucinate

FarmLens separates **facts** from **language**:

- **Facts** come from real sources — ICAR documents (via RAG), live government
  APIs (mandi prices, weather), and a curated schemes list. If the answer is not
  in the sources, the model says it does not know.
- **Language and tone** come from a **fine-tuned Hindi model** (Airavata), so
  answers read naturally to a farmer without inventing facts.

---

## Phase 1 — what's built

| Capability | What it does | Powered by |
|---|---|---|
| Hindi Q&A from ICAR docs | Answers crop questions grounded in official documents | RAG — ChromaDB + multilingual embeddings + Hindi prompt |
| Natural Hindi tone | Reads like a real advisor, not a machine translation | Fine-tuned Airavata (Unsloth + QLoRA, exported to GGUF) |
| Live mandi prices | Latest market rates by crop and state | Agmarknet (data.gov.in) API |
| Weather and spray advisory | Forecast plus whether it is safe to spray today | OpenWeatherMap + spray-safety rules |
| Government schemes | Surfaces schemes relevant to a query | Curated list + keyword ranking |
| Voice input | Lets a farmer ask by speaking | Whisper ASR (`/voice-chat`) |
| Intent routing | Sends each question to the right handler | Keyword classifier |
| Swappable LLM backend | Runs fast locally, or self-contained on CPU | Ollama or llama.cpp |
| Two UIs | Public web demo and a local app | Gradio and Streamlit |
| Quality | Tested, typed, strict architecture | 61 tests, `ruff` + `mypy` clean |

### How a question flows

```
   farmer (Hindi text / voice)
            |
            v
     +--------------+        price / weather / scheme intent
     | intent router| ---------------------------------------+
     +--------------+                                         |
            | general / disease                               v
            v                                          +--------------+
     +--------------+      ICAR docs (facts)           |    tools     |
     | RAG pipeline | <------ ChromaDB                  |  Mandi price |
     +--------------+                                   |  Weather     |
            |                                           |  Schemes     |
            v                                           +--------------+
     +-----------------------+                          (live data,
     | LLM (Airavata, Hindi) |                           no hallucination)
     +-----------------------+
            |
            v
     grounded Hindi answer
```

---

## Tech stack

- **Backend:** FastAPI — service-class architecture, dependency injection, a
  custom exception hierarchy
- **RAG:** LangChain, ChromaDB, `paraphrase-multilingual-MiniLM` embeddings
- **LLM:** Airavata GGUF — served via Ollama (local) or llama-cpp-python (CPU)
- **ASR:** faster-whisper
- **Fine-tuning:** Unsloth + QLoRA on Kaggle, exported to GGUF (llama.cpp)
- **UI:** Gradio (Spaces) and Streamlit (local)
- **Tooling:** `uv` (never pip), `ruff`, `mypy`, `pytest`

## Project layout

```
farmlens/
  core/        config, dependency injection, exceptions, logging
  features/    mandi, weather, rag, schemes, intent, asr  (one class each)
  api/         FastAPI app, routes, exception handlers
  frontend/    gradio_app.py (Spaces), app.py (Streamlit)
notebooks/     01 translate KCC, 02 fine-tune Airavata (Kaggle)
data/chroma_db prebuilt ICAR vector store (shipped via git-LFS)
```

---

## Run it locally

Uses **uv** and **Ollama** (never pip):

```bash
uv sync
ollama create farmlens -f models/Modelfile      # import the fine-tuned GGUF
uv run uvicorn farmlens.api.app:app --reload     # API at http://localhost:8000
uv run streamlit run farmlens/frontend/app.py     # UI
```

Copy `.env.example` to `.env` and set `LLM_BACKEND=ollama`,
`OLLAMA_MODEL=farmlens`, and your API keys.

## Deploy on HuggingFace Spaces (Docker)

This repo is Space-ready (Docker SDK, port 7860, pinned = False, GGUF pulled from HF Hub at
runtime). Set the following under **Settings, Variables and secrets**:

| Name | Kind | Value |
|---|---|---|
| `LLM_BACKEND` | variable | `llamacpp` |
| `GGUF_REPO_ID` | variable | `amity838/farmlens-airavata-gguf` |
| `DATA_GOV_API_KEY` | secret | data.gov.in key |
| `OPENWEATHER_API_KEY` | secret | OpenWeatherMap key |

---

## Phase 2 — roadmap

| Area | Plan |
|---|---|
| Crop disease detection | EfficientNet on PlantVillage — photo to Hindi diagnosis and remedy |
| Agentic routing | LLM decides RAG vs. which tool to call (today intent is classified but answers always go through RAG) |
| Better RAG | bge-m3 embeddings, layout-aware PDF parsing, metadata + parent-child retrieval, table-aware chunking, late chunking |
| Evaluation | RAGAS (faithfulness, context precision/recall) and tracing via LangGraph |
| Full multilingual | Punjabi, Marathi, Telugu, Tamil, Bengali — re-evaluate Llama-3.1-8B / Sarvam-1 |
| Spoken replies | AI4Bharat Indic TTS (text to voice out) |
| WhatsApp | Reach farmers on the channel they already use |

Detailed Phase-2 decisions live in [`TASKS.md`](TASKS.md).

---

## Data and credits

- **ICAR** — Package of Practices documents (the RAG knowledge base)
- **Kisan Call Centre (KCC)** — Q&A dataset for fine-tuning (translated to Hindi)
- **AI4Bharat** — Airavata base model
- **data.gov.in (Agmarknet)** and **OpenWeatherMap** — live data

> FarmLens is an MVP. Always cross-check critical agronomic decisions with a
> local Krishi Vigyan Kendra (KVK) or extension officer.
