from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import logging
from typing import List, Dict, Any
from langchain.schema import Document
from dotenv import load_dotenv
import PyPDF2
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
PDF_PATH = os.getenv("PDF_PATH", "data/pdf")

class DatabaseCreator:
    def __init__(self, data_dir: str = PDF_PATH):
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

    def extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                info = pdf_reader.metadata
                
                metadata = {
                    "source": os.path.basename(pdf_path),
                    "title": info.get('/Title', 'Unknown Title'),
                    "author": info.get('/Author', 'Unknown Author'),
                    "creation_date": info.get('/CreationDate', 'Unknown Date'),
                    "modification_date": info.get('/ModDate', 'Unknown Date'),
                    "creator": info.get('/Creator', 'Unknown Creator'),
                    "producer": info.get('/Producer', 'Unknown Producer')
                }
                logger.info(f"Extracted metadata from {pdf_path}: {metadata}")
                return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {str(e)}")
            return {
                "source": os.path.basename(pdf_path),
                "title": "Unknown Title",
                "author": "Unknown Author"
            }

    def load_pdfs(self) -> List[Dict[str, Any]]:
        """Load PDFs from the data directory and extract their content and metadata."""
        documents = []
        try:
            if not os.path.exists(self.data_dir):
                logger.error(f"PDF directory not found: {self.data_dir}")
                raise FileNotFoundError(f"PDF directory not found: {self.data_dir}")

            pdf_files = [f for f in os.listdir(self.data_dir) if f.endswith(".pdf")]
            if not pdf_files:
                logger.error(f"No PDF files found in {self.data_dir}")
                raise FileNotFoundError(f"No PDF files found in {self.data_dir}")

            logger.info(f"Found {len(pdf_files)} PDF files: {pdf_files}")
            
            for filename in pdf_files:
                pdf_path = os.path.join(self.data_dir, filename)
                logger.info(f"Loading PDF: {filename}")
                
                # Extract metadata
                metadata = self.extract_pdf_metadata(pdf_path)
                
                # Load and process PDF content
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                
                # Add metadata to each page
                for i, page in enumerate(pages):
                    page.metadata.update(metadata)
                    page.metadata["page"] = i + 1
                    documents.append(page)
                
                logger.info(f"Successfully loaded {len(pages)} pages from {filename}")
            
            logger.info(f"Total documents loaded: {len(documents)}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDFs: {str(e)}")
            raise Exception(f"Failed to load PDFs: {str(e)}")

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks."""
        try:
            logger.info(f"Splitting {len(documents)} documents into chunks")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Log example chunk
            if chunks:
                logger.info(f"Example chunk content: {chunks[0].page_content[:200]}")
                logger.info(f"Example chunk metadata: {chunks[0].metadata}")
            
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise Exception(f"Failed to split documents: {str(e)}")

    def save_to_chroma(self, chunks: List[Dict[str, Any]]) -> None:
        """Save document chunks to Chroma database."""
        try:
            # Clear existing database if it exists
            if os.path.exists(CHROMA_PATH):
                logger.info(f"Clearing existing Chroma database at {CHROMA_PATH}")
                shutil.rmtree(CHROMA_PATH)
            
            logger.info(f"Saving {len(chunks)} chunks to Chroma database at {CHROMA_PATH}")
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name="horizon_europe",
                persist_directory=CHROMA_PATH  # Use persistent storage
            )
            logger.info("Successfully saved to Chroma database")
            
            # Verify the save
            if os.path.exists(CHROMA_PATH):
                logger.info(f"Chroma database created at {CHROMA_PATH}")
            else:
                logger.error("Chroma database was not created!")
        except Exception as e:
            logger.error(f"Error saving to Chroma: {str(e)}")
            raise Exception(f"Failed to save to Chroma: {str(e)}")

    def run(self) -> None:
        """Run the complete database creation pipeline."""
        try:
            logger.info("Starting database creation pipeline")
            documents = self.load_pdfs()
            chunks = self.split_documents(documents)
            self.save_to_chroma(chunks)
            logger.info("Database creation completed successfully")
        except Exception as e:
            logger.error(f"Error in database creation pipeline: {str(e)}")
            raise Exception(f"Failed to create database: {str(e)}")

    def get_document_count(self):
        if os.path.exists(CHROMA_PATH):
            # You could list files or use Chroma API to get the count of saved documents.
            print(f"Documents in Chroma: {len(os.listdir(CHROMA_PATH))}")
        else:
            print("❌ Chroma database not found!")

    def split_text(self):
        """
        Split the loaded documents into smaller chunks for embedding.
        """
        try:
            if not self.documents:
                logger.error("No documents loaded to split.")
                raise ValueError("No documents available for splitting")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=300,
                chunk_overlap=100,
                length_function=len,
                add_start_index=True,
            )
            self.chunks = text_splitter.split_documents(self.documents)
            logger.info(f"Split {len(self.documents)} documents into {len(self.chunks)} chunks.")

            if self.chunks:
                document = self.chunks[0]
                logger.debug(f"Example chunk content: {document.page_content[:200]}")
                logger.debug(f"Example chunk metadata: {document.metadata}")

            return self
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            raise Exception(f"Failed to split text: {str(e)}")

def create_database():
    """Create the database from PDF documents."""
    try:
        creator = DatabaseCreator()
        creator.run()
        return {"status": "success", "message": "Database created successfully"}
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return {"status": "error", "message": str(e)}

