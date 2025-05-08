from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import logging
from typing import List
from langchain.schema import Document
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseCreator:
    def __init__(self):
        """Initialize the database creator."""
        self.pdf_path = os.getenv("PDF_PATH", "data/pdf")
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
        self.vector_store = None

    def load_pdfs(self):
        """Load PDF documents from the specified directory."""
        try:
            logger.info(f"Loading PDFs from {self.pdf_path}")
            pdf_files = [f for f in os.listdir(self.pdf_path) if f.endswith('.pdf')]
            
            for pdf_file in pdf_files:
                file_path = os.path.join(self.pdf_path, pdf_file)
                logger.info(f"Loading PDF: {pdf_file}")
                loader = PyPDFLoader(file_path)
                self.documents.extend(loader.load())
            
            logger.info(f"Loaded {len(self.documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error loading PDFs: {str(e)}")
            raise Exception(f"Failed to load PDFs: {str(e)}")

    def split_documents(self):
        """Split documents into chunks."""
        try:
            logger.info("Splitting documents into chunks...")
            self.chunks = self.text_splitter.split_documents(self.documents)
            logger.info(f"Split into {len(self.chunks)} chunks")
            return True
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise Exception(f"Failed to split documents: {str(e)}")

    def save_to_chroma(self):
        """Save documents to Chroma database."""
        try:
            logger.info("Creating new Chroma database...")
            self.vector_store = Chroma.from_documents(
                documents=self.chunks,
                embedding=self.embeddings,
                persist_directory=None  # Use in-memory storage
            )
            logger.info("Successfully created Chroma database")
            return True
        except Exception as e:
            logger.error(f"Error saving to Chroma: {str(e)}")
            raise Exception(f"Failed to save to Chroma: {str(e)}")

    def create_database_pipeline(self):
        """Run the complete database creation pipeline."""
        try:
            logger.info("Starting database creation pipeline...")
            self.load_pdfs()
            self.split_documents()
            self.save_to_chroma()
            logger.info("Database creation completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error in database pipeline: {str(e)}")
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

