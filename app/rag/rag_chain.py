from app.core.config import settings
from app.rag.vector_store import VectorStore
from google import genai


class RAGChain:

    _client = None

    @classmethod
    def _initialize(cls):

        if cls._client is None:

            if not settings.GEMINI_API_KEY:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured."
                )

            cls._client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

    @classmethod
    def answer(cls, question: str, k: int = 5):

        cls._initialize()

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        # =====================================================
        # 1. LOAD VECTOR DATABASE
        # =====================================================

        db = VectorStore.load()

        # =====================================================
        # 2. RETRIEVE RELEVANT DOCUMENT CHUNKS
        # =====================================================

        documents = db.similarity_search(
            question,
            k=k,
        )

        if not documents:

            return {
                "answer": (
                    "I could not find relevant information "
                    "in the provided DIU documents."
                ),
                "sources": [],
                "retrieved_chunks": 0,
            }

        # =====================================================
        # 3. BUILD CONTEXT + CLEAN SOURCES
        # =====================================================

        context_parts = []
        sources = []

        seen_sources = set()

        for index, document in enumerate(
            documents,
            start=1,
        ):

            content = (
                document.page_content
                or ""
            ).strip()

            if not content:
                continue

            metadata = (
                document.metadata
                or {}
            )

            # ---------------------------------------------
            # Source filename
            # ---------------------------------------------

            filename = (
                metadata.get("source")
                or metadata.get("file")
                or metadata.get("filename")
                or "Unknown document"
            )

            # ---------------------------------------------
            # Page number
            # ---------------------------------------------

            page = metadata.get("page")

            if isinstance(page, int):
                page = page + 1

            # ---------------------------------------------
            # Remove duplicate source cards
            # ---------------------------------------------

            source_key = (
                str(filename),
                page,
            )

            if source_key not in seen_sources:

                seen_sources.add(source_key)

                sources.append(
                    {
                        "file": str(filename),
                        "page": page,
                    }
                )

            # ---------------------------------------------
            # Context
            # ---------------------------------------------

            context_parts.append(
                f"""
[Source {index}]
Document: {filename}
Page: {page}

{content}
""".strip()
            )

        if not context_parts:

            return {
                "answer": (
                    "I could not find usable information "
                    "in the provided DIU documents."
                ),
                "sources": sources,
                "retrieved_chunks": 0,
            }

        context = "\n\n".join(
            context_parts
        )

        # =====================================================
        # 4. RAG PROMPT
        # =====================================================

        prompt = f"""
You are DIU Smart Assistant, an AI assistant
for Daffodil International University (DIU).

Your task is to answer the user's question using
ONLY the information contained in the provided
DIU document context.

IMPORTANT RULES:

1. Use ONLY the provided context.

2. Never use outside knowledge.

3. Never invent facts, numbers, dates, fees,
   requirements, policies, programs, or links.

4. If the answer cannot be determined from the
   context, clearly say:

   "I could not find this information in the
   provided DIU documents."

5. If only part of the question can be answered,
   answer only the supported part and clearly
   mention what information is missing.

6. Give a direct answer first.

7. Use bullet points or short sections when
   that makes the answer easier to understand.

8. Preserve important terminology used by DIU.

9. Do not mention that you are an AI unless
   the user specifically asks.

10. Do not create fake citations.

11. When information comes from multiple sources,
    combine the information carefully.

12. Do not repeat the same information unnecessarily.

13. If the user asks about a specific DIU policy,
    requirement, fee, admission process, program,
    scholarship, credit transfer, or other official
    information, rely strictly on the retrieved
    documents.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        # =====================================================
        # 5. GENERATE ANSWER
        # =====================================================

        response = cls._client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        answer = (
            response.text.strip()
            if response.text
            else
            "I could not generate an answer from "
            "the provided DIU documents."
        )

        # =====================================================
        # 6. RETURN RAG RESULT
        # =====================================================

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(documents),
        }