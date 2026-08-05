from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:

    @staticmethod
    def split_documents(documents):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        chunks = splitter.split_documents(documents)

        return chunks