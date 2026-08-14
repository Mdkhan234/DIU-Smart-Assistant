from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker
from app.core.config import settings


router = APIRouter()

UPLOAD_FOLDER = Path("data/uploads")


@router.get("/document-info")
def document_info():

    # ---------------------------------------------------------
    # Check upload directory
    # ---------------------------------------------------------

    if not UPLOAD_FOLDER.exists():
        raise HTTPException(
            status_code=404,
            detail="Upload directory does not exist."
        )

    # ---------------------------------------------------------
    # Find all PDF files
    # ---------------------------------------------------------

    pdf_files = sorted(
        UPLOAD_FOLDER.glob("*.pdf")
    )

    if not pdf_files:
        return {
            "success": True,
            "total_documents": 0,
            "total_pages": 0,
            "total_chunks": 0,
            "documents": []
        }

    documents = []

    total_pages = 0
    total_chunks = 0

    # ---------------------------------------------------------
    # Process every PDF
    # ---------------------------------------------------------

    for pdf_path in pdf_files:

        try:

            # -------------------------------------------------
            # Load PDF
            # -------------------------------------------------

            docs = DocumentLoader.load_pdf(
                str(pdf_path)
            )

            pages = len(docs)

            # -------------------------------------------------
            # Create chunks
            # -------------------------------------------------

            chunks = TextChunker.split_documents(
                docs
            )

            chunk_count = len(chunks)

            total_pages += pages
            total_chunks += chunk_count

            # -------------------------------------------------
            # Metadata
            # -------------------------------------------------

            metadata = (
                docs[0].metadata
                if docs
                else {}
            )

            # -------------------------------------------------
            # Document information
            # -------------------------------------------------

            documents.append({

                "filename": pdf_path.name,

                "path": str(pdf_path),

                "pages": pages,

                "chunks": chunk_count,

                "characters": sum(
                    len(doc.page_content)
                    for doc in docs
                ),

                "status": "Indexed",

                "metadata": metadata
            })

        except Exception as e:

            documents.append({

                "filename": pdf_path.name,

                "path": str(pdf_path),

                "pages": 0,

                "chunks": 0,

                "characters": 0,

                "status": "Error",

                "error": str(e)
            })

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------

    return {

        "success": True,

        "total_documents": len(pdf_files),

        "total_pages": total_pages,

        "total_chunks": total_chunks,

        "documents": documents
    }