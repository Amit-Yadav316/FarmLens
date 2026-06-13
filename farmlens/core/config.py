from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # External API keys
    data_gov_api_key: str = ""
    mandi_resource_id: str = "9ef84268-d588-465a-a308-a864a43d0070"
    openweather_api_key: str = ""
    hf_token: str = ""

    # LLM backend: "ollama" (local dev) or "llamacpp" (CPU GGUF, e.g. HF Spaces)
    llm_backend: str = "ollama"
    llm_max_tokens: int = 512

    # Ollama (used when llm_backend == "ollama")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    # llama.cpp GGUF (used when llm_backend == "llamacpp")
    # Local path takes precedence; otherwise the model is pulled from HF Hub.
    gguf_path: str = ""
    gguf_repo_id: str = ""
    gguf_filename: str = "Airavata.Q4_K_M.gguf"

    # Storage
    chroma_db_path: str = "./data/chroma_db"

    # Language
    default_lang: str = "hi"

    # Cache TTLs (seconds)
    mandi_cache_ttl: int = 3600
    weather_cache_ttl: int = 1800


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
