from pathlib import Path
from typing import List, Dict, Any
import re

from app.rag.vector_store import VectorStore


class Retriever:

    # ============================================================
    # CONFIGURATION
    # ============================================================

    INITIAL_K = 60

    MAX_RESULTS = 10
    PROGRAM_RESULTS = 30

    MAX_CHUNKS_PER_PAGE = 2

    INTENT_BONUS = 0.12
    ENTITY_BONUS = 0.10

    # ============================================================
    # QUERY ENTITY DETECTION
    # ============================================================

    @staticmethod
    def detect_entities(query: str):

        q = (query or "").lower().strip()

        return {
            "health": (
                "health and life sciences" in q
                or "health & life sciences" in q
                or "health bi semester" in q
                or "health tri semester" in q
            ),

            "engineering": (
                "engineering" in q
            ),

            "science_it": (
                "science and information technology" in q
                or "science & information technology" in q
                or "science and it" in q
                or q == "sit"
            ),

            "humanities": (
                "humanities and social science" in q
                or "humanities and social sciences" in q
                or "humanities & social sciences" in q
            ),

            "business": (
                "business and entrepreneurship" in q
                or "business entrepreneurship" in q
            ),

            "agriculture": (
                "agricultural science" in q
            ),

            "tri": (
                "tri semester" in q
                or "trimester" in q
                or "tri-semester" in q
            ),

            "bi": (
                "bi semester" in q
                or "bisemester" in q
                or "bi-semester" in q
            ),
        }

    # ============================================================
    # DOCUMENT ENTITY DETECTION
    # ============================================================

    @staticmethod
    def document_entities(content: str):

        text = (content or "").lower()

        return {
            "health": (
                "health and life sciences" in text
                or "health & life sciences" in text
            ),

            "engineering": (
                "faculty of engineering" in text
                or "engineering" in text
            ),

            "science_it": (
                "science and information technology" in text
                or "science & information technology" in text
            ),

            "humanities": (
                "humanities and social science" in text
                or "humanities and social sciences" in text
                or "humanities & social sciences" in text
            ),

            "business": (
                "business and entrepreneurship" in text
            ),

            "agriculture": (
                "agricultural science" in text
            ),

            "tri": (
                "tri semester" in text
                or "trimester" in text
                or "tri-semester" in text
            ),

            "bi": (
                "bi semester" in text
                or "bisemester" in text
                or "bi-semester" in text
            ),
        }

    # ============================================================
    # QUERY INTENT DETECTION
    # ============================================================

    @staticmethod
    def detect_intent(query: str):

        q = (query or "").lower().strip()

        return {

            "programs": any(
                keyword in q
                for keyword in [

                    "what programs",
                    "which programs",
                    "available programs",
                    "programs are available",
                    "programs at diu",
                    "programs in diu",

                    "what departments",
                    "departments at diu",
                    "departments are available",
                    "which departments",

                    "faculties at diu",
                    "which faculties",
                    "faculty list",

                    "department list",
                    "program list",
                    "list of programs",

                    "degree programs",
                    "academic programs",

                    "what courses does diu offer",
                    "what degrees does diu offer",
                    "degrees available at diu",

                    "courses available at diu",
                    "courses does diu offer",

                    "subjects available at diu",
                ]
            ),

            "admission_test": any(
                keyword in q
                for keyword in [
                    "admission test",
                    "admission exam",
                    "admission schedule",
                    "exam schedule",
                    "test schedule",
                    "exam time",
                    "test time",
                ]
            ),

            "fees": any(
                keyword in q
                for keyword in [
                    "tuition fee",
                    "tuition fees",
                    "admission fee",
                    "semester fee",
                    "cost",
                    "fees",
                    "fee",
                ]
            ),

            "waiver": any(
                keyword in q
                for keyword in [
                    "waiver",
                    "scholarship",
                    "financial aid",
                    "discount",
                ]
            ),

            "credit_transfer": any(
                keyword in q
                for keyword in [
                    "credit transfer",
                    "transfer credit",
                    "transfer from another university",
                ]
            ),
        }

    # ============================================================
    # BASIC VECTOR SEARCH
    # ============================================================

    @staticmethod
    def search(query: str, k: int = 5):

        db = VectorStore.load()

        results = db.similarity_search_with_score(
            query,
            k=k
        )

        output = []

        for doc, score in results:

            distance = float(score)

            output.append(
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata or {},

                    "score": round(distance, 4),
                    "original_score": round(distance, 4),

                    "entity_bonus": 0.0,
                    "intent_bonus": 0.0,
                }
            )

        return output

    # ============================================================
    # FILENAME
    # ============================================================

    @staticmethod
    def get_filename(result) -> str:

        metadata = result.get("metadata", {}) or {}

        source = metadata.get("source", "")

        return Path(str(source)).name.lower()

    # ============================================================
    # PROGRAM DOCUMENT
    # ============================================================

    @staticmethod
    def is_program_document(result) -> bool:

        filename = Retriever.get_filename(result)

        return (
            filename.startswith("programs")
            or "program" in filename
        )

    # ============================================================
    # PROGRAM CONTENT SCORE
    # ============================================================

    @staticmethod
    def calculate_program_content_score(content: str):

        text = (content or "").lower()

        score = 0.0

        strong_keywords = [
            "b. sc. in",
            "b.sc. in",
            "bachelor of",
            "master of",
            "program overview",
            "program objective",
            "credit requirement",
            "tuition fees",
            "career paths",
            "eligibilities",
            "department of",
            "faculty of",
        ]

        for keyword in strong_keywords:
            if keyword in text:
                score += 0.02

        program_keywords = [
            "computer science and engineering",
            "software engineering",
            "data science",
            "cyber security",
            "robotics",
            "multimedia",
            "information technology",
            "computing and information system",
            "information systems",
            "business administration",
            "electrical engineering",
            "civil engineering",
            "mechanical engineering",
            "architecture",
            "pharmacy",
            "law",
            "english",
            "journalism",
        ]

        for keyword in program_keywords:
            if keyword in text:
                score += 0.015

        return min(score, 0.20)

    # ============================================================
    # INTENT BONUS
    # ============================================================

    @staticmethod
    def calculate_intent_bonus(query: str, result):

        intents = Retriever.detect_intent(query)

        if not intents["programs"]:
            return 0.0

        content = result.get("content", "") or ""
        filename = Retriever.get_filename(result)

        if filename.startswith("programs"):

            content_score = (
                Retriever.calculate_program_content_score(
                    content
                )
            )

            return round(
                Retriever.INTENT_BONUS + content_score,
                4
            )

        bonus = 0.0

        text = content.lower()

        useful_keywords = [
            "bachelor of",
            "bachelor's degree",
            "master of",
            "department of",
            "faculty of",
            "degree program",
            "academic program",
            "program overview",
        ]

        matches = sum(
            1
            for keyword in useful_keywords
            if keyword in text
        )

        if matches >= 3:
            bonus += 0.08
        elif matches >= 1:
            bonus += 0.04

        negative_keywords = [
            "waiver",
            "scholarship",
            "financial aid",
            "credit transfer",
            "student exchange",
            "payment guideline",
            "payment system",
            "hall facilities",
            "student portal",
            "admission flow chart",
        ]

        negative_matches = sum(
            1
            for keyword in negative_keywords
            if keyword in text
        )

        if negative_matches >= 3:
            bonus -= 0.08
        elif negative_matches >= 1:
            bonus -= 0.04

        return round(max(bonus, 0.0), 4)

    # ============================================================
    # ENTITY BONUS
    # ============================================================

    @staticmethod
    def calculate_entity_bonus(query: str, result):

        entities = Retriever.detect_entities(query)

        document = Retriever.document_entities(
            result.get("content", "")
        )

        bonus = 0.0

        faculty_pairs = [
            ("health", 0.10),
            ("engineering", 0.10),
            ("science_it", 0.10),
            ("humanities", 0.10),
            ("business", 0.10),
            ("agriculture", 0.10),
        ]

        for entity, value in faculty_pairs:

            if (
                entities[entity]
                and document[entity]
            ):
                bonus += value

        if entities["tri"] and document["tri"]:
            bonus += 0.10

        if entities["bi"] and document["bi"]:
            bonus += 0.10

        return round(bonus, 4)

    # ============================================================
    # ADJUST SCORE
    # ============================================================

    @staticmethod
    def calculate_adjusted_score(query: str, result):

        original_score = float(
            result.get(
                "original_score",
                result.get("score", 1.0)
            )
        )

        entity_bonus = (
            Retriever.calculate_entity_bonus(
                query,
                result
            )
        )

        intent_bonus = (
            Retriever.calculate_intent_bonus(
                query,
                result
            )
        )

        adjusted_score = (
            original_score
            - entity_bonus
            - intent_bonus
        )

        adjusted_score = max(
            adjusted_score,
            0.0
        )

        return (
            round(adjusted_score, 4),
            entity_bonus,
            intent_bonus
        )

    # ============================================================
    # RERANK
    # ============================================================

    @staticmethod
    def rerank(query: str, results):

        reranked = []

        for result in results:

            item = dict(result)

            (
                adjusted_score,
                entity_bonus,
                intent_bonus
            ) = Retriever.calculate_adjusted_score(
                query,
                result
            )

            item["score"] = adjusted_score
            item["entity_bonus"] = entity_bonus
            item["intent_bonus"] = intent_bonus

            reranked.append(item)

        reranked.sort(
            key=lambda x: x["score"]
        )

        return reranked

    # ============================================================
    # ENTITY FILTER
    # ============================================================

    @staticmethod
    def filter_results(query: str, results):

        entities = Retriever.detect_entities(query)

        faculty_requested = any(
            [
                entities["health"],
                entities["engineering"],
                entities["science_it"],
                entities["humanities"],
                entities["business"],
                entities["agriculture"],
            ]
        )

        semester_requested = (
            entities["tri"]
            or entities["bi"]
        )

        if not faculty_requested and not semester_requested:
            return results

        filtered = []

        for result in results:

            document = Retriever.document_entities(
                result.get("content", "")
            )

            faculty_match = True

            if faculty_requested:

                faculty_match = False

                for faculty in [
                    "health",
                    "engineering",
                    "science_it",
                    "humanities",
                    "business",
                    "agriculture",
                ]:

                    if (
                        entities[faculty]
                        and document[faculty]
                    ):
                        faculty_match = True
                        break

            semester_match = True

            if semester_requested:

                semester_match = False

                if entities["tri"] and document["tri"]:
                    semester_match = True

                if entities["bi"] and document["bi"]:
                    semester_match = True

            if faculty_match and semester_match:
                filtered.append(result)

        return filtered

    # ============================================================
    # DEDUPLICATION
    # ============================================================

    @staticmethod
    def deduplicate(results):

        unique = []
        seen = set()

        for result in results:

            metadata = result.get(
                "metadata",
                {}
            ) or {}

            source = str(
                metadata.get(
                    "source",
                    ""
                )
            ).lower()

            page = metadata.get("page")

            content = (
                result.get("content", "")
                or ""
            ).strip()

            normalized_content = (
                " ".join(
                    content.split()
                ).lower()
            )

            key = (
                source,
                page,
                normalized_content
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(result)

        return unique

    # ============================================================
    # GET PROGRAM DOCUMENTS
    # ============================================================

    @staticmethod
    def get_program_documents():

        db = VectorStore.load()

        program_results = []

        # --------------------------------------------------------
        # First retrieval
        # --------------------------------------------------------

        queries = [
            "Daffodil International University programs",
            "DIU academic programs",
            "degree programs departments faculties",
            "Bachelor of Science programs",
            "Bachelor of Business programs",
            "Master programs",
        ]

        seen = set()

        for search_query in queries:

            try:

                docs = db.similarity_search(
                    search_query,
                    k=150
                )

            except Exception as error:

                print(
                    "[Retriever] Program retrieval error:",
                    error
                )

                continue

            for doc in docs:

                metadata = doc.metadata or {}

                source = str(
                    metadata.get(
                        "source",
                        ""
                    )
                )

                filename = Path(source).name.lower()

                if not (
                    filename.startswith("programs")
                    or "program" in filename
                ):
                    continue

                content = (
                    doc.page_content
                    or ""
                ).strip()

                if not content:
                    continue

                key = (
                    source,
                    metadata.get("page"),
                    content
                )

                if key in seen:
                    continue

                seen.add(key)

                program_results.append(
                    {
                        "content": content,
                        "metadata": metadata,
                        "score": 0.50,
                        "original_score": 0.50,
                        "entity_bonus": 0.0,
                        "intent_bonus": 0.0,
                    }
                )

        program_results = Retriever.deduplicate(
            program_results
        )

        print(
            "[Retriever] Program chunks found:",
            len(program_results)
        )

        return program_results

    # ============================================================
    # NORMALIZE PROGRAM LINE
    # ============================================================

    @staticmethod
    def normalize_program_line(line: str):

        if not line:
            return ""

        line = (
            line
            .replace("\uf0b7", " ")
            .replace("\xa0", " ")
        )

        # Remove common bullet characters
        line = re.sub(
            r"^[\s•·▪◦■□●\-–—]+",
            "",
            line
        )

        # Normalize whitespace
        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        return line

    # ============================================================
    # PROGRAM HEADING DETECTION
    # ============================================================

    @staticmethod
    def is_program_heading(line: str):

        text = Retriever.normalize_program_line(
            line
        )

        if not text:
            return False

        lower = text.lower()

        # --------------------------------------------------------
        # Reject obvious non-program headings
        # --------------------------------------------------------

        rejected = [
            "program overview",
            "program objective",
            "career paths",
            "tuition fees",
            "admission fees",
            "credit requirement",
            "credit requirements",
            "eligibilities",
            "eligibility",
            "total fees",
            "department overview",
            "faculty overview",
        ]

        if any(
            value in lower
            for value in rejected
        ):
            return False

        # --------------------------------------------------------
        # Degree/program patterns
        # --------------------------------------------------------

        patterns = [

            r"^b\.?\s*sc\.?\s*(?:\(hons\.?\))?\s+in\s+.+",

            r"^b\.?\s*eng\.?\s*(?:\(hons\.?\))?\s+in\s+.+",

            r"^b\.?\s*arch\.?\s*(?:\(hons\.?\))?\s+in\s+.+",

            r"^b\.?\s*pharm\.?\s*(?:\(hons\.?\))?\s+in\s+.+",

            r"^bba\s+(?:in\s+)? .+",

            r"^bca\s+(?:in\s+)? .+",

            r"^mba\s+(?:in\s+)? .+",

            r"^m\.?\s*sc\.?\s+(?:in\s+)? .+",

            r"^m\.?\s*eng\.?\s+(?:in\s+)? .+",

            r"^master\s+of\s+.+",

            r"^bachelor\s+of\s+.+",

            r"^ll\.?\s*b\.?\s*(?:\(hons\.?\))?.+",

            r"^ll\.?\s*m\.?\s+.+",

        ]

        for pattern in patterns:

            if re.match(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False

    # ============================================================
    # EXTRACT PROGRAM NAMES
    # ============================================================

    @staticmethod
    def extract_program_names():

        documents = Retriever.get_program_documents()

        if not documents:
            print(
                "[Retriever] No program documents found."
            )
            return []

        programs = []
        seen = set()

        # --------------------------------------------------------
        # Sort by page number
        # --------------------------------------------------------

        documents = sorted(
            documents,
            key=lambda x: (
                x.get(
                    "metadata",
                    {}
                ).get(
                    "page",
                    999999
                ),
                x.get(
                    "content",
                    ""
                )
            )
        )

        # --------------------------------------------------------
        # Extract headings
        # --------------------------------------------------------

        for document in documents:

            content = (
                document.get(
                    "content",
                    ""
                )
                or ""
            )

            # Fix common encoding artifacts
            content = (
                content
                .replace("\uf0b7", " ")
                .replace("\xa0", " ")
            )

            lines = content.splitlines()

            for raw_line in lines:

                line = Retriever.normalize_program_line(
                    raw_line
                )

                if not line:
                    continue

                if not Retriever.is_program_heading(
                    line
                ):
                    continue

                # ------------------------------------------------
                # Reject very long paragraph-like text
                # ------------------------------------------------

                if len(line) > 180:
                    continue

                key = line.lower()

                if key in seen:
                    continue

                seen.add(key)
                programs.append(line)

        print(
            "[Retriever] Program names extracted:",
            len(programs)
        )

        return programs

    # ============================================================
    # PAGE DIVERSITY
    # ============================================================

    @staticmethod
    def diversify_results(
        results,
        max_results=10
    ):

        selected = []

        page_counts = {}

        for result in results:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
                or {}
            )

            source = metadata.get("source")
            page = metadata.get("page")

            page_key = (
                str(source),
                page
            )

            count = page_counts.get(
                page_key,
                0
            )

            if count >= Retriever.MAX_CHUNKS_PER_PAGE:
                continue

            selected.append(result)

            page_counts[page_key] = count + 1

            if len(selected) >= max_results:
                break

        return selected

    # ============================================================
    # PROGRAM SEARCH
    # ============================================================

    @staticmethod
    def search_programs(
        query: str,
        k: int = 10
    ):

        print(
            "[Retriever] Program intent detected"
        )

        candidates = (
            Retriever.get_program_documents()
        )

        if not candidates:
            return []

        # --------------------------------------------------------
        # Semantic search only as secondary ranking signal
        # --------------------------------------------------------

        try:

            db = VectorStore.load()

            semantic_results = (
                db.similarity_search_with_score(
                    query,
                    k=100
                )
            )

        except Exception as error:

            print(
                "[Retriever] Program semantic search error:",
                error
            )

            semantic_results = []

        semantic_map = {}

        for doc, distance in semantic_results:

            metadata = doc.metadata or {}

            source = str(
                metadata.get(
                    "source",
                    ""
                )
            )

            filename = Path(
                source
            ).name.lower()

            if not (
                filename.startswith("programs")
                or "program" in filename
            ):
                continue

            key = (
                source,
                metadata.get("page"),
                (
                    doc.page_content
                    or ""
                ).strip()
            )

            semantic_map[key] = float(distance)

        scored = []

        for result in candidates:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
                or {}
            )

            source = str(
                metadata.get(
                    "source",
                    ""
                )
            )

            page = metadata.get("page")

            content = (
                result.get(
                    "content",
                    ""
                )
                or ""
            ).strip()

            key = (
                source,
                page,
                content
            )

            semantic_distance = semantic_map.get(
                key,
                0.50
            )

            content_bonus = (
                Retriever.calculate_program_content_score(
                    content
                )
            )

            adjusted = max(
                semantic_distance - content_bonus,
                0.0
            )

            item = dict(result)

            item["score"] = round(
                adjusted,
                4
            )

            item["original_score"] = round(
                semantic_distance,
                4
            )

            item["intent_bonus"] = round(
                content_bonus,
                4
            )

            scored.append(item)

        scored.sort(
            key=lambda x: x["score"]
        )

        diversified = (
            Retriever.diversify_results(
                scored,
                max_results=min(
                    k,
                    Retriever.PROGRAM_RESULTS
                )
            )
        )

        # --------------------------------------------------------
        # Fill if diversification was insufficient
        # --------------------------------------------------------

        if len(diversified) < k:

            selected_keys = set()

            for item in diversified:

                metadata = (
                    item.get(
                        "metadata",
                        {}
                    )
                    or {}
                )

                selected_keys.add(
                    (
                        str(
                            metadata.get(
                                "source",
                                ""
                            )
                        ),
                        metadata.get("page"),
                        (
                            item.get(
                                "content",
                                ""
                            )
                            or ""
                        ).strip()
                    )
                )

            for item in scored:

                metadata = (
                    item.get(
                        "metadata",
                        {}
                    )
                    or {}
                )

                key = (
                    str(
                        metadata.get(
                            "source",
                            ""
                        )
                    ),
                    metadata.get("page"),
                    (
                        item.get(
                            "content",
                            ""
                        )
                        or ""
                    ).strip()
                )

                if key in selected_keys:
                    continue

                diversified.append(item)
                selected_keys.add(key)

                if len(diversified) >= k:
                    break

        print(
            "[Retriever] Final program results:",
            len(diversified)
        )

        return diversified[:k]

    # ============================================================
    # SEARCH WITH FALLBACK
    # ============================================================

    @staticmethod
    def search_with_fallback(
        query: str,
        k: int = 5
    ):

        intents = Retriever.detect_intent(query)

        if intents["programs"]:

            return Retriever.search_programs(
                query=query,
                k=max(k, 15)
            )

        results = Retriever.search(
            query=query,
            k=max(
                k,
                Retriever.INITIAL_K
            )
        )

        results = Retriever.deduplicate(
            results
        )

        reranked = Retriever.rerank(
            query,
            results
        )

        filtered = Retriever.filter_results(
            query,
            reranked
        )

        entities = Retriever.detect_entities(
            query
        )

        has_entity = any(
            entities.values()
        )

        if has_entity:

            if filtered:
                return filtered[:k]

            return reranked[:k]

        return reranked[:k]

    # ============================================================
    # SAME PAGE CONTEXT EXPANSION
    # ============================================================

    @staticmethod
    def expand_page_context(results):

        if not results:
            return results

        db = VectorStore.load()

        expanded = list(results)

        existing = set()

        for result in results:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
                or {}
            )

            existing.add(
                (
                    metadata.get("source"),
                    metadata.get("page"),
                    (
                        result.get(
                            "content",
                            ""
                        )
                        or ""
                    ).strip()
                )
            )

        source_pages = set()

        for result in results:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
                or {}
            )

            source = metadata.get("source")
            page = metadata.get("page")

            if source is not None and page is not None:

                source_pages.add(
                    (
                        source,
                        page
                    )
                )

        for result in results:

            content = (
                result.get(
                    "content",
                    ""
                )
                or ""
            ).strip()

            if not content:
                continue

            try:

                related = db.similarity_search(
                    content,
                    k=4
                )

            except Exception as error:

                print(
                    "[Retriever] Page expansion error:",
                    error
                )

                continue

            for doc in related:

                metadata = doc.metadata or {}

                source = metadata.get("source")
                page = metadata.get("page")

                if (
                    source,
                    page
                ) not in source_pages:
                    continue

                doc_content = (
                    doc.page_content
                    or ""
                ).strip()

                if not doc_content:
                    continue

                key = (
                    source,
                    page,
                    doc_content
                )

                if key in existing:
                    continue

                existing.add(key)

                expanded.append(
                    {
                        "content": doc_content,
                        "metadata": metadata,

                        "score": result.get(
                            "score",
                            1.0
                        ),

                        "original_score": result.get(
                            "original_score",
                            result.get(
                                "score",
                                1.0
                            )
                        ),

                        "entity_bonus": result.get(
                            "entity_bonus",
                            0.0
                        ),

                        "intent_bonus": result.get(
                            "intent_bonus",
                            0.0
                        ),
                    }
                )

        return expanded

    # ============================================================
    # FINAL RETRIEVAL
    # ============================================================

    @staticmethod
    def retrieve(
        query: str,
        k: int = 5
    ):

        intents = Retriever.detect_intent(query)

        # --------------------------------------------------------
        # Program query
        # --------------------------------------------------------

        if intents["programs"]:

            return Retriever.search_programs(
                query=query,
                k=max(k, 15)
            )

        # --------------------------------------------------------
        # Normal query
        # --------------------------------------------------------

        results = Retriever.search_with_fallback(
            query=query,
            k=k
        )

        results = Retriever.deduplicate(
            results
        )

        results = Retriever.expand_page_context(
            results
        )

        results = Retriever.deduplicate(
            results
        )

        results.sort(
            key=lambda x: x.get(
                "score",
                1.0
            )
        )

        return results[:k]

    # ============================================================
    # API COMPATIBILITY
    # ============================================================

    @staticmethod
    def search_relevant(
        query: str,
        k: int = 5
    ):

        return Retriever.retrieve(
            query=query,
            k=k
        )