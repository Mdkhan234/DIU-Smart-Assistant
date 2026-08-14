from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.rag_chain import RAGChain


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question about Daffodil International University"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve"
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list
    retrieved_chunks: int


@router.post(
    "",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    try:

        result = RAGChain.answer(
            question=request.question,
            k=request.top_k
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            retrieved_chunks=result.get("retrieved_chunks", 0)
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {str(e)}"
        )