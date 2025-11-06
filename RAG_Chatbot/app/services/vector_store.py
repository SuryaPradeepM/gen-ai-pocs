from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.embeddings import EmbeddingsService
import os

class VectorStoreService:
    def __init__(self, embeddings_service: EmbeddingsService):
        self.embeddings_service = embeddings_service
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vector_store = None

    def ingest_pdf(self, pdf_path: str):
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents
        texts = self.text_splitter.split_documents(documents)
        
        # Get text content from documents
        text_contents = [text.page_content for text in texts]
        
        # Create embeddings for each text
        embeddings = [self.embeddings_service.get_embeddings(text) 
                     for text in text_contents]

        text_embedding_pairs = zip(text_contents, embeddings)
        self.vector_store = FAISS.from_embeddings(text_embedding_pairs, embeddings)

    async def similarity_search(self, query: str, k: int = 4):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Please ingest documents first.")

        query_embedding = self.embeddings_service.get_embeddings(query)
        results = self.vector_store.similarity_search_by_vector(query_embedding, k=k)
        return results
