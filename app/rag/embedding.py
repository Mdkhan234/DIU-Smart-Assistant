from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings


class EmbeddingModel:

    @staticmethod
    def get_embeddings():

        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        return embeddings