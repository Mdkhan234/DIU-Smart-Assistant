from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import logger
from app.api.upload import router as upload_router
from app.services.pdf_service import PDFService
from app.api.document import router as document_router
from app.api.chunks import router as chunk_router
from app.api.vector import router as vector_router
from app.api.retriever import router as retriever_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

logger.info("DIU Smart Assistant API Started")
app.include_router(upload_router, tags=["Upload"])
app.include_router(document_router, tags=["Document"])
app.include_router(chunk_router, tags=["Chunks"])
app.include_router(vector_router, tags=["Vector Database"])
app.include_router(retriever_router, tags=["Retriever"])



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