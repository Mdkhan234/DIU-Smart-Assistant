from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger

from app.api.upload import router as upload_router
from app.api.document import router as document_router
from app.api.chunks import router as chunk_router
from app.api.vector import router as vector_router
from app.api.retriever import router as retriever_router
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API Routers
# ============================================================

app.include_router(
    chat_router,
    tags=["Chat"],
)

app.include_router(
    upload_router,
    tags=["Upload"],
)

app.include_router(
    document_router,
    tags=["Document"],
)

app.include_router(
    chunk_router,
    tags=["Chunks"],
)

app.include_router(
    vector_router,
    tags=["Vector Database"],
)

app.include_router(
    retriever_router,
    tags=["Retriever"],
)

app.include_router(
    admin_router,
    tags=["Admin"],
)


# ============================================================
# Startup Log
# ============================================================

logger.info("DIU Smart Assistant API Started")


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}"
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }