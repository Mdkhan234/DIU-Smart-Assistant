from fastapi import APIRouter
from pathlib import Path

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker

router = APIRouter()

# Upload directory
UPLOAD_FOLDER = Path("data/uploads")


@router.get("/chunks")
def chunk_info():

    # ---------------------------------------------------------
    # Find all PDF files
    # ---------------------------------------------------------
    pdf_files = sorted(UPLOAD_FOLDER.glob("*.pdf"))

    if not pdf_files:
        return {
            "success": False,
            "message": "No PDF files found in data/uploads.",
            "total_documents": 0,
            "total_chunks": 0
        }

    # ---------------------------------------------------------
    # Load all PDF documents
    # ---------------------------------------------------------
    all_docs = []

    for pdf_file in pdf_files:

        try:
            docs = DocumentLoader.load_pdf(str(pdf_file))
            all_docs.extend(docs)

        except Exception as e:
            print(f"Failed to load {pdf_file.name}: {e}")

    # ---------------------------------------------------------
    # Check whether documents were loaded
    # ---------------------------------------------------------
    if not all_docs:
        return {
            "success": False,
            "message": "PDF files were found, but no documents could be loaded.",
            "total_documents": len(pdf_files),
            "total_pages": 0,
            "total_chunks": 0
        }

    # ---------------------------------------------------------
    # Split all documents into chunks
    # ---------------------------------------------------------
    chunks = TextChunker.split_documents(all_docs)

    # ---------------------------------------------------------
    # Check chunks
    # ---------------------------------------------------------
    if not chunks:
        return {
            "success": False,
            "message": "Documents were loaded, but no chunks were created.",
            "total_documents": len(pdf_files),
            "total_pages": len(all_docs),
            "total_chunks": 0
        }

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------
    return {
        "success": True,
        "total_documents": len(pdf_files),
        "total_pages": len(all_docs),
        "total_chunks": len(chunks),

        "first_chunk": chunks[0].page_content,

        "chunk_size": len(chunks[0].page_content),

        "metadata": chunks[0].metadata
    }