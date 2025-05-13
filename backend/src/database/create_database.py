import requests
from bs4 import BeautifulSoup
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os
import logging
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from dotenv import load_dotenv
import shutil
import re  # Added for extracting project ID
import json # Import json
import glob # For finding saved text files

from src.xml_scraper import CordisXmlScraper, OUTPUT_DIR # Added XML Scraper and output directory
from src.database.scraper import CordisWebScraper, extract_project_id_from_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- DEBUG PRINT ---
# print(f"DEBUG: Loaded CORDIS_URLS from env: {os.getenv('CORDIS_URLS', 'NOT FOUND')}")
# --- END DEBUG PRINT ---

# Define paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
CORDIS_URLS = os.getenv("CORDIS_URLS", "").split(',') # Example: Get URLs from env var, comma-separated
PDF_PATH = os.getenv("PDF_PATH", "data/pdf")
# CORDIS_URLS = os.getenv("CORDIS_URLS", "").split(',') # Example: Get URLs from env var, comma-separated
CORDIS_BASE_URL = "https://cordis.europa.eu/project/id"
PROJECT_DATA_PATH = "data/processed/project_data.json"  # Relative to backend directory
XML_DATA_PATH = OUTPUT_DIR  # Path where XML data text files are stored

# Helper function to extract Project ID from URL
def extract_project_id_from_url(url: str) -> Optional[str]:
    # Corrected regex: removed extra backslash before \\d
    match = re.search(r'/project/id/(\d+)', url)
    if match:
        return match.group(1)
    logger.warning(f"Could not extract project ID from URL: {url}")
    return None
TXT_PATH = os.getenv("TXT_PATH", "data/txt")

class DatabaseCreator:
    def __init__(self, project_data_path: str = PROJECT_DATA_PATH, do_scraping: bool = False):
        """
        Initialize the database creator with project data from JSON file.
        
        Args:
            project_data_path: Path to the project_data.json file
            do_scraping: Whether to run the XML scraper (default: False)
        """
        self.project_data_path = project_data_path
        self.cordis_urls = []
        self.project_metadata_store = {}  # Store for project_data.json
        self.do_scraping = do_scraping  # Flag to control scraping

        # Load project data and initialize URLs
        self._load_project_json_data()
        self._initialize_cordis_urls()

        # Initialize scrapers
        self.web_scraper = CordisWebScraper(self.project_metadata_store)

        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
        self.vector_store = None

    def _load_project_json_data(self):
        """Loads project metadata from the project_data.json file."""
        try:
            logger.info(f"Loading project metadata from {self.project_data_path}")
            with open(self.project_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list): # Assuming it's a list of project objects
                for project_item in data:
                    if isinstance(project_item, dict) and 'id' in project_item:
                        # Convert ID to string to match extract_project_id_from_url output
                        self.project_metadata_store[str(project_item['id'])] = project_item
                    else:
                        logger.warning(f"Skipping invalid project item in {self.project_data_path}: {project_item}")
            else:
                logger.error(f"Expected a list of projects in {self.project_data_path}, but got {type(data)}. Metadata store will be empty.")

            logger.info(f"Successfully loaded {len(self.project_metadata_store)} projects into metadata store.")

        except FileNotFoundError:
            logger.error(f"Project data file not found: {self.project_data_path}. Proceeding without pre-loaded metadata.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.project_data_path}: {e}. Proceeding without pre-loaded metadata.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading {self.project_data_path}: {e}. Proceeding without pre-loaded metadata.")
    
    def _initialize_cordis_urls(self):
        """Generate CORDIS URLs from the project IDs in the project_data.json file."""
        if not self.project_metadata_store:
            logger.error("No project metadata loaded. Cannot initialize CORDIS URLs.")
            return
            
        # Generate reporting URLs for each project
        for project_id in self.project_metadata_store.keys():
            reporting_url = f"{CORDIS_BASE_URL}/{project_id}/reporting"
            self.cordis_urls.append(reporting_url)
            
        logger.info(f"Initialized {len(self.cordis_urls)} CORDIS URLs from project_data.json")
        
        # Log a sample of URLs for debugging
        if self.cordis_urls:
            sample_size = min(5, len(self.cordis_urls))
            logger.info(f"Sample of {sample_size} CORDIS URLs: {self.cordis_urls[:sample_size]}")
        
        if not self.cordis_urls:
            logger.warning("No CORDIS URLs were generated from project_data.json.")

    def load_data_from_urls(self) -> List[Document]:
        """
        Load data from CORDIS URLs and create Document objects.
        Uses the web scraper to handle both XML and web page scraping.
        """
        documents = []
        processed_project_ids = set()

        # Process existing saved XML text files first
        logger.info(f"Checking for existing XML data text files in {XML_DATA_PATH}")
        xml_text_files = glob.glob(os.path.join(XML_DATA_PATH, "*.txt"))
        
        for xml_file in xml_text_files:
            try:
                # Extract project ID from filename (format: project_id_type.txt)
                filename = os.path.basename(xml_file)
                match = re.match(r"(\d+)_(factsheet|reporting)\.txt", filename)
                
                if match:
                    project_id = match.group(1)
                    data_type = match.group(2)
                    
                    # Read the file content
                    with open(xml_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create metadata
                    metadata = {
                        "source": f"{CORDIS_BASE_URL}/{project_id}",
                        "project_id": project_id,
                        "data_type": data_type,
                        "file_source": xml_file
                    }
                    
                    # Add project metadata if available
                    if project_id in self.project_metadata_store:
                        metadata.update(self.project_metadata_store[project_id])
                    
                    # Create document
                    document = Document(page_content=content, metadata=metadata)
                    documents.append(document)
                    processed_project_ids.add(project_id)
                    logger.info(f"Added XML data from text file for project {project_id} ({data_type})")
            
            except Exception as e:
                logger.error(f"Error processing XML text file {xml_file}: {e}")

        # Skip the scraping part if scraping is disabled
        if not self.do_scraping:
            logger.info("Scraping is disabled. Only loaded existing text files.")
            return documents

        # Get all project IDs that need to be scraped
        project_ids_to_scrape = []
        for url in self.cordis_urls:
            project_id = extract_project_id_from_url(url)
            if project_id and project_id not in processed_project_ids:
                project_ids_to_scrape.append(project_id)

        # Use the web scraper to scrape all remaining projects
        if project_ids_to_scrape:
            logger.info(f"Scraping {len(project_ids_to_scrape)} projects that don't have saved data")
            scraped_documents = self.web_scraper.scrape_projects(project_ids_to_scrape)
            documents.extend(scraped_documents)

        logger.info(f"Created {len(documents)} documents from XML files and web scraping")
        return documents

    def load_txt_file(self, file_path: str) -> List[Document]:
        """Load a single TXT file and return its content as a document."""
        try:
            logger.info(f"Loading TXT file: {file_path}")
            loader = TextLoader(file_path)
            document = loader.load()
            
            # Add metadata
            for doc in document:
                doc.metadata.update({
                    "source": os.path.basename(file_path),
                    "file_type": "txt",
                })
            
            logger.info(f"Successfully loaded TXT file: {file_path}")
            return document
        except Exception as e:
            logger.error(f"Error loading TXT file {file_path}: {str(e)}")
            raise

    def load_txt_files(self) -> List[Document]:
        """Load all TXT files from the TXT_PATH directory."""
        documents = []
        try:
            if not os.path.exists(TXT_PATH):
                logger.error(f"TXT directory not found: {TXT_PATH}")
                raise FileNotFoundError(f"TXT directory not found: {TXT_PATH}")

            txt_files = [f for f in os.listdir(TXT_PATH) if f.endswith(".txt")]
            if not txt_files:
                logger.warning(f"No TXT files found in {TXT_PATH}")
                return []

            logger.info(f"Found {len(txt_files)} TXT files: {txt_files}")
            
            for filename in txt_files:
                txt_path = os.path.join(TXT_PATH, filename)
                documents.extend(self.load_txt_file(txt_path))
            
            logger.info(f"Successfully loaded {len(documents)} TXT documents")
            return documents
        except Exception as e:
            logger.error(f"Error loading TXT files: {str(e)}")
            raise

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        try:
            if not documents:
                 logger.warning("No documents to split.")
                 return []
            logger.info(f"Splitting {len(documents)} documents into chunks")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Log example chunk
            if chunks:
                logger.info(f"Example chunk content: {chunks[0].page_content[:200]}...")
                logger.info(f"Example chunk metadata: {chunks[0].metadata}")
            
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise Exception(f"Failed to split documents: {str(e)}")

    def save_to_chroma(self, chunks: List[Document]) -> None:
        """Save document chunks to Chroma database."""
        try:
            if not chunks:
                 logger.warning("No chunks to save to Chroma.")
                 return
            logger.info(f"Saving {len(chunks)} chunks to Chroma database at {CHROMA_PATH}")
            
            # Clear existing database if it exists
            if os.path.exists(CHROMA_PATH):
                logger.warning(f"Existing Chroma database found at {CHROMA_PATH}. Removing it before creating a new one.")
                try:
                    shutil.rmtree(CHROMA_PATH)
                    logger.info(f"Removed existing database at {CHROMA_PATH}")
                except OSError as e:
                    logger.error(f"Error removing existing database {CHROMA_PATH}: {e.strerror}.")

            # Create new database
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name="cordis_summaries",
                persist_directory=CHROMA_PATH
            )
            logger.info("Successfully created new Chroma database with CORDIS summaries")
            
            # Verify the save
            if os.path.exists(CHROMA_PATH):
                logger.info(f"Chroma database available at {CHROMA_PATH}")
            else:
                logger.error("Chroma database was not created!")
        except Exception as e:
            logger.error(f"Error saving to Chroma: {str(e)}")
            raise Exception(f"Failed to save to Chroma: {str(e)}")

    def run(self) -> None:
        """Run the database creation process."""
        try:
            logger.info("Starting database creation")
            # Backup existing database if it exists
            if os.path.exists(CHROMA_PATH):
                logger.info(f"Backing up existing Chroma database from {CHROMA_PATH}")
                backup_folder = f"{CHROMA_PATH}_backup"
                if os.path.exists(backup_folder):
                    shutil.rmtree(backup_folder)
                shutil.copytree(CHROMA_PATH, backup_folder)
            
            # Run the pipeline
            self.documents = self.load_data_from_urls()
            self.chunks = self.split_documents(self.documents)
            self.save_to_chroma(self.chunks)
            logger.info("Database creation completed successfully")
        except Exception as e:
            logger.error(f"Error during database creation: {e}")
            raise

def create_database(do_scraping: bool = False):
    """
    Create the database.
    
    Args:
        do_scraping: Whether to scrape data from CORDIS (default: False)
    
    Returns:
        True if successful
    """
    db_creator = DatabaseCreator(do_scraping=do_scraping)
    db_creator.run()
    return True

# For backward compatibility with main.py - this is the original function
def create_database_without_scraping():
    """Create the database without scraping (for backward compatibility)."""
    return create_database(do_scraping=False)

# Preserve the original name for imports in main.py
# When main.py imports DatabaseCreator, it will still work with the default do_scraping=False
# But our new script with the command line argument will use the new functionality

def add_txt_file(file_path: str):
    """Add a single TXT file to the database."""
    try:
        creator = DatabaseCreator()
        documents = creator.load_txt_file(file_path)
        chunks = creator.split_documents(documents)
        creator.save_to_chroma(chunks)
        return {"status": "success", "message": f"TXT file {file_path} added successfully"}
    except Exception as e:
        logger.error(f"Error adding TXT file: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scrape":
            result = create_database(do_scraping=True)
        else:
            result = create_database(do_scraping=False)
    else:
        result = create_database(do_scraping=False)
    
    print(result)