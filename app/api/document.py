from fastapi import APIRouter
from app.rag.document_loader import DocumentLoader

router = APIRouter()


@router.get("/document-info")
def document_info():

    docs = DocumentLoader.load_pdf(
        "data/uploads/AI_Project_Proposal.pdf"
    )

    return {
        "pages": len(docs),
        "first_page": docs[0].page_content[:500],
        "metadata": docs[0].metadata
    }