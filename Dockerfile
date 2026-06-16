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

# Project deps first (better layer caching). NOTE: llama-cpp-python is installed
# separately below as a prebuilt CPU wheel — compiling it from source OOMs the
# Spaces build runner (exit 137).
COPY --chown=user pyproject.toml uv.lock ./
COPY --chown=user farmlens ./farmlens
RUN uv sync --no-dev --frozen

# Prebuilt CPU wheel for llama-cpp-python (no compilation → no OOM, faster build).
RUN uv pip install llama-cpp-python --only-binary llama-cpp-python \
        --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Prebuilt ChromaDB knowledge base (config default path: ./data/chroma_db).
COPY --chown=user data/chroma_db ./data/chroma_db

EXPOSE 7860
# Run the venv's Python directly — `uv run` would re-sync and drop the
# separately-installed llama-cpp-python wheel.
CMD ["/home/user/app/.venv/bin/python", "-m", "farmlens.frontend.gradio_app"]
