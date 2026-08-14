from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    # ============================================================
    # PROJECT
    # ============================================================

    PROJECT_NAME: str = "DIU Smart Assistant"

    VERSION: str = "1.0.0"

    DESCRIPTION: str = (
        "AI-powered university assistant "
        "using Retrieval-Augmented Generation"
    )

    # ============================================================
    # SERVER
    # ============================================================

    HOST: str = "127.0.0.1"

    PORT: int = 8000

    # ============================================================
    # STORAGE
    # ============================================================

    UPLOAD_DIR: str = "data/uploads"

    CHROMA_DB_PATH: str = "data/chroma_db"

    # ============================================================
    # AI MODELS
    # ============================================================

    MODEL_NAME: str = "llama3.2:1b"

    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ============================================================
    # LLM PROVIDER
    # ============================================================

    LLM_PROVIDER: str = "ollama"

    # ============================================================
    # OLLAMA - LOCAL DEVELOPMENT
    # ============================================================

    OLLAMA_URL: str = (
        "http://127.0.0.1:11434/api/generate"
    )

    # ============================================================
    # OPENAI - PRODUCTION
    # ============================================================

    OPENAI_API_KEY: str = ""

    OPENAI_MODEL: str = "gpt-5-mini"

    OPENAI_EMBEDDING_MODEL: str = (
        "text-embedding-3-small"
    )

    # ============================================================
    # LOGGING
    # ============================================================

    LOG_LEVEL: str = "INFO"

    # ============================================================
    # RETRIEVAL
    # ============================================================

    TOP_K: int = 5

    RELEVANCE_THRESHOLD: float = 0.65

    MAX_CONTEXT_CHARS: int = 6000

    DEBUG_RETRIEVAL: bool = True

    # ============================================================
    # ENVIRONMENT
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()