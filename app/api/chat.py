from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.rag.retriever import Retriever
from app.rag.context_builder import ContextBuilder
from app.rag.llm import LLM


router = APIRouter()


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    session_id: str = Field(
        default="default",
        min_length=1
    )

    question: str = Field(
        ...,
        min_length=1
    )

    k: int = Field(
        default=5,
        ge=1,
        le=100
    )


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post("/chat")
def chat(request: ChatRequest):

    question = request.question.strip()
    k = request.k

    # ========================================================
    # 1. DETECT INTENT
    # ========================================================

    intents = Retriever.detect_intent(question)

    # ========================================================
    # 2. PROGRAM LIST QUERY
    # ========================================================

    if intents.get("programs", False):

        programs = Retriever.extract_program_names()

        # ----------------------------------------------------
        # Extraction failed
        # ----------------------------------------------------

        if not programs:

            return {
                "success": True,
                "session_id": request.session_id,
                "query": question,
                "answer": (
                    "I could not extract the DIU program list "
                    "from the available Programs document."
                ),
                "sources": []
            }

        # ----------------------------------------------------
        # Build authoritative program context
        # ----------------------------------------------------

        context = (
            ContextBuilder.build_program_list_context(
                programs
            )
        )

        # ----------------------------------------------------
        # Generate program list
        # ----------------------------------------------------

        answer = (
            LLM.extract_program_list_answer(
                question=question,
                context=context
            )
        )

        if not answer:

            answer = (
                "The DIU program list could not be generated."
            )

        # ----------------------------------------------------
        # Program document sources
        # ----------------------------------------------------

        program_documents = (
            Retriever.get_program_documents()
        )

        sources = (
            ContextBuilder.build_sources(
                program_documents
            )
        )

        return {
            "success": True,
            "session_id": request.session_id,
            "query": question,
            "answer": answer,
            "sources": sources
        }

    # ========================================================
    # 3. NORMAL RAG SEARCH
    # ========================================================

    results = (
        Retriever.search_relevant(
            query=question,
            k=k
        )
    )

    # ========================================================
    # 4. BUILD CONTEXT
    # ========================================================

    context = (
        ContextBuilder.build(
            results
        )
    )

    # ========================================================
    # 5. GENERATE ANSWER
    # ========================================================

    answer = (
        LLM.generate(
            question=question,
            context=context
        )
    )

    # ========================================================
    # 6. BUILD SOURCES
    # ========================================================

    sources = (
        ContextBuilder.build_sources(
            results
        )
    )

    # ========================================================
    # 7. FINAL RESPONSE
    # ========================================================

    return {
        "success": True,
        "session_id": request.session_id,
        "query": question,
        "answer": answer,
        "sources": sources
    }