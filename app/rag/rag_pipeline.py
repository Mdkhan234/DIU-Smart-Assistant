from app.rag.retriever import Retriever
from app.rag.llm import LLMService
from app.rag.prompt import PromptBuilder
from app.rag.question_rewriter import QuestionRewriter
from app.memory.memory import memory
from app.core.config import settings


class RAGPipeline:

    @staticmethod
    def ask(session_id: str, question: str):

        # =================================================
        # 1. Get Conversation History
        # =================================================

        history = memory.get_history(
            session_id
        )

        history_text = ""

        for item in history:

            history_text += (
                f"{item['role']}: "
                f"{item['content']}\n"
            )

        # =================================================
        # 2. Rewrite Question
        # =================================================

        standalone_question = (
            QuestionRewriter.rewrite(
                history_text,
                question
            )
        )

        # =================================================
        # 3. Retrieve Relevant Documents
        # =================================================
        
        retrieval_results = Retriever.retrieve(
            query=standalone_question,
            k=settings.TOP_K
        )
        # =================================================
        # 4. Retrieval Debug
        # =================================================

        if settings.DEBUG_RETRIEVAL:

            print(
                "\n================ RETRIEVAL DEBUG ================"
            )

            print(
                "Original Question:",
                question
            )

            print(
                "Standalone Question:",
                standalone_question
            )

            print(
                "Retrieved Chunks:",
                len(retrieval_results)
            )

            for i, result in enumerate(
                retrieval_results,
                start=1
            ):

                print(
                    f"\n--- RESULT {i} ---"
                )

                print(
                    "Score:",
                    round(
                        result["score"],
                        4
                    )
                )

                print(
                    "Source:",
                    result["metadata"].get(
                        "source"
                    )
                )

                print(
                    "Page:",
                    result["metadata"].get(
                        "page"
                    )
                )

                print(
                    "Content:"
                )

                print(
                    result["content"][:700]
                )

            print(
                "\n==================================================\n"
            )

        # =================================================
        # 5. No Relevant Documents
        # =================================================

        if not retrieval_results:

            fallback = (
                "I couldn't find that information "
                "in the uploaded university documents."
            )

            memory.add_message(
                session_id,
                "User",
                question
            )

            memory.add_message(
                session_id,
                "Assistant",
                fallback
            )

            return {
                "answer": fallback,

                "standalone_question":
                    standalone_question,

                "retrieved_documents": [],

                "sources": []
            }

        # =================================================
        # 6. Build Focused Context
        # =================================================

        context_parts = []

        total_chars = 0

        max_context_chars = (
            settings.MAX_CONTEXT_CHARS
        )

        for result in retrieval_results:

            content = (
                result["content"]
                .strip()
            )

            if not content:
                continue

            remaining_chars = (
                max_context_chars
                - total_chars
            )

            if remaining_chars <= 0:
                break

            if len(content) > remaining_chars:

                content = content[
                    :remaining_chars
                ]

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
            )

            source = metadata.get(
                "source",
                "Unknown source"
            )

            page = metadata.get(
                "page",
                "Unknown page"
            )

            # Add source marker to context
            context_parts.append(
                f"[SOURCE: {source} | PAGE: {page}]\n"
                f"{content}"
            )

            total_chars += len(content)

        context = (
            "\n\n--- DOCUMENT CHUNK ---\n\n"
            .join(context_parts)
        )

        # =================================================
        # 7. Load Prompt
        # =================================================

        prompt = PromptBuilder.get_prompt()

        # =================================================
        # 8. Load LLM
        # =================================================

        llm = LLMService.get_llm()

        # =================================================
        # 9. Build Chain
        # =================================================

        chain = prompt | llm

        # =================================================
        # 10. Generate Answer
        # =================================================

        response = chain.invoke(
            {
                "history": history_text,

                "context": context,

                "question":
                    standalone_question
            }
        )

        answer = response.content.strip()

# =================================================
# Clean duplicated fallback responses
# =================================================

        fallback_message = (
            "I couldn't find that information in the uploaded "
            "university documents."
        )

        if fallback_message in answer:

            # If the retrieved context exists, do not allow
            # the LLM to incorrectly claim that nothing was found.
            if retrieval_results:

                # Ask the LLM to answer again with a very strict instruction.
                retry_prompt = PromptBuilder.get_prompt()

                retry_chain = retry_prompt | llm

                retry_response = retry_chain.invoke(
                    {
                        "history": history_text,
                        "context": context,
                        "question": standalone_question
                    }
                )

                answer = retry_response.content.strip()

        # Remove accidental duplicate fallback text
        if answer.count(fallback_message) > 1:

            answer = fallback_message

        # =================================================
        # 11. Save User Message
        # =================================================

        memory.add_message(
            session_id,
            "User",
            question
        )

        # =================================================
        # 12. Save Assistant Message
        # =================================================

        memory.add_message(
            session_id,
            "Assistant",
            answer
        )

        # =================================================
        # 13. Prepare Sources
        # =================================================

        sources = []

        seen_sources = set()

        for result in retrieval_results:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
            )

            filename = metadata.get(
                "source"
            )

            page = metadata.get(
                "page"
            )

            key = (
                filename,
                page
            )

            if key in seen_sources:
                continue

            seen_sources.add(
                key
            )

            sources.append(
                {
                    "filename":
                        filename,

                    "page":
                        page,

                    "score":
                        round(
                            result["score"],
                            4
                        )
                }
            )

        # =================================================
        # 14. Retrieved Document Debug Info
        # =================================================

        retrieved_documents = []

        for result in retrieval_results:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
            )

            retrieved_documents.append(
                {
                    "filename":
                        metadata.get(
                            "source"
                        ),

                    "page":
                        metadata.get(
                            "page"
                        ),

                    "score":
                        round(
                            result["score"],
                            4
                        ),

                    "content_preview":
                        result["content"][:300]
                }
            )

        # =================================================
        # 15. Final Response
        # =================================================

        return {
            "answer":
                answer,

            "standalone_question":
                standalone_question,

            "retrieved_documents":
                retrieved_documents,

            "sources":
                sources
        }