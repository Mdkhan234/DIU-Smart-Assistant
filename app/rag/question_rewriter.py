from app.rag.llm import LLMService


class QuestionRewriter:

    @staticmethod
    def rewrite(history: str, question: str) -> str:

        original_question = question.strip()

        # ============================================================
        # 1. No history -> question is already standalone
        # ============================================================

        if not history or not history.strip():
            return original_question

        # ============================================================
        # 2. Strong rewriting prompt
        # ============================================================

        prompt = f"""
You are the QUESTION REWRITER for DIU Smart Assistant.

Your ONLY task is to rewrite the LATEST USER QUESTION into a
standalone question that can be understood without conversation history.

You MUST NOT answer the question.

You MUST NOT retrieve information.

You MUST NOT invent facts.

You MUST preserve the user's intent.

============================================================
IMPORTANT REWRITING RULES
============================================================

RULE 1:
If the latest question is already standalone, return it unchanged.

RULE 2:
Resolve conversational references using the conversation history.

Examples:

"What about Health and Life Sciences?"
-->
"What is the admission test schedule for Health and Life Sciences?"

"What about CSE?"
-->
"What is the admission test schedule for CSE?"

"How much is it?"
-->
"How much is [the item being discussed]?"

"What about the previous one?"
-->
Rewrite using the immediately relevant topic from history.

RULE 3:
If the latest question contains a broad contextual term such as:

- Bi Semester
- Tri Semester
- Trimester
- Semester
- Engineering
- Science
- Business
- Health
- Humanities
- CSE

and the previous conversation clearly established a topic,
KEEP THAT TOPIC.

For example:

Previous question:
"What is the admission test schedule?"

Latest question:
"What about the Bi Semester?"

Correct rewrite:
"What is the admission test schedule for Bi Semester?"

NOT:
"Bi Semester"

NOT:
"What is Bi Semester?"

NOT:
"What does the admission test schedule for the Faculty of Engineering say?"

RULE 4:
If the previous question was about an admission test schedule and
the latest question asks:

"What about the Bi Semester?"

rewrite it as:

"What is the admission test schedule for Bi Semester?"

If the latest question asks:

"What about the Tri Semester?"

rewrite it as:

"What is the admission test schedule for Tri Semester?"

RULE 5:
If the previous question was about fees and the latest question says:

"What about Bi Semester?"

then preserve the fee topic.

Example:

Previous:
"What is the tuition fee for CSE?"

Latest:
"What about Bi Semester?"

Possible rewrite:
"What is the tuition fee for CSE Bi Semester?"

ONLY if the history clearly supports that interpretation.

RULE 6:
Never switch the topic.

If the previous topic is admission test schedule,
do NOT rewrite the question into:

- tuition fees
- waiver
- program requirements
- credit transfer
- courses
- admission requirements

unless the user explicitly changes the topic.

RULE 7:
Do not use unrelated retrieved documents.

You only see conversation history and the latest question.

RULE 8:
Do not add facts that are not present in the history.

RULE 9:
When resolving a reference, prefer the most recent relevant topic.

RULE 10:
Return ONLY the rewritten standalone question.

Do not return:

- explanations
- answers
- bullet points
- "Answer:"
- "Rewritten question:"
- quotation marks
- markdown

============================================================
CONVERSATION HISTORY
============================================================

{history}

============================================================
LATEST USER QUESTION
============================================================

{original_question}

============================================================
STANDALONE QUESTION
============================================================
"""

        # ============================================================
        # 3. Call LLM
        # ============================================================

        try:

            llm = LLMService.get_llm()

            response = llm.invoke(prompt)

            rewritten = response.content.strip()

        except Exception:

            return original_question

        # ============================================================
        # 4. Basic cleanup
        # ============================================================

        if not rewritten:
            return original_question

        # Remove accidental quotes
        rewritten = rewritten.strip('"').strip("'").strip()

        # ============================================================
        # 5. Remove common unwanted prefixes
        # ============================================================

        forbidden_prefixes = [
            "answer:",
            "rewritten question:",
            "standalone question:",
            "rewritten standalone question:",
            "here is the rewritten question:",
        ]

        lowered = rewritten.lower()

        for prefix in forbidden_prefixes:

            if lowered.startswith(prefix):

                rewritten = rewritten[
                    len(prefix):
                ].strip()

                break

        # ============================================================
        # 6. Final validation
        # ============================================================

        if not rewritten:
            return original_question

        # Prevent multi-line LLM explanations
        if "\n" in rewritten:

            first_line = rewritten.splitlines()[0].strip()

            if first_line:
                rewritten = first_line

        # ============================================================
        # 7. Rule-based protection for common contextual references
        # ============================================================
        #
        # The LLM sometimes returns:
        #
        # "Bi Semester"
        #
        # instead of:
        #
        # "What is the admission test schedule for Bi Semester?"
        #
        # We protect the most important conversational pattern here.
        # ============================================================

        lower_original = original_question.lower()

        admission_context = any(
            keyword in history.lower()
            for keyword in [
                "admission test schedule",
                "admission test",
                "exam time",
                "admission schedule",
            ]
        )

        # ------------------------------------------------------------
        # Bi Semester
        # ------------------------------------------------------------

        if (
            admission_context
            and "bi semester" in lower_original
            and (
                lower_original.startswith("what about")
                or lower_original.startswith("how about")
                or lower_original.startswith("and ")
            )
        ):

            return (
                "What is the admission test schedule "
                "for Bi Semester?"
            )

        # ------------------------------------------------------------
        # Tri Semester
        # ------------------------------------------------------------

        if (
            admission_context
            and (
                "tri semester" in lower_original
                or "trimester" in lower_original
            )
            and (
                lower_original.startswith("what about")
                or lower_original.startswith("how about")
                or lower_original.startswith("and ")
            )
        ):

            return (
                "What is the admission test schedule "
                "for Tri Semester?"
            )

        # ============================================================
        # 8. Health and Life Sciences protection
        # ============================================================

        if (
            admission_context
            and "health and life sciences" in lower_original
            and (
                lower_original.startswith("what about")
                or lower_original.startswith("how about")
            )
        ):

            return (
                "What is the admission test schedule "
                "for Health and Life Sciences?"
            )

        # ============================================================
        # 9. Return rewritten question
        # ============================================================

        return rewritten