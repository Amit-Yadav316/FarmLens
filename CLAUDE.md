# FarmLens — Claude Code Instructions

## Project Context

FarmLens is a multilingual voice-first AI advisory system for Indian farmers.
It answers questions about mandi prices, weather/spray advisory, crop diseases,
government schemes, and general farming guidance in Hindi and 5 other Indian languages.

Target users: Small and marginal farmers in India who may have low literacy.
Primary interface: Voice input → Hindi text response (WhatsApp in Phase 2)
Core principle: Never hallucinate — real data from APIs, real documents from ICAR.

---

## Hard Rules — Never Break These

### Package Management
- Use uv ONLY. Never use pip directly.
- All dependencies go in pyproject.toml under [project.dependencies]
- Dev dependencies go under [tool.uv.dev-dependencies]
- Never create or modify requirements.txt
- Run `uv sync` to install, never `pip install`

### Python Version
- Python 3.11 only
- Use `from __future__ import annotations` in every file
- Use union types with | not Optional (e.g. str | None not Optional[str])
- Use match/case for intent routing

### Architecture — Non Negotiable
- Feature-based folder structure (see below)
- Every service is a class, never standalone functions
- FastAPI dependency injection for all services
- No global singletons outside of core/dependencies.py
- No business logic in API route handlers — routes are thin
- Custom exceptions only — never raise generic Exception

### Code Style
- Type hints on every function — no exceptions
- Docstrings on every class and public method
- No bare except — always catch specific exceptions
- No hardcoded strings — use constants or config
- Max function length: 30 lines
- Max file length: 200 lines — split if longer

### What Claude Must Never Do
- Never use `from module import *`
- Never put logic directly in __init__.py
- Never use mutable default arguments
- Never ignore exceptions silently
- Never hardcode API keys or secrets
- Never mix Hindi and English in variable names
- Never create a file without type hints

---

## Folder Structure

```
farmlens/
├── core/
│   ├── __init__.py
│   ├── config.py          # Settings class with pydantic-settings
│   ├── dependencies.py    # FastAPI dependency injection providers
│   ├── exceptions.py      # Custom exception hierarchy
│   └── logging.py         # Structured logging setup
│
├── features/
│   ├── asr/
│   │   ├── __init__.py
│   │   ├── service.py     # ASRService class
│   │   ├── schemas.py     # TranscriptRequest, TranscriptResponse
│   │   └── exceptions.py  # ASRException
│   │
│   ├── mandi/
│   │   ├── __init__.py
│   │   ├── service.py     # MandiService class
│   │   ├── schemas.py     # PriceRequest, PriceResponse
│   │   ├── exceptions.py  # MandiException
│   │   └── constants.py   # CROP_MAP, LOCATION_MAP
│   │
│   ├── weather/
│   │   ├── __init__.py
│   │   ├── service.py     # WeatherService class
│   │   ├── schemas.py     # WeatherRequest, WeatherResponse
│   │   ├── exceptions.py  # WeatherException
│   │   └── constants.py   # SPRAY_RULES, STATE_CAPITALS
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── pipeline.py    # RAGPipeline class
│   │   ├── ingestion.py   # PDFIngestion class
│   │   ├── schemas.py     # RAGRequest, RAGResponse
│   │   └── exceptions.py  # RAGException
│   │
│   ├── schemes/
│   │   ├── __init__.py
│   │   ├── service.py     # SchemeService class
│   │   ├── schemas.py     # SchemeRequest, SchemeResponse
│   │   └── data.py        # SCHEMES list (static data)
│   │
│   └── intent/
│       ├── __init__.py
│       ├── router.py      # IntentRouter class
│       ├── schemas.py     # IntentResult
│       └── constants.py   # PRICE_KW, WEATHER_KW etc
│
├── api/
│   ├── __init__.py
│   ├── app.py             # FastAPI app factory
│   ├── middleware.py      # CORS, rate limiting, logging
│   └── routes/
│       ├── __init__.py
│       ├── chat.py        # /chat, /voice-chat endpoints
│       ├── health.py      # /health, /status endpoints
│       └── data.py        # /price, /weather endpoints
│
├── frontend/
│   ├── app.py             # Streamlit UI
│   └── gradio_app.py      # Gradio UI for HuggingFace deploy
│
└── scripts/
    ├── ingest_pdfs.py     # One-time PDF ingestion
    └── prepare_kcc.py     # KCC dataset preparation (Phase 2)

tests/
├── conftest.py            # Shared fixtures
├── unit/
│   ├── test_mandi_service.py
│   ├── test_weather_service.py
│   ├── test_rag_pipeline.py
│   └── test_intent_router.py
└── integration/
    └── test_api.py

data/
├── pdfs/                  # ICAR PDF files
├── crop_map.json          # Crop names in all languages
├── location_map.json      # Cities to coordinates
└── schemes.json           # Government schemes

pyproject.toml
.env
.env.example
CLAUDE.md                  # This file
TASKS.md                   # Current work
```

