from langchain.vectorstores import FAISS

class FAISS:
    def __init__(self, index: faiss.Index, embeddings: Embeddings, metadata: List[Dict[str, Any]]):
        self.index = index
        self.embeddings = embeddings
        self.metadata = metadata

    @classmethod
    def from_documents(cls, documents: List[Document], embeddings: Embeddings) -> "FAISS":
        """
        Creates a FAISS index from a list of documents.
        """
        embeddings_list = []
        metadata = []
        for document in documents:
            embedding = embeddings.embed(document)
            embeddings_list.append(embedding)
            metadata.append(document.metadata)
        embeddings_list = np.array(embeddings_list)
        index = faiss.IndexFlatIP(embeddings_list.shape[1])
        index.add(embeddings_list)
        return cls(index, embeddings, metadata)

    def similarity_search(self, query: str, k: int = 10) -> List[Document]:
        """
        Returns the k most similar documents to the query.
        """
        query_embedding = self.embeddings.embed(query)
        _, indices = self.index.search(np.array([query_embedding]), k)
        return [Document(self.metadata[index], "") for index in indices[0]]

    def similarity_search_documents(self, documents: List[Document], k: int = 10) -> List[List[Document]]:
        """
        Returns the k most similar documents to each document in the list.
        """
        return [self.similarity_search(document.page_content, k) for document in documents]

    def similarity_search_document(self, document: Document, k: int = 10) -> List[Document]:
        """
        Returns the k most similar documents to the document.
        """
        return self.similarity_search(document.page_content, k)

    def similarity_search_queries(self, queries: List[str], k: int = 10) -> List[List[Document]]:
        """
        Returns the k most similar documents to each query in the list.
        """
        return [self.similarity_search(query, k) for query in queries]

    def similarity_search_query(self, query: str, k: int = 10) -> List[Document]:
        """
        Returns the k most similar documents to the query.
        """
        return self.similarity_search(query, k)

    def __str__(self):
        return f"FAISS index with {self.index.ntotal} documents."

    def __repr__(self):
        return self.__str