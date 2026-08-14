from fastapi import APIRouter, Query

from app.rag.retriever import Retriever


router = APIRouter()


@router.get("/search")
def search(
    query: str = Query(
        ...,
        min_length=1
    ),
    k: int = Query(
        5,
        ge=1,
        le=100
    )
):

    # ============================================================
    # RETRIEVE
    # ============================================================

    results = (
        Retriever.search_relevant(
            query=query,
            k=k
        )
    )

    # ============================================================
    # FORMAT RESULTS
    # ============================================================

    formatted_results = []

    for result in results:

        metadata = (
            result.get(
                "metadata",
                {}
            )
            or {}
        )

        formatted_results.append(
            {
                "score": result.get(
                    "score"
                ),

                "original_score": result.get(
                    "original_score"
                ),

                "entity_bonus": result.get(
                    "entity_bonus"
                ),

                "intent_bonus": result.get(
                    "intent_bonus"
                ),

                "page": metadata.get(
                    "page"
                ),

                "source": metadata.get(
                    "source"
                ),

                "content": result.get(
                    "content"
                )
            }
        )

    # ============================================================
    # RESPONSE
    # ============================================================

    return {
        "success": True,
        "query": query,
        "count": len(formatted_results),
        "results": formatted_results
    }