from langchain_community.document_loaders import PyPDFLoader


class DocumentLoader:

    @staticmethod
    def load_pdf(pdf_path: str):

        loader = PyPDFLoader(pdf_path)

        documents = loader.load()

        cleaned_documents = []

        for document in documents:

            text = document.page_content

            # ==========================================
            # Fix common PDF encoding problems
            # ==========================================

            replacements = {
                "â¢": "•",
                "â€“": "–",
                "â€”": "—",
                "â€™": "'",
                "â€œ": '"',
                "â€": '"',
                "Â": "",
            }

            for old, new in replacements.items():
                text = text.replace(old, new)

            # ==========================================
            # Clean excessive whitespace
            # ==========================================

            lines = []

            for line in text.splitlines():

                line = " ".join(line.split())

                if line:
                    lines.append(line)

            cleaned_text = "\n".join(lines)

            document.page_content = cleaned_text

            cleaned_documents.append(document)

        return cleaned_documents