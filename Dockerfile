# FarmLens — HuggingFace Spaces (Docker SDK). Serves the Gradio app on :7860.
FROM python:3.11-slim

# Build tools for llama-cpp-python (CPU GGUF inference) + chromadb native deps.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git && rm -rf /var/lib/apt/lists/*

# Project rule: uv only, never pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# HF Spaces runs containers as a non-root user (uid 1000) with a writable home.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    UV_LINK_MODE=copy \
    HF_HOME=/home/user/.cache/huggingface
WORKDIR /home/user/app

# Dependencies first for better layer caching. --extra spaces adds llama-cpp-python.
COPY --chown=user pyproject.toml uv.lock ./
COPY --chown=user farmlens ./farmlens
RUN uv sync --extra spaces --no-dev --frozen

# Prebuilt ChromaDB knowledge base (config default path: ./data/chroma_db).
COPY --chown=user data/chroma_db ./data/chroma_db

EXPOSE 7860
CMD ["uv", "run", "python", "-m", "farmlens.frontend.gradio_app"]