---

## Service Class Pattern

Every service follows this exact pattern:

```python
class MandiService:
    """Fetches live mandi prices from Agmarknet API."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.data_gov_api_key
        self._cache: TTLCache = TTLCache(
            maxsize=100,
            ttl=settings.mandi_cache_ttl
        )

    def get_price(self, crop: str, state: str) -> PriceResponse:
        """Public method with full type hints and docstring."""
        ...

    def _fetch_from_api(self, crop_en: str, state: str) -> dict:
        """Private helper methods prefixed with _"""
        ...
```

---

## FastAPI Dependency Injection Pattern

```python
# core/dependencies.py
def get_mandi_service(
    settings: Settings = Depends(get_settings)
) -> MandiService:
    return MandiService(settings)

# api/routes/data.py
@router.get("/price")
async def get_price(
    crop: str,
    state: str,
    service: MandiService = Depends(get_mandi_service)
) -> PriceResponse:
    return service.get_price(crop, state)
```

---

## Exception Hierarchy

```python
# core/exceptions.py
class FarmLensException(Exception):
    """Base exception for all FarmLens errors."""

class MandiException(FarmLensException): ...
class WeatherException(FarmLensException): ...
class RAGException(FarmLensException): ...
class ASRException(FarmLensException): ...
class SchemeException(FarmLensException): ...
```

---

## RAGPipeline Class Pattern

```python
class RAGPipeline:
    """Class-based RAG pipeline. Single instance per app."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._embedder: HuggingFaceEmbeddings | None = None
        self._db: Chroma | None = None
        self._chain = None

    def initialize(self) -> None:
        """Load embedder and DB. Called once at startup."""
        ...

    def answer(self, question: str) -> str:
        """Answer a farming question using RAG."""
        ...

    def ingest(self, pdf_dir: str) -> int:
        """Ingest PDFs. Returns number of chunks created."""
        ...

    def evaluate(self, eval_dataset: list) -> dict:
        """Run RAGAS evaluation. Returns metrics dict."""
        ...

    @property
    def is_ready(self) -> bool:
        """Check if DB is loaded and ready."""
        ...
```

---

## Environment Variables

Required in .env:
```
DATA_GOV_API_KEY=
OPENWEATHER_API_KEY=
HF_TOKEN=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
CHROMA_DB_PATH=./data/chroma_db
DEFAULT_LANG=hi
MANDI_CACHE_TTL=3600
WEATHER_CACHE_TTL=1800
```

---

## Testing Rules

- Every service method has at least one test
- Use pytest fixtures for service instances
- Mock external APIs — never call real APIs in unit tests
- Integration tests in tests/integration/ only
- Test file mirrors source file name (test_mandi_service.py tests service.py)

---

## What Good Code Looks Like Here

```python
# GOOD
class WeatherService:
    def get_advisory(self, lat: float, lon: float) -> WeatherResponse:
        """Get spray advisory for given coordinates."""
        try:
            forecast = self._fetch_forecast(lat, lon)
            return self._apply_rules(forecast)
        except requests.Timeout as e:
            raise WeatherException("API timeout") from e

# BAD
def get_weather(lat, lon):
    try:
        r = requests.get(...)
        return r.json()
    except:
        return None
```
