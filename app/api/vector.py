from fastapi import APIRouter

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker
from app.rag.vector_store import VectorStore

router = APIRouter()


@router.post("/build-vector-db")
def build_vector_db():

    # Load PDF
    docs = DocumentLoader.load_pdf(
        "data/uploads/AI_Project_Proposal.pdf"
    )

    # Split into chunks
    chunks = TextChunker.split_documents(docs)

    # Create Chroma Database
    db = VectorStore.create(chunks)

    return {
        "success": True,
        "documents": len(docs),
        "chunks": len(chunks),
        "message": "Vector database created successfully."
    }