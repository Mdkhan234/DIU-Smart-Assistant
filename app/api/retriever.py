from fastapi import APIRouter

from app.rag.vector_store import VectorStore

router = APIRouter()


@router.get("/search")
def search(query: str):

    db = VectorStore.load()

    results = db.similarity_search(
        query=query,
        k=3
    )

    output = []

    for doc in results:

        output.append(
            {
                "page": doc.metadata.get("page"),
                "content": doc.page_content
            }
        )

    return {
        "query": query,
        "results": output
    }