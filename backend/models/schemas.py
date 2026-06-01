from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────

class Language(str, Enum):
    HINDI      = "hi"
    MARATHI    = "mr"
    PUNJABI    = "pa"
    TELUGU     = "te"
    BENGALI    = "bn"
    KANNADA    = "kn"


class IntentType(str, Enum):
    PRICE      = "price"
    WEATHER    = "weather"
    DISEASE    = "disease"
    GENERAL    = "general"


class ResponseSource(str, Enum):
    MANDI      = "mandi"
    WEATHER    = "weather"
    DISEASE    = "disease"
    RAG        = "rag"
    LLM        = "llm"


# ── Request Models ─────────────────────────────────────────

class ChatRequest(BaseModel):
    text: str = Field(..., description="Farmer's question in any Indian language")
    lang: Language = Field(default=Language.HINDI, description="Language code")
    lat: float = Field(default=28.6139, description="Latitude for weather")
    lon: float = Field(default=77.2090, description="Longitude for weather")

    model_config = {"use_enum_values": True}


class PriceRequest(BaseModel):
    crop: str = Field(..., description="Crop name in Hindi e.g. गेहूं")
    state: str = Field(..., description="State name in English e.g. Uttar Pradesh")
    district: Optional[str] = Field(default=None, description="District name")


class WeatherRequest(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    lang: Language = Field(default=Language.HINDI)

    model_config = {"use_enum_values": True}


class DiagnoseRequest(BaseModel):
    image_path: str = Field(..., description="Path to uploaded leaf image")
    lang: Language = Field(default=Language.HINDI)

    model_config = {"use_enum_values": True}


# ── Response Models ────────────────────────────────────────

class ChatResponse(BaseModel):
    response: str = Field(..., description="Answer in farmer's language")
    source: ResponseSource = Field(..., description="Which module answered")
    lang: str = Field(..., description="Language of the response")
    audio_url: Optional[str] = Field(default=None, description="TTS audio URL")

    model_config = {"use_enum_values": True}


class PriceResponse(BaseModel):
    crop: str
    market: str
    state: str
    min_price: str
    max_price: str
    modal_price: str
    date: str
    response_hi: str = Field(..., description="Formatted Hindi response string")


class WeatherResponse(BaseModel):
    spray_ok: bool
    reason: str
    temp: float
    rain_prob: int = Field(..., ge=0, le=100, description="Rain probability 0-100")
    wind_speed: float
    humidity: int = Field(..., ge=0, le=100)
    response_hi: str = Field(..., description="Formatted Hindi response string")


class DiagnoseResponse(BaseModel):
    disease_class: str = Field(..., description="PlantVillage class name")
    disease_name_hi: str = Field(..., description="Hindi disease name")
    crop_hi: str = Field(..., description="Hindi crop name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence")
    treatment_hi: str = Field(..., description="Hindi treatment instructions")
    response_hi: str = Field(..., description="Full formatted Hindi response")


# ── Internal Models ────────────────────────────────────────

class IntentResult(BaseModel):
    intent: IntentType
    crop: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    model_config = {"use_enum_values": True}


class AudioTranscript(BaseModel):
    text: str = Field(..., description="Transcribed text from audio")
    lang: str = Field(..., description="Detected or provided language code")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)