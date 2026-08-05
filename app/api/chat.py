from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.rag_pipeline import RAGPipeline

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    result = RAGPipeline.ask(
        request.session_id,
        request.question
    )

    return result