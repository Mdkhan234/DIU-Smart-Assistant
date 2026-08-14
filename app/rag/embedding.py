from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


class EmbeddingModel:

    _embeddings = None

    @staticmethod
    def get_embeddings():

        if EmbeddingModel._embeddings is None:

            if not settings.OPENAI_API_KEY:
                raise RuntimeError(
                    "OPENAI_API_KEY is not configured."
                )

            EmbeddingModel._embeddings = OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY,
            )

        return EmbeddingModel._embeddings