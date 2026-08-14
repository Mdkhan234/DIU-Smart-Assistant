from pathlib import Path
import shutil
import uuid

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
    def create(chunks, persist_directory=None):

        db_path = persist_directory or settings.CHROMA_DB_PATH

        db = Chroma.from_documents(
            documents=chunks,
            embedding=EmbeddingModel.get_embeddings(),
            persist_directory=db_path,
        )

        return db

    # ========================================================
    # LOAD
    # ========================================================

    @staticmethod
    def load():

        chroma_path = Path(settings.CHROMA_DB_PATH)

        if not chroma_path.exists():
            raise RuntimeError(
                "Vector database does not exist. "
                "Please build the knowledge base first."
            )

        return Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=EmbeddingModel.get_embeddings(),
        )

    # ========================================================
    # REBUILD
    # ========================================================

    @staticmethod
    def rebuild_from_uploads():

        upload_folder = Path("data/uploads")

        upload_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        pdf_files = sorted(
            upload_folder.glob("*.pdf"),
            key=lambda x: x.name.lower(),
        )

        if not pdf_files:

            return {
                "success": False,
                "documents": 0,
                "pages": 0,
                "chunks": 0,
                "message": "No PDF files found.",
            }

        # ----------------------------------------------------
        # Load PDFs
        # ----------------------------------------------------

        all_docs = []
        failed_files = []

        for pdf_file in pdf_files:

            try:

                docs = DocumentLoader.load_pdf(
                    str(pdf_file)
                )

                all_docs.extend(docs)

            except Exception as e:

                failed_files.append({
                    "filename": pdf_file.name,
                    "error": str(e),
                })

        if not all_docs:

            return {
                "success": False,
                "documents": len(pdf_files),
                "pages": 0,
                "chunks": 0,
                "failed_files": failed_files,
                "message": "No documents could be loaded.",
            }

        # ----------------------------------------------------
        # Split documents
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
                "failed_files": failed_files,
                "message": "No chunks were created.",
            }

        # ----------------------------------------------------
        # IMPORTANT:
        # Create NEW temporary database first.
        # Do NOT delete the current database yet.
        # ----------------------------------------------------

        current_path = Path(
            settings.CHROMA_DB_PATH
        )

        temporary_path = Path(
            f"{settings.CHROMA_DB_PATH}_tmp_{uuid.uuid4().hex[:8]}"
        )

        backup_path = Path(
            f"{settings.CHROMA_DB_PATH}_backup"
        )

        try:

            # ------------------------------------------------
            # Create temporary vector database
            # ------------------------------------------------

            VectorStore.create(
                chunks,
                persist_directory=str(temporary_path),
            )

            # ------------------------------------------------
            # Verify temporary database
            # ------------------------------------------------

            test_db = Chroma(
                persist_directory=str(temporary_path),
                embedding_function=EmbeddingModel.get_embeddings(),
            )

            count = test_db._collection.count()

            if count != len(chunks):

                raise RuntimeError(
                    f"Vector database verification failed. "
                    f"Expected {len(chunks)} chunks but found {count}."
                )

            # ------------------------------------------------
            # Remove old backup
            # ------------------------------------------------

            if backup_path.exists():

                shutil.rmtree(
                    backup_path,
                    ignore_errors=True,
                )

            # ------------------------------------------------
            # Move current database to backup
            # ------------------------------------------------

            if current_path.exists():

                current_path.rename(
                    backup_path
                )

            # ------------------------------------------------
            # Activate new database
            # ------------------------------------------------

            temporary_path.rename(
                current_path
            )

            # ------------------------------------------------
            # Remove backup after successful activation
            # ------------------------------------------------

            if backup_path.exists():

                shutil.rmtree(
                    backup_path,
                    ignore_errors=True,
                )

        except Exception as e:

            # ------------------------------------------------
            # Clean temporary database
            # ------------------------------------------------

            if temporary_path.exists():

                shutil.rmtree(
                    temporary_path,
                    ignore_errors=True,
                )

            # ------------------------------------------------
            # Restore previous database if necessary
            # ------------------------------------------------

            if (
                not current_path.exists()
                and backup_path.exists()
            ):

                backup_path.rename(
                    current_path
                )

            raise RuntimeError(
                f"Vector database rebuild failed: {str(e)}"
            ) from e

        return {
            "success": True,
            "documents": len(pdf_files),
            "pages": len(all_docs),
            "chunks": len(chunks),
            "failed_files": failed_files,
            "message": "Vector database rebuilt successfully.",
        }