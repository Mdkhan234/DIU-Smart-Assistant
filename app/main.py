from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import logger
from app.api.upload import router as upload_router
from app.services.pdf_service import PDFService

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

logger.info("DIU Smart Assistant API Started")
app.include_router(upload_router, tags=["Upload"])

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