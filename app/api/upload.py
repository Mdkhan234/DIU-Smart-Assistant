from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil
import uuid

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker
from app.rag.vector_store import VectorStore

router = APIRouter()

UPLOAD_FOLDER = Path("data/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------

    if not file.filename:
        return {
            "success": False,
            "message": "No file selected."
        }

    # ---------------------------------------------------------
    # Validate PDF
    # ---------------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are allowed."
        }

    # ---------------------------------------------------------
    # Generate unique filename
    # ---------------------------------------------------------

    unique_id = uuid.uuid4().hex[:8]

    original_name = Path(file.filename).stem
    extension = Path(file.filename).suffix

    safe_filename = f"{original_name}_{unique_id}{extension}"

    file_path = UPLOAD_FOLDER / safe_filename

    # ---------------------------------------------------------
    # Save PDF
    # ---------------------------------------------------------

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as e:

        return {
            "success": False,
            "message": f"Failed to save PDF: {str(e)}"
        }

    # ---------------------------------------------------------
    # Load PDF
    # ---------------------------------------------------------

    try:

        documents = DocumentLoader.load_pdf(
            str(file_path)
        )

    except Exception as e:

        file_path.unlink(missing_ok=True)

        return {
            "success": False,
            "message": f"Failed to read PDF: {str(e)}"
        }

    # ---------------------------------------------------------
    # Create chunks
    # ---------------------------------------------------------

    try:

        chunks = TextChunker.split_documents(
            documents
        )

    except Exception as e:

        file_path.unlink(missing_ok=True)

        return {
            "success": False,
            "message": f"Failed to create chunks: {str(e)}"
        }

    if not chunks:

        file_path.unlink(missing_ok=True)

        return {
            "success": False,
            "message": "No text chunks could be created from this PDF."
        }

    # ---------------------------------------------------------
    # Rebuild vector database
    # ---------------------------------------------------------

    try:

        VectorStore.rebuild_from_uploads()

    except Exception as e:

        return {
            "success": False,
            "message": (
                "PDF uploaded, but vector database update failed: "
                f"{str(e)}"
            ),
            "filename": safe_filename
        }

    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    return {
        "success": True,
        "message": (
            "PDF uploaded and added to the knowledge base "
            "successfully."
        ),
        "original_filename": file.filename,
        "filename": safe_filename,
        "location": str(file_path),
        "pages": len(documents),
        "chunks": len(chunks),
        "vector_database": "updated"
    }