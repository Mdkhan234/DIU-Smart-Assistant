import re
import requests

from app.core.config import settings


class LLM:

    # ============================================================
    # CONFIGURATION
    # ============================================================

    OLLAMA_URL = (
        "http://127.0.0.1:11434/api/generate"
    )

    MODEL_NAME = (
        settings.MODEL_NAME
        or "llama3.2:1b"
    )

    TIMEOUT = 120

    # ============================================================
    # ADMISSION SCHEDULE EXTRACTION
    # ============================================================

    @staticmethod
    def extract_admission_schedule(
        question: str,
        context: str
    ) -> str | None:

        question_lower = (
            question.lower().strip()
        )

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

        # --------------------------------------------------------
        # Faculty
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Semester
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Normalize context
        # --------------------------------------------------------

        normalized_context = (
            context
            .replace("\xa0", " ")
        )

        lines = [
            line.strip()
            for line in normalized_context.splitlines()
            if line.strip()
        ]

        # --------------------------------------------------------
        # Search schedule
        # --------------------------------------------------------

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

            # ----------------------------------------------------
            # Semester
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # Match
            # ----------------------------------------------------

            if faculty_match and semester_match:

                time_match = re.search(
                    r"(\d{1,2}:\d{2}\s*(?:am|pm))"
                    r"\s*(?:to|-)\s*"
                    r"(\d{1,2}:\d{2}\s*(?:am|pm))",
                    line,
                    re.IGNORECASE
                )

                if time_match:

                    start_time = (
                        time_match.group(1)
                    )

                    end_time = (
                        time_match.group(2)
                    )

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

            program = (
                match.group(1)
                .strip()
            )

            if program:
                programs.append(program)

        if not programs:
            return None

        return (
            "The programs available at Daffodil "
            "International University are:\n\n"
            + "\n".join(
                f"{index}. {program}"
                for index, program in enumerate(
                    programs,
                    start=1
                )
            )
        )

    # ============================================================
    # GENERAL GENERATION
    # ============================================================

    @staticmethod
    def generate(
        question: str,
        context: str
    ) -> str:

        # --------------------------------------------------------
        # Validate question
        # --------------------------------------------------------

        if not question or not question.strip():

            return (
                "Please provide a question."
            )

        # --------------------------------------------------------
        # Validate context
        # --------------------------------------------------------

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

        # ========================================================
        # GENERAL RAG PROMPT
        # ========================================================

        prompt = f"""
You are DIU Smart Assistant, an AI assistant
for Daffodil International University (DIU).

Your job is to answer the user's question using
ONLY the information contained in the provided
DIU DOCUMENT CONTEXT.

IMPORTANT:

The user expects a useful, complete answer,
not just a keyword or a one-line fragment.

Follow these rules carefully:

1. Use ONLY the provided DIU DOCUMENT CONTEXT.

2. Do NOT use outside knowledge.

3. Do NOT invent facts.

4. Answer the actual question directly.

5. If the context contains several relevant facts,
   include the important relevant facts.

6. For a normal factual question, give approximately
   2 to 5 clear sentences when the context supports it.

7. If the context contains a definition or description,
   explain the definition clearly instead of returning
   only the institution's name.

8. If the context contains a list, preserve the important
   items in the list.

9. If the user asks "what is", "what are", "tell me about",
   or "explain", provide a short explanatory answer.

10. If the user asks for a specific value such as a date,
    time, fee, deadline, requirement, or eligibility,
    give the exact value from the context.

11. If multiple similar values exist, choose the value
    that matches the user's exact question.

12. Do not combine unrelated information.

13. If the answer is not available in the context,
    say exactly:

    "I could not find this information in the
    available DIU documents."

14. Never mention internal technical details.

Do NOT mention:

- RAG
- retrieval
- embeddings
- ChromaDB
- vector database
- similarity score
- context retrieval
- prompt
- model
- Ollama

15. Do not start the answer with unnecessary phrases such as:

"According to the context..."
"Based on the documents..."
"The context says..."

16. Be concise but informative.

17. Never answer with only a name when the question
    asks for an explanation or description.

USER QUESTION:
{question}

DIU DOCUMENT CONTEXT:
{context}

FINAL ANSWER:
"""

        # ========================================================
        # OLLAMA REQUEST
        # ========================================================

        payload = {
            "model": LLM.MODEL_NAME,

            "prompt": prompt,

            "stream": False,

            "options": {

                # Deterministic answers
                "temperature": 0.0,

                # Allow enough answer tokens
                "num_predict": 400,

                # Better context processing
                "num_ctx": 4096,
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
                data.get(
                    "response",
                    ""
                )
                or ""
            ).strip()

            # ----------------------------------------------------
            # Clean common unwanted prefixes
            # ----------------------------------------------------

            answer = re.sub(
                r"^(FINAL ANSWER:\s*)+",
                "",
                answer,
                flags=re.IGNORECASE
            ).strip()

            # ----------------------------------------------------
            # Empty response
            # ----------------------------------------------------

            if not answer:

                return (
                    "I could not generate an answer "
                    "from the available DIU documents."
                )

            return answer

        # ========================================================
        # ERROR HANDLING
        # ========================================================

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
                "Unable to connect to the AI model."
            )

        except Exception as error:

            print(
                "[LLM] Unexpected error:",
                error
            )

            return (
                "An error occurred while generating "
                "the answer."
            )