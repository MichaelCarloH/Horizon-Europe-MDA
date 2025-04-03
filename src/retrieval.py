import chromadb
import os
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer

class ProjectRetriever:
    def __init__(self, db_path: str = "data/chromadb"):
        """Initialize ChromaDB and the embedding model."""
        os.makedirs(db_path, exist_ok=True)  # Ensure the database directory exists
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_func = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(name="horizon_projects", embedding_function=self.embedding_func)

    def add_documents(self, docs: list, metadata: list = None):
        """Store documents (project descriptions) in ChromaDB."""
        metadata = metadata or [{} for _ in range(len(docs))]  # Default to empty metadata
        ids = [str(i) for i in range(len(docs))]
        self.collection.add(documents=docs, metadatas=metadata, ids=ids)
        print(f"✅ Added {len(docs)} projects to ChromaDB.")

    def query(self, text: str, top_k: int = 5):
        """Retrieve similar project descriptions."""
        results = self.collection.query(query_texts=[text], n_results=top_k)
        return results["documents"][0] if "documents" in results else []

# Example Usage
if __name__ == "__main__":
    retriever = ProjectRetriever()
    
    # Example data (replace with actual Horizon Europe dataset)
    projects = [
        "AI for climate change adaptation in agriculture.",
        "Quantum computing for next-generation cybersecurity.",
        "Renewable energy storage solutions in Europe.",
    ]
    
    retriever.add_documents(docs=projects)
    print(retriever.query("climate and agriculture"))
