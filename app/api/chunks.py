from fastapi import APIRouter

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker

router = APIRouter()


@router.get("/chunks")
def chunk_info():

    docs = DocumentLoader.load_pdf(
        "data/uploads/AI_Project_Proposal.pdf"
    )

    chunks = TextChunker.split_documents(docs)

    return {
        "total_chunks": len(chunks),
        "first_chunk": chunks[0].page_content,
        "chunk_size": len(chunks[0].page_content),
        "metadata": chunks[0].metadata
    }