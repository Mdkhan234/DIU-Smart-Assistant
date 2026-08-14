from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    _model = None

    # Lightweight and free local embedding model.
    MODEL_NAME = "all-MiniLM-L6-v2"

    @classmethod
    def _initialize(cls):

        if cls._model is None:

            print(
                f"Loading local embedding model: {cls.MODEL_NAME}"
            )

            cls._model = SentenceTransformer(
                cls.MODEL_NAME
            )

            print("Local embedding model: OK")

    @classmethod
    def get_embeddings(cls):

        cls._initialize()

        return cls

    @classmethod
    def embed_documents(cls, texts):

        cls._initialize()

        if not texts:
            return []

        embeddings = cls._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.tolist()

    @classmethod
    def embed_query(cls, text):

        cls._initialize()

        embedding = cls._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()