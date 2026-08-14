from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:

    @staticmethod
    def split_documents(documents):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=120,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

        chunks = splitter.split_documents(documents)

        return chunks