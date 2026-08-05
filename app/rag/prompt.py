from langchain_core.prompts import ChatPromptTemplate


class PromptBuilder:

    @staticmethod
    def get_prompt():

        template = """
You are DIU Smart Assistant.

Answer ONLY from the provided university documents.

If the answer is not found in the context,
reply with:

"I couldn't find that information in the uploaded university documents."

--------------------

Context:

{context}

--------------------

Question:

{question}

Answer:
"""

        return ChatPromptTemplate.from_template(template)