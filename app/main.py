from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

logger.info("DIU Smart Assistant API Started")


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }