from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./research.db"

    OPENROUTER_API_KEY: str = ""
    LLM_BACKEND: str = "auto"
    JWT_SECRET_KEY: str = ""
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, ge=5)
    OPENROUTER_MODEL: str = "qwen/qwen3.8-27b:free"
    OPENROUTER_SYNTHESIS_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    EMBEDDING_BACKEND: str = "auto"
    MAX_UPLOAD_SIZE_MB: int = Field(default=50, ge=1)
    RETRIEVAL_TOP_K: int = Field(default=5, ge=1)
    SYNTHESIS_CHUNKS_PER_DOCUMENT: int = Field(default=3, ge=1)
    SYNTHESIS_CANDIDATE_K: int = Field(default=10, ge=1)
    SYNTHESIS_MAX_DISTANCE: float = Field(default=0.75, ge=0, le=2)
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_PRIVATE_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()