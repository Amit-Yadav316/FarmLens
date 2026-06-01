from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # API Keys
    data_gov_api_key: str = Field(..., validation_alias="DATA_GOV_API_KEY")
    openweather_api_key: str = Field(..., validation_alias="OPENWEATHER_API_KEY")

    # Ollama
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        validation_alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(
        default="mistral",
        validation_alias="OLLAMA_MODEL"
    )

    # Paths
    chroma_db_path: str = Field(
        default="./chroma_db",
        validation_alias="CHROMA_DB_PATH"
    )

    mandi_resource_id: str = Field(
        default="9ef84268-d588-465a-a308-a864a43d0070",
        validation_alias="MANDI_RESOURCE_ID"
    )


    mandi_cache_ttl: int = Field(default=3600, validation_alias="MANDI_CACHE_TTL")
    weather_cache_ttl: int = Field(default=1800, validation_alias="WEATHER_CACHE_TTL")

    # Default language
    default_lang: str = Field(default="hi", validation_alias="DEFAULT_LANG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()