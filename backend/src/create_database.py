from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import shutil
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use environment variables with defaults
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
DATA_PATH = os.getenv("DATA_PATH", "data/pdf")

class DocumentProcessor:
    def __init__(self, data_path: str = DATA_PATH, chroma_path: str = CHROMA_PATH):
        self.data_path = data_path
        self.chroma_path = chroma_path
        self.documents = []
        self.chunks = []

    def create_database_pipeline(self):
        try:
            logger.info("Starting database creation pipeline...")
            self.load_documents()
            logger.info(f"Loaded {len(self.documents)} documents.")
            
            self.split_text()
            logger.info(f"Split into {len(self.chunks)} chunks.")
            
            self.save_to_chroma()
            logger.info("Database pipeline complete!")
            return self
        except Exception as e:
            logger.error(f"Error in database pipeline: {str(e)}")
            raise Exception(f"Failed to create database: {str(e)}")

    def load_documents(self):
        """
        Load all PDF files from the specified directory and extract text.
        """
        try:
            documents = []
            if not os.path.exists(self.data_path):
                logger.error(f"Directory '{self.data_path}' does not exist.")
                raise FileNotFoundError(f"Data directory not found: {self.data_path}")

            for file_name in os.listdir(self.data_path):
                if file_name.endswith(".pdf"):
                    file_path = os.path.join(self.data_path, file_name)
                    logger.info(f"Loading PDF: {file_name}")
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)

            self.documents = documents
            logger.info(f"Loaded {len(documents)} documents from {self.data_path}.")
            return self
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise Exception(f"Failed to load documents: {str(e)}")

    def get_document_count(self):
        if os.path.exists(self.chroma_path):
            # You could list files or use Chroma API to get the count of saved documents.
            print(f"Documents in Chroma: {len(os.listdir(self.chroma_path))}")
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

    def save_to_chroma(self):
        """Save documents to Chroma database."""
        try:
            logger.info("Creating new Chroma database...")
            chroma_database = Chroma.from_documents(
                documents=self.chunks,
                embedding=OpenAIEmbeddings(),
                persist_directory=None,  # Use in-memory storage
                collection_name="horizon_europe"
            )
            self.chroma_database = chroma_database
            logger.info("Successfully created Chroma database")
        except Exception as e:
            logger.error(f"Error saving to Chroma: {str(e)}")
            raise Exception(f"Failed to save to Chroma: {str(e)}")

