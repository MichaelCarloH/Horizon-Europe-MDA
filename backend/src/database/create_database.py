import os
import sys
import logging
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
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
        self.vector_store = None

    def _load_database(self) -> None:
        """Load existing Chroma database."""
        if not os.path.exists(CHROMA_PATH):
            raise FileNotFoundError("Chroma database not found")
        self.vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.embeddings,
            collection_name=settings.COLLECTION_NAME
        )

    def _save_to_chroma(self, documents: List[Document]) -> None:
        """Save documents to Chroma database."""
        try:
            logger.info(f"Saving {len(documents)} documents to Chroma database at {CHROMA_PATH}")
            
            # Filter out None values from metadata
            filtered_documents = []
            for doc in documents:
                filtered_metadata = {k: v for k, v in doc.metadata.items() if v is not None}
                filtered_doc = Document(
                    page_content=doc.page_content,
                    metadata=filtered_metadata
                )
                filtered_documents.append(filtered_doc)
            
            # If database exists, delete it
            if os.path.exists(CHROMA_PATH):
                logger.info("Found existing Chroma database, deleting it")
                shutil.rmtree(CHROMA_PATH)
            
            logger.info("Creating new Chroma database...")
            self.vector_store = Chroma.from_documents(
                documents=filtered_documents,
                embedding=self.embeddings,
                collection_name=settings.COLLECTION_NAME,
                persist_directory=CHROMA_PATH
            )
            logger.info("Successfully created new Chroma database")
            
        except Exception as e:
            logger.error(f"Error saving to Chroma: {str(e)}")
            raise Exception(f"Failed to save to Chroma: {str(e)}")

    def _add_to_database(self, documents: List[Document]) -> None:
        """Add documents to existing database."""
        try:
            if not documents:
                logger.warning("No documents to add")
                return
                
            self._load_database()
            logger.info(f"Adding {len(documents)} documents to database...")
            
            # Log details about each document
            for i, doc in enumerate(documents, 1):
                logger.info(f"Document {i}/{len(documents)}:")
                logger.info(f"  Source file: {doc.metadata.get('source', 'N/A')}")
                logger.info(f"  Page number: {doc.metadata.get('page', 'N/A')}")
                logger.info(f"  Total pages: {doc.metadata.get('total_pages', 'N/A')}")
                logger.info(f"  File type: {doc.metadata.get('file_type', 'N/A')}")
                logger.info(f"  Content preview: {doc.page_content[:100]}...")
                logger.info(f"  All metadata: {doc.metadata}")
            
            self.vector_store.add_documents(documents)
            logger.info("Successfully added documents to database")
            
        except Exception as e:
            logger.error(f"Error adding to database: {str(e)}")
            raise Exception(f"Failed to add to database: {str(e)}")

    def load_excel_files(self) -> List[Document]:
        """Load Excel files and convert each row to a document."""
        documents = []
        try:
            if not os.path.exists(EXCEL_PATH):
                raise FileNotFoundError(f"Excel directory not found: {EXCEL_PATH}")

            excel_files = [f for f in os.listdir(EXCEL_PATH) if f.endswith((".xlsx", ".xls"))]
            if not excel_files:
                raise FileNotFoundError(f"No Excel files found in {EXCEL_PATH}")

            logger.info(f"Found {len(excel_files)} Excel files: {excel_files}")
            
            for filename in excel_files:
                excel_path = os.path.join(EXCEL_PATH, filename)
                logger.info(f"Loading Excel file: {filename}")
                file_documents = import_excel_to_documents(excel_path)
                documents.extend(file_documents)
                logger.info(f"Successfully loaded {len(file_documents)} rows from {filename}")
            
            return documents
        except Exception as e:
            logger.error(f"Error loading Excel files: {str(e)}")
            raise

    def load_pdf_files(self) -> List[Document]:
        """Load PDF files and convert each page to a document."""
        documents = []
        try:
            if not os.path.exists(PDF_PATH):
                raise FileNotFoundError(f"PDF directory not found: {PDF_PATH}")

            pdf_files = [f for f in os.listdir(PDF_PATH) if f.endswith('.pdf')]
            if not pdf_files:
                raise FileNotFoundError(f"No PDF files found in {PDF_PATH}")

            logger.info(f"Found {len(pdf_files)} PDF files: {pdf_files}")
            
            for filename in pdf_files:
                pdf_path = os.path.join(PDF_PATH, filename)
                logger.info(f"Loading PDF file: {filename}")
                loader = PyPDFLoader(pdf_path)
                file_documents = loader.load()
                documents.extend(file_documents)
                logger.info(f"Successfully loaded {len(file_documents)} pages from {filename}")
            
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF files: {str(e)}")
            raise

    def load_single_file(self, file_path: str) -> List[Document]:
        """Load a single file (PDF or Excel) and return its documents."""
        try:
            file_path = os.path.abspath(file_path)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.pdf':
                logger.info(f"Loading PDF file: {file_path}")
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                
                # Get total pages
                with open(file_path, 'rb') as file:
                    pdf = PyPDF2.PdfReader(file)
                    total_pages = len(pdf.pages)
                
                # Enhance metadata for each document
                for doc in documents:
                    doc.metadata.update({
                        'file_type': 'pdf',
                        'total_pages': total_pages,
                        'filename': os.path.basename(file_path),
                        'page_number': doc.metadata.get('page', 0) + 1  # Convert to 1-based page numbers
                    })
                return documents
                
            elif file_extension in ['.xlsx', '.xls']:
                logger.info(f"Loading Excel file: {file_path}")
                documents = import_excel_to_documents(file_path)
                # Add file metadata to each document
                for doc in documents:
                    doc.metadata.update({
                        'file_type': 'excel',
                        'filename': os.path.basename(file_path)
                    })
                return documents
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            raise

    def create_database(self, include_excel: bool = True, include_pdf: bool = True) -> None:
        """Create a new database with specified file types."""
        try:
            documents = []
            if include_excel:
                documents.extend(self.load_excel_files())
            if include_pdf:
                documents.extend(self.load_pdf_files())
            
            if not documents:
                raise ValueError("No documents found to create database")
                
            self._save_to_chroma(documents)
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise

    def append_file(self, file_path: str) -> None:
        """Append a single file to the existing database."""
        try:
            documents = self.load_single_file(file_path)
            self._add_to_database(documents)
        except Exception as e:
            logger.error(f"Error appending file: {str(e)}")
            raise

def create_database(include_excel: bool = True, include_pdf: bool = True):
    """Create a new database with specified file types."""
    try:
        creator = DatabaseCreator()
        creator.create_database(include_excel, include_pdf)
        return {"status": "success", "message": "Database created successfully"}
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return {"status": "error", "message": str(e)}

def append_file(file_path: str):
    """Append a single file to the existing database."""
    try:
        creator = DatabaseCreator()
        creator.append_file(file_path)
        return {"status": "success", "message": f"File {file_path} added successfully"}
    except Exception as e:
        logger.error(f"Error appending file: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pdf-only":
            create_database(include_excel=False, include_pdf=True)
        elif sys.argv[1] == "--excel-only":
            create_database(include_excel=True, include_pdf=False)
        elif sys.argv[1] == "--append" and len(sys.argv) > 2:
            append_file(sys.argv[2])
        else:
            create_database()
    else:
        create_database()

