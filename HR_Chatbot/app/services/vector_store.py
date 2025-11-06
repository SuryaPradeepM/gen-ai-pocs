import os
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

from app.services.embeddings import EmbeddingsService


class VectorStoreService:
    def __init__(self, embeddings_service: EmbeddingsService):
        self.embeddings_service = embeddings_service
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=200
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
        embeddings = [
            self.embeddings_service.get_embeddings(text) for text in text_contents
        ]

        # If vector_store exists, add to it; otherwise create new
        if self.vector_store is None:
            text_embedding_pairs = zip(text_contents, embeddings)
            self.vector_store = FAISS.from_embeddings(text_embedding_pairs, embeddings)
        else:
            # Add to existing vector store by merging
            new_store = FAISS.from_embeddings(zip(text_contents, embeddings), embeddings)
            self.vector_store.merge_from(new_store)

    def ingest_directory(self, directory_path: str):
        """Ingest all PDF files from a directory"""
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        pdf_files = list(directory.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return
        
        print(f"Found {len(pdf_files)} PDF file(s) to index")
        
        # Collect all documents from all PDFs first
        all_texts = []
        for pdf_file in pdf_files:
            print(f"Loading: {pdf_file.name}")
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
                texts = self.text_splitter.split_documents(documents)
                all_texts.extend(texts)
                print(f"Loaded {len(texts)} chunks from {pdf_file.name}")
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {str(e)}")
                raise
        
        if not all_texts:
            print("No documents found to index")
            return
        
        # Get text content from all documents
        text_contents = [text.page_content for text in all_texts]
        
        print(f"Creating embeddings for {len(text_contents)} chunks...")
        # Create embeddings for each text
        embeddings = [
            self.embeddings_service.get_embeddings(text) for text in text_contents
        ]
        
        # Create vector store from all documents
        print("Building vector store...")
        text_embedding_pairs = zip(text_contents, embeddings)
        self.vector_store = FAISS.from_embeddings(text_embedding_pairs, embeddings)
        print(f"Successfully indexed {len(pdf_files)} PDF file(s) with {len(text_contents)} total chunks")

    async def similarity_search(self, query: str, k: int = 4):
        if not self.vector_store:
            raise ValueError(
                "Vector store not initialized. Please ingest documents first."
            )

        query_embedding = self.embeddings_service.get_embeddings(query)
        results = self.vector_store.similarity_search_by_vector(query_embedding, k=k)
        return results
