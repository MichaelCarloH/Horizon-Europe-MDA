import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import logging
from typing import List, Dict, Any
from langchain.schema import Document
from dotenv import load_dotenv
import PyPDF2
import shutil
from src.config import settings
from src.utils.excel_importer import import_excel_to_documents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
PDF_PATH = os.getenv("PDF_PATH", "data/pdf")
EXCEL_PATH = os.getenv("EXCEL_PATH", "data/raw")

class DatabaseCreator:
    def __init__(self, data_dir: str = None):
        """Initialize the database creator with the data directory."""
        self.data_dir = data_dir
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
        self.vector_store = None

    def load_excel_files(self) -> List[Document]:
        """Load Excel files and convert each row to a document."""
        documents = []
        try:
            if not os.path.exists(EXCEL_PATH):
                logger.error(f"Excel directory not found: {EXCEL_PATH}")
                raise FileNotFoundError(f"Excel directory not found: {EXCEL_PATH}")

            excel_files = [f for f in os.listdir(EXCEL_PATH) if f.endswith((".xlsx", ".xls"))]
            if not excel_files:
                logger.error(f"No Excel files found in {EXCEL_PATH}")
                raise FileNotFoundError(f"No Excel files found in {EXCEL_PATH}")

            logger.info(f"Found {len(excel_files)} Excel files: {excel_files}")
            
            for filename in excel_files:
                excel_path = os.path.join(EXCEL_PATH, filename)
                logger.info(f"Loading Excel file: {filename}")
                
                # Import Excel file to documents
                file_documents = import_excel_to_documents(excel_path)
                # Only take first 5 rows
                file_documents = file_documents[:5]
                documents.extend(file_documents)
                
                logger.info(f"Successfully loaded {len(file_documents)} rows from {filename}")
            
            logger.info(f"Total documents loaded from Excel: {len(documents)}")
            return documents
        except Exception as e:
            logger.error(f"Error loading Excel files: {str(e)}")
            raise Exception(f"Failed to load Excel files: {str(e)}")

    def save_to_chroma(self, documents: List[Document]) -> None:
        """Save documents to Chroma database."""
        try:
            logger.info(f"Saving {len(documents)} documents to Chroma database at {CHROMA_PATH}")
            
            # Filter out None values from metadata
            filtered_documents = []
            for doc in documents:
                # Create a new metadata dict without None values
                filtered_metadata = {k: v for k, v in doc.metadata.items() if v is not None}
                # Create new document with filtered metadata
                filtered_doc = Document(
                    page_content=doc.page_content,
                    metadata=filtered_metadata
                )
                filtered_documents.append(filtered_doc)
            
            # Log each document being added
            for i, doc in enumerate(filtered_documents, 1):
                logger.info(f"Processing document {i}/{len(filtered_documents)}")
                logger.info(f"Content: {doc.page_content[:100]}...")  # Show first 100 chars
                logger.info(f"Metadata keys: {list(doc.metadata.keys())}")
            
            logger.info("Initializing embeddings...")
            # Initialize embeddings
            embedding_function = OpenAIEmbeddings()
            
            # If database exists, delete it
            if os.path.exists(CHROMA_PATH):
                logger.info("Found existing Chroma database, deleting it")
                shutil.rmtree(CHROMA_PATH)
            
            logger.info("Creating new Chroma database...")
            # Create new database
            self.vector_store = Chroma.from_documents(
                documents=filtered_documents,
                embedding=embedding_function,
                collection_name=settings.COLLECTION_NAME,
                persist_directory=CHROMA_PATH
            )
            logger.info("Successfully created new Chroma database")
            
            # Verify the save
            if os.path.exists(CHROMA_PATH):
                logger.info(f"Chroma database available at {CHROMA_PATH}")
            else:
                logger.error("Chroma database was not created!")
        except Exception as e:
            logger.error(f"Error saving to Chroma: {str(e)}")
            raise Exception(f"Failed to save to Chroma: {str(e)}")

    def run(self) -> None:
        """Run the complete database creation pipeline."""
        try:
            logger.info("Starting database creation pipeline")
            
            # Load Excel files
            documents = self.load_excel_files()
            
            # Save to Chroma
            self.save_to_chroma(documents)
            
            logger.info("Database creation completed successfully")
        except Exception as e:
            logger.error(f"Error in database creation pipeline: {str(e)}")
            raise Exception(f"Failed to create database: {str(e)}")

def create_database():
    """Create the database from Excel documents."""
    try:
        creator = DatabaseCreator()
        creator.run()
        return {"status": "success", "message": "Database created successfully"}
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    create_database()

