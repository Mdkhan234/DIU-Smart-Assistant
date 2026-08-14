from fastapi import APIRouter
from pathlib import Path

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker
from app.rag.vector_store import VectorStore

router = APIRouter()

# Upload directory
UPLOAD_FOLDER = Path("data/uploads")


@router.post("/build-vector-db")
def build_vector_db():

    # ---------------------------------------------------------
    # Find all PDF files
    # ---------------------------------------------------------
    pdf_files = sorted(UPLOAD_FOLDER.glob("*.pdf"))

    if not pdf_files:
        return {
            "success": False,
            "message": "No PDF files found in data/uploads.",
            "total_documents": 0,
            "total_pages": 0,
            "total_chunks": 0
        }

    # ---------------------------------------------------------
    # Load all PDF documents
    # ---------------------------------------------------------
    all_docs = []
    failed_files = []

    for pdf_file in pdf_files:

        try:
            docs = DocumentLoader.load_pdf(str(pdf_file))
            all_docs.extend(docs)

        except Exception as e:
            failed_files.append({
                "filename": pdf_file.name,
                "error": str(e)
            })

    # ---------------------------------------------------------
    # Check loaded documents
    # ---------------------------------------------------------
    if not all_docs:
        return {
            "success": False,
            "message": "PDF files were found, but no documents could be loaded.",
            "total_documents": len(pdf_files),
            "total_pages": 0,
            "total_chunks": 0,
            "failed_files": failed_files
        }

    # ---------------------------------------------------------
    # Split all documents into chunks
    # ---------------------------------------------------------
    chunks = TextChunker.split_documents(all_docs)

    if not chunks:
        return {
            "success": False,
            "message": "Documents were loaded, but no chunks were created.",
            "total_documents": len(pdf_files),
            "total_pages": len(all_docs),
            "total_chunks": 0,
            "failed_files": failed_files
        }

    # ---------------------------------------------------------
    # Create ChromaDB
    # ---------------------------------------------------------
    db = VectorStore.create(chunks)

    # ---------------------------------------------------------
    # Return result
    # ---------------------------------------------------------
    return {
        "success": True,
        "total_documents": len(pdf_files),
        "total_pages": len(all_docs),
        "total_chunks": len(chunks),
        "failed_files": failed_files,
        "message": "Vector database created successfully."
    }