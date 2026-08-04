from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str

    HOST: str
    PORT: int

    UPLOAD_DIR: str
    CHROMA_DB_PATH: str

    MODEL_NAME: str
    EMBEDDING_MODEL: str

    LOG_LEVEL: str

    class Config:
        env_file = ".env"


settings = Settings()