import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from PyPDF2 import PdfReader

class ProjectRetriever:
    def __init__(self, db_path: str = "data/chromadb"):
        """Initialize ChromaDB and the embedding model."""
        os.makedirs(db_path, exist_ok=True)  # Ensure the database directory exists
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(name="pdf_documents", embedding_function=self.embedding_func)

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file."""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
        return text.strip()

    def add_document(self, pdf_path: str, metadata: dict):
        """
        Add a PDF document to the database after extracting its text.

        Args:
            pdf_path (str): Path to the PDF file.
            metadata (dict): Metadata including title, author, etc.
        """
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"⚠️ No text extracted from {pdf_path}. Skipping.")
            return
        
        doc_id = metadata.get("file_name", "unknown_id")
        self.collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
        print(f"✅ Added document '{doc_id}' to ChromaDB.")

    def query(self, query_text: str, top_k: int = 3):
        """Retrieve the most relevant documents."""
        results = self.collection.query(query_texts=[query_text], n_results=top_k)
        
        if "documents" not in results:
            return []

        documents = results["documents"]
        metadata = results.get("metadatas", [])
        return [{"text": doc, "metadata": meta} for doc, meta in zip(documents, metadata)]
