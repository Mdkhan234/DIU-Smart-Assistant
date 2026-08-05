from langchain_ollama import ChatOllama

from app.core.config import settings


class LLMService:

    @staticmethod
    def get_llm():

        llm = ChatOllama(
            model=settings.MODEL_NAME,
            temperature=0
        )

        return llm