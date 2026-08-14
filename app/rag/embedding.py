from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings


class EmbeddingModel:

    _embeddings = None

    @staticmethod
    def get_embeddings():

        if EmbeddingModel._embeddings is None:

            EmbeddingModel._embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,

                model_kwargs={
                    "device": "cpu"
                },

                encode_kwargs={
                    "normalize_embeddings": True
                }
            )

        return EmbeddingModel._embeddings