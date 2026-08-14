from pathlib import Path
import shutil

from langchain_chroma import Chroma

from app.core.config import settings
from app.rag.embedding import EmbeddingModel
from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextChunker


class VectorStore:

    # ========================================================
    # CREATE
    # ========================================================

    @staticmethod
    def create(chunks):

        db = Chroma.from_documents(
            documents=chunks,
            embedding=EmbeddingModel.get_embeddings(),
            persist_directory=settings.CHROMA_DB_PATH
        )

        return db

    # ========================================================
    # LOAD
    # ========================================================

    @staticmethod
    def load():

        db = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=EmbeddingModel.get_embeddings()
        )

        return db

    # ========================================================
    # REBUILD
    # ========================================================

    @staticmethod
    def rebuild_from_uploads():

        upload_folder = Path("data/uploads")

        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        pdf_files = sorted(
            upload_folder.glob("*.pdf"),
            key=lambda x: x.name.lower()
        )

        if not pdf_files:

            return {
                "success": False,
                "documents": 0,
                "pages": 0,
                "chunks": 0,
                "message": "No PDF files found."
            }

        # ----------------------------------------------------
        # Load PDFs
        # ----------------------------------------------------

        all_docs = []

        for pdf_file in pdf_files:

            try:

                docs = DocumentLoader.load_pdf(
                    str(pdf_file)
                )

                all_docs.extend(docs)

            except Exception as e:

                print(
                    f"Failed to load {pdf_file.name}: {e}"
                )

        if not all_docs:

            return {
                "success": False,
                "documents": len(pdf_files),
                "pages": 0,
                "chunks": 0,
                "message": "No documents could be loaded."
            }

        # ----------------------------------------------------
        # Split
        # ----------------------------------------------------

        chunks = TextChunker.split_documents(
            all_docs
        )

        if not chunks:

            return {
                "success": False,
                "documents": len(pdf_files),
                "pages": len(all_docs),
                "chunks": 0,
                "message": "No chunks were created."
            }

        # ----------------------------------------------------
        # Remove old Chroma database
        # ----------------------------------------------------

        chroma_path = Path(
            settings.CHROMA_DB_PATH
        )

        if chroma_path.exists():

            try:
                shutil.rmtree(chroma_path)

            except PermissionError as e:

                raise RuntimeError(
                    "Chroma database is currently locked. "
                    "Restart FastAPI and try again."
                ) from e

        # ----------------------------------------------------
        # Create new database
        # ----------------------------------------------------

        VectorStore.create(chunks)

        return {
            "success": True,
            "documents": len(pdf_files),
            "pages": len(all_docs),
            "chunks": len(chunks),
            "message": "Vector database rebuilt successfully."
        }