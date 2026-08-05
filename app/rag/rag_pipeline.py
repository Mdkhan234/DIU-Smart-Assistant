from app.rag.vector_store import VectorStore
from app.rag.llm import LLMService
from app.rag.prompt import PromptBuilder
from app.memory.memory import memory


class RAGPipeline:

    @staticmethod
    def ask(session_id: str, question: str):

        # Load Vector Database
        db = VectorStore.load()

        # Retrieve Top 3 Relevant Chunks
        docs = db.similarity_search(
            question,
            k=5
        )

        # Build Document Context
        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        # Get Previous Conversation History
        history = memory.get_history(session_id)

        history_text = ""

        for item in history:
            history_text += f"{item['role']}: {item['content']}\n"

        # Merge History + Retrieved Context
        full_context = f"""
Conversation History:

{history_text}

-------------------------

Document Context:

{context}
"""

        # Load Prompt
        prompt = PromptBuilder.get_prompt()

        # Load LLM
        llm = LLMService.get_llm()

        # Build Chain
        chain = prompt | llm

        # Generate Response
        response = chain.invoke(
            {
                "context": full_context,
                "question": question
            }
        )

        # Save User Message
        memory.add_message(
            session_id,
            "User",
            question
        )

        # Save AI Response
        memory.add_message(
            session_id,
            "Assistant",
            response.content
        )

        return {
            "answer": response.content,
            "sources": [
                doc.metadata.get("page")
                for doc in docs
            ]
        }