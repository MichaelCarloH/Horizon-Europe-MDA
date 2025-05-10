import os
from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")

def get_db_connection() -> Optional[Chroma]:
    """Get a connection to the Chroma database."""
    try:
        if not os.path.exists(CHROMA_PATH):
            return None
            
        # Initialize embeddings
        embedding_function = OpenAIEmbeddings()
        
        # Connect to existing database
        db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embedding_function
        )
        
        return db
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None 