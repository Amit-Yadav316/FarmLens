---
title: FarmLens
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# FarmLens — किसान सहायक

Multilingual, voice-first AI advisory for Indian farmers. Answers questions about
crop practices, mandi prices, weather/spray advisory, and government schemes — in
Hindi. Facts come from **RAG over ICAR documents** (never hallucinated); the
fine-tuned **Airavata** model supplies natural Hindi *tone*.

## Architecture

- **RAG** — ChromaDB (prebuilt, shipped in `data/chroma_db/`) + multilingual
  embeddings + a Hindi prompt.
- **LLM** — swappable backend:
  - `ollama` (local dev, fast, needs Ollama running),
  - `llamacpp` (this Space — runs the GGUF on CPU, no Ollama needed).
- **Tools** — live mandi prices (Agmarknet), weather/spray advisory
  (OpenWeatherMap), government schemes.
- **UI** — Gradio (`farmlens/frontend/gradio_app.py`), calling the services
  in-process.

## Deploying on HuggingFace Spaces (Docker)

This repo is Space-ready (Docker SDK, port 7860). Set these under
**Settings → Variables and secrets**:

| Name | Kind | Value |
|------|------|-------|
| `LLM_BACKEND` | variable | `llamacpp` |
| `GGUF_REPO_ID` | variable | `<your-hf-username>/farmlens-airavata-gguf` |
| `GGUF_FILENAME` | variable | `Airavata.Q4_K_M.gguf` |
| `HF_TOKEN` | secret | a HF **read** token (to download the GGUF) |
| `DATA_GOV_API_KEY` | secret | data.gov.in key (mandi prices) |
| `OPENWEATHER_API_KEY` | secret | OpenWeatherMap key (weather) |

> First chat downloads the ~4 GB GGUF from your HF model repo (slow first boot),
> then CPU inference is **~30–60s per answer** on the free tier. Tool tabs
> (price/weather/schemes) respond immediately. Upload the GGUF to your HF repo
> first via the fine-tune notebook's §6 cell.

## Local development

Uses **uv** (never pip) and **Ollama** for the LLM:

```bash
uv sync
ollama create farmlens -f models/Modelfile   # import the fine-tuned GGUF
uv run uvicorn farmlens.api.app:app --reload  # API
uv run streamlit run farmlens/frontend/app.py # or the Streamlit UI
```

`.env` (local only) sets `LLM_BACKEND=ollama`, `OLLAMA_MODEL=farmlens`, and the
API keys. See `.env.example`.
