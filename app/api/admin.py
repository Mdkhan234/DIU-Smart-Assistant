from fastapi import APIRouter, HTTPException
from pathlib import Path
import shutil

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker
from app.rag.vector_store import VectorStore

router = APIRouter(prefix="/admin", tags=["Admin"])

UPLOAD_FOLDER = Path("data/uploads")


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get("/documents")
def get_documents():

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(
        UPLOAD_FOLDER.glob("*.pdf"),
        key=lambda x: x.name.lower()
    )

    documents = []

    total_pages = 0
    total_chunks = 0

    for pdf_file in pdf_files:

        try:
            docs = DocumentLoader.load_pdf(str(pdf_file))

            chunks = TextChunker.split_documents(docs)

            pages = len(docs)
            chunks_count = len(chunks)

            total_pages += pages
            total_chunks += chunks_count

            documents.append({
                "filename": pdf_file.name,
                "path": str(pdf_file),
                "pages": pages,
                "chunks": chunks_count,
                "size_bytes": pdf_file.stat().st_size,
                "status": "Indexed"
            })

        except Exception as e:

            documents.append({
                "filename": pdf_file.name,
                "path": str(pdf_file),
                "pages": 0,
                "chunks": 0,
                "size_bytes": pdf_file.stat().st_size,
                "status": "Error",
                "error": str(e)
            })

    return {
        "success": True,
        "total_documents": len(pdf_files),
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "documents": documents
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete("/documents/{filename}")
def delete_document(filename: str):

    file_path = UPLOAD_FOLDER / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    if file_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents can be deleted."
        )

    try:

        file_path.unlink()

        # Rebuild knowledge base after deletion
        rebuild_result = VectorStore.rebuild_from_uploads()

        return {
            "success": True,
            "message": "Document deleted and knowledge base rebuilt successfully.",
            "filename": filename,
            "rebuild": rebuild_result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


# ============================================================
# REBUILD VECTOR DATABASE
# ============================================================

@router.post("/rebuild-vector-db")
def rebuild_vector_db():

    try:

        result = VectorStore.rebuild_from_uploads()

        return {
            "success": True,
            "message": "Vector database rebuilt successfully.",
            "details": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Vector database rebuild failed: {str(e)}"
        )