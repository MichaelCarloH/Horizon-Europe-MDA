import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from src.config import settings

# Load environment variables
load_dotenv()

# Define paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")

def view_database():
    """View the contents of the Chroma database."""
    try:
        # Initialize embeddings
        embedding_function = OpenAIEmbeddings()
        
        # Load the database
        db = Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=embedding_function,
            persist_directory=CHROMA_PATH
        )
        
        # Get all documents
        results = db.get()
        
        # Print each document
        print(f"\nFound {len(results['documents'])} documents in the database:\n")
        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
            print(f"Document {i}:")
            print("Content:", doc)
            print("Metadata:", metadata)
            print("Source:", metadata.get('source', 'No source'))
            print("Project ID:", metadata.get('project_id', 'No project ID'))
            print("-" * 80)
            
        # Print some statistics
        print("\nDatabase Statistics:")
        print(f"Total documents: {len(results['documents'])}")
        print(f"Total embeddings: {len(results['embeddings'])}")
        print(f"Total metadatas: {len(results['metadatas'])}")
            
    except Exception as e:
        print(f"Error viewing database: {str(e)}")

if __name__ == "__main__":
    view_database() 