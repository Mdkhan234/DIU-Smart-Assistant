import re
import requests

from openai import OpenAI

from app.core.config import settings


class LLM:

    # ============================================================
    # CONFIGURATION
    # ============================================================

    OLLAMA_URL = (
        settings.OLLAMA_URL
        or "http://127.0.0.1:11434/api/generate"
    )

    MODEL_NAME = (
        settings.MODEL_NAME
        or "llama3.2:1b"
    )

    OPENAI_MODEL = (
        settings.OPENAI_MODEL
        or "gpt-5-mini"
    )

    OPENAI_API_KEY = (
        settings.OPENAI_API_KEY
        or ""
    )

    PROVIDER = (
        settings.LLM_PROVIDER
        or "ollama"
    ).lower().strip()

    TIMEOUT = 120

    # ============================================================
    # ADMISSION SCHEDULE EXTRACTION
    # ============================================================

    @staticmethod
    def extract_admission_schedule(
        question: str,
        context: str
    ) -> str | None:

        question_lower = question.lower().strip()

        admission_keywords = [
            "admission test",
            "admission exam",
            "admission schedule",
            "exam schedule",
            "test schedule",
            "exam time",
            "test time",
        ]

        if not any(
            keyword in question_lower
            for keyword in admission_keywords
        ):
            return None

        faculty_patterns = {

            "health": [
                "health and life sciences",
                "health & life sciences",
            ],

            "engineering": [
                "engineering",
            ],

            "science_it": [
                "science and information technology",
                "science & information technology",
            ],

            "humanities": [
                "humanities and social science",
                "humanities and social sciences",
                "humanities & social sciences",
            ],

            "business": [
                "business and entrepreneurship",
            ],

            "agriculture": [
                "agricultural science",
            ],
        }

        requested_faculty = None

        for faculty, patterns in faculty_patterns.items():

            if any(
                pattern in question_lower
                for pattern in patterns
            ):
                requested_faculty = faculty
                break

        requested_semester = None

        if (
            "bi semester" in question_lower
            or "bisemester" in question_lower
            or "bi-semester" in question_lower
        ):
            requested_semester = "bi"

        elif (
            "tri semester" in question_lower
            or "trimester" in question_lower
            or "tri-semester" in question_lower
        ):
            requested_semester = "tri"

        normalized_context = (
            context.replace("\xa0", " ")
        )

        lines = [
            line.strip()
            for line in normalized_context.splitlines()
            if line.strip()
        ]

        for line in lines:

            line_lower = line.lower()

            faculty_match = True
            semester_match = True

            if requested_faculty == "health":

                faculty_match = (
                    "health and life sciences"
                    in line_lower
                    or
                    "health & life sciences"
                    in line_lower
                )

            elif requested_faculty == "engineering":

                faculty_match = (
                    "engineering"
                    in line_lower
                )

            elif requested_faculty == "science_it":

                faculty_match = (
                    "science and information technology"
                    in line_lower
                    or
                    "science & information technology"
                    in line_lower
                )

            elif requested_faculty == "humanities":

                faculty_match = (
                    "humanities and social science"
                    in line_lower
                    or
                    "humanities and social sciences"
                    in line_lower
                    or
                    "humanities & social sciences"
                    in line_lower
                )

            elif requested_faculty == "business":

                faculty_match = (
                    "business and entrepreneurship"
                    in line_lower
                )

            elif requested_faculty == "agriculture":

                faculty_match = (
                    "agricultural science"
                    in line_lower
                )

            if requested_semester == "bi":

                semester_match = (
                    "bi semester" in line_lower
                    or "bisemester" in line_lower
                    or "bi-semester" in line_lower
                )

            elif requested_semester == "tri":

                semester_match = (
                    "tri semester" in line_lower
                    or "trimester" in line_lower
                    or "tri-semester" in line_lower
                )

            if faculty_match and semester_match:

                time_match = re.search(
                    r"(\d{1,2}:\d{2}\s*(?:am|pm))"
                    r"\s*(?:to|-)\s*"
                    r"(\d{1,2}:\d{2}\s*(?:am|pm))",
                    line,
                    re.IGNORECASE
                )

                if time_match:

                    start_time = time_match.group(1)
                    end_time = time_match.group(2)

                    faculty_name = (
                        requested_faculty
                        .replace("_", " ")
                        .title()
                    )

                    semester_name = (
                        "Bi Semester"
                        if requested_semester == "bi"
                        else "Tri Semester"
                    )

                    return (
                        f"The admission test schedule for "
                        f"{faculty_name} "
                        f"{semester_name} is "
                        f"{start_time} to {end_time}."
                    )

        return None

    # ============================================================
    # PROGRAM LIST ANSWER
    # ============================================================

    @staticmethod
    def extract_program_list_answer(
        question: str,
        context: str
    ):

        if not context.strip():
            return None

        if "DIU PROGRAM LIST:" not in context:
            return None

        lines = context.splitlines()

        programs = []

        for line in lines:

            line = line.strip()

            match = re.match(
                r"^\d+\.\s+(.+)$",
                line
            )

            if not match:
                continue

            program = match.group(1).strip()

            if program:
                programs.append(program)

        if not programs:
            return None

        return (
            "The programs available at DIU are:\n\n"
            + "\n".join(
                f"{index}. {program}"
                for index, program in enumerate(
                    programs,
                    start=1
                )
            )
        )

    # ============================================================
    # COMMON PROMPT
    # ============================================================

    @staticmethod
    def build_prompt(
        question: str,
        context: str
    ) -> str:

        return f"""
You are DIU Smart Assistant, an AI assistant for
Daffodil International University (DIU).

Answer the user's question using ONLY the
DIU DOCUMENT CONTEXT.

STRICT RULES:

1. Use only the provided document context.

2. Never use outside knowledge.

3. Never invent information.

4. If the requested answer is present in the context,
   answer it directly.

5. If multiple similar values exist, select the one
   matching the user's exact faculty, program,
   semester, category, or topic.

6. Do not combine unrelated information.

7. If the answer is not present in the context,
   clearly say that the information is not available
   in the provided DIU documents.

8. Do not mention internal technical details.

9. Do not mention:
   - embeddings
   - ChromaDB
   - vector database
   - retrieval
   - RAG
   - similarity scores

10. Preserve important items when the context contains
    a list.

11. For factual questions, use the exact value from
    the context.

12. Give a clear, natural and useful answer.

13. Do not unnecessarily make the answer extremely short.

USER QUESTION:
{question}

DIU DOCUMENT CONTEXT:
{context}

FINAL ANSWER:
"""

    # ============================================================
    # OLLAMA GENERATION
    # ============================================================

    @staticmethod
    def generate_with_ollama(
        prompt: str
    ) -> str:

        payload = {
            "model": LLM.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }

        try:

            response = requests.post(
                LLM.OLLAMA_URL,
                json=payload,
                timeout=LLM.TIMEOUT
            )

            response.raise_for_status()

            data = response.json()

            answer = (
                data.get("response", "")
                or ""
            ).strip()

            if not answer:

                return (
                    "I could not generate an answer "
                    "from the available DIU documents."
                )

            return answer

        except requests.exceptions.ConnectionError:

            return (
                "Ollama is not running. "
                "Please start Ollama and try again."
            )

        except requests.exceptions.Timeout:

            return (
                "The AI model took too long to respond. "
                "Please try again."
            )

        except requests.exceptions.RequestException as error:

            print(
                "[LLM] Ollama request error:",
                error
            )

            return (
                "Unable to connect to the Ollama model."
            )

        except Exception as error:

            print(
                "[LLM] Ollama unexpected error:",
                error
            )

            return (
                "An error occurred while generating "
                "the answer."
            )

    # ============================================================
    # OPENAI GENERATION
    # ============================================================

    @staticmethod
    def generate_with_openai(
        prompt: str
    ) -> str:

        if not LLM.OPENAI_API_KEY:

            return (
                "OpenAI API key is not configured."
            )

        try:

            client = OpenAI(
                api_key=LLM.OPENAI_API_KEY
            )

            response = client.responses.create(
                model=LLM.OPENAI_MODEL,
                input=prompt,
                temperature=0
            )

            answer = (
                getattr(
                    response,
                    "output_text",
                    ""
                )
                or ""
            ).strip()

            if not answer:

                return (
                    "I could not generate an answer "
                    "from the available DIU documents."
                )

            return answer

        except Exception as error:

            print(
                "[LLM] OpenAI request error:",
                error
            )

            return (
                "Unable to connect to the OpenAI model."
            )

    # ============================================================
    # GENERAL GENERATION
    # ============================================================

    @staticmethod
    def generate(
        question: str,
        context: str
    ) -> str:

        if not question or not question.strip():

            return "Please provide a question."

        if not context or not context.strip():

            return (
                "I could not find relevant information "
                "in the available DIU documents."
            )

        # --------------------------------------------------------
        # Direct admission schedule extraction
        # --------------------------------------------------------

        direct_schedule_answer = (
            LLM.extract_admission_schedule(
                question=question,
                context=context
            )
        )

        if direct_schedule_answer:

            return direct_schedule_answer

        # --------------------------------------------------------
        # Build common RAG prompt
        # --------------------------------------------------------

        prompt = LLM.build_prompt(
            question=question,
            context=context
        )

        # ========================================================
        # PROVIDER SWITCH
        # ========================================================

        if LLM.PROVIDER == "openai":

            return LLM.generate_with_openai(
                prompt
            )

        # Default provider = Ollama

        return LLM.generate_with_ollama(
            prompt
        )