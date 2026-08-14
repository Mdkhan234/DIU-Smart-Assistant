from typing import List, Dict


class ContextBuilder:

    # ============================================================
    # CONFIGURATION
    # ============================================================

    MAX_CONTEXT_CHARS = 6000
    MAX_CHUNKS = 6

    # ============================================================
    # BUILD NORMAL CONTEXT
    # ============================================================

    @staticmethod
    def build(
        results: List[Dict],
        max_chars: int = MAX_CONTEXT_CHARS
    ) -> str:

        if not results:
            return ""

        context_parts = []
        total_chars = 0

        selected_results = (
            results[:ContextBuilder.MAX_CHUNKS]
        )

        for index, result in enumerate(
            selected_results,
            start=1
        ):

            content = (
                result.get(
                    "content",
                    ""
                )
                or ""
            ).strip()

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
                or {}
            )

            if not content:
                continue

            source = metadata.get(
                "source",
                "Unknown source"
            )

            page = metadata.get(
                "page",
                "Unknown page"
            )

            chunk = (
                f"[SOURCE {index}]\n"
                f"Document: {source}\n"
                f"Page: {page}\n"
                f"Content:\n"
                f"{content}\n"
                f"[/SOURCE {index}]\n"
            )

            chunk_length = len(chunk)

            if (
                total_chars + chunk_length
                > max_chars
            ):

                remaining = (
                    max_chars - total_chars
                )

                if remaining > 300:

                    context_parts.append(
                        chunk[:remaining]
                    )

                break

            context_parts.append(
                chunk
            )

            total_chars += chunk_length

        return "\n".join(
            context_parts
        )

    # ============================================================
    # PROGRAM LIST CONTEXT
    # ============================================================

    @staticmethod
    def build_program_list_context(
        programs
    ) -> str:

        if not programs:
            return ""

        lines = [
            "DIU PROGRAM LIST:",
            ""
        ]

        for index, program in enumerate(
            programs,
            start=1
        ):

            lines.append(
                f"{index}. {program}"
            )

        return "\n".join(lines)

    # ============================================================
    # BUILD SOURCES
    # ============================================================

    @staticmethod
    def build_sources(
        results: List[Dict]
    ) -> List[Dict]:

        sources = []

        seen = set()

        for result in results:

            metadata = (
                result.get(
                    "metadata",
                    {}
                )
                or {}
            )

            source = metadata.get(
                "source"
            )

            page = metadata.get(
                "page"
            )

            if source is None:
                continue

            # Keep source + page unique.
            key = (
                str(source),
                page
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "filename": source,
                    "page": page
                }
            )

        return sources