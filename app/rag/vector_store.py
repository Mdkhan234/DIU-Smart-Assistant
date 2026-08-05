from langchain_chroma import Chroma

from app.core.config import settings
from app.rag.embedding import EmbeddingModel


class VectorStore:

    @staticmethod
    def create(chunks):

        db = Chroma.from_documents(
            documents=chunks,
            embedding=EmbeddingModel.get_embeddings(),
            persist_directory=settings.CHROMA_DB_PATH
        )

        return db

    @staticmethod
    def load():

        db = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=EmbeddingModel.get_embeddings()
        )

        return db