from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

from app.services.pdf_service import PDFService

router = APIRouter()

UPLOAD_FOLDER = Path("data/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Check if the uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are allowed."
        }

    # Save the uploaded PDF
    file_path = UPLOAD_FOLDER / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from the PDF
    text = PDFService.extract_text(str(file_path))

    # Return response
    return {
        "success": True,
        "filename": file.filename,
        "location": str(file_path),
        "characters": len(text),
        "preview": text[:500]
    }