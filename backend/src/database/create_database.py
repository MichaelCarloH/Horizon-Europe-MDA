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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- DEBUG PRINT ---
print(f"DEBUG: Loaded CORDIS_URLS from env: {os.getenv('CORDIS_URLS', 'NOT FOUND')}")
# --- END DEBUG PRINT ---

# Define paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
CORDIS_URLS = os.getenv("CORDIS_URLS", "").split(',') # Example: Get URLs from env var, comma-separated
PDF_PATH = os.getenv("PDF_PATH", "data/pdf")

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
    def __init__(self, cordis_urls: List[str] = CORDIS_URLS):
        """Initialize the database creator with the list of CORDIS URLs."""
        self.cordis_urls = [url.strip() for url in cordis_urls if url.strip()] # Clean up URLs
        if not self.cordis_urls:
            logger.warning("No CORDIS URLs provided. Check CORDIS_URLS environment variable.")

        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
        self.vector_store = None

    def scrape_cordis_reporting_page(self, url: str) -> Optional[Document]:
        """Scrape summary text and metadata from a CORDIS reporting page."""
        try:
            logger.info(f"Scraping CORDIS page: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status() # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')

            # --- Extract Metadata ---
            project_id = extract_project_id_from_url(url)
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

            # Find Grant Agreement ID - Revised Approach
            ga_id = "Unknown"
            try:
                # Search for the label more broadly first
                ga_id_label_tag = soup.find(lambda tag: tag.name in ['strong', 'b', 'span'] and "Grant agreement ID:" in tag.get_text())

                if ga_id_label_tag:
                    # Attempt 1: Check next sibling text node
                    potential_id = ga_id_label_tag.next_sibling
                    if potential_id and isinstance(potential_id, str) and potential_id.strip():
                        ga_id = potential_id.strip()
                        logger.info(f"Found Grant Agreement ID ({ga_id}) via next sibling text.")
                    else:
                        # Attempt 2: Check within the parent element's text
                        parent = ga_id_label_tag.parent
                        if parent:
                            parent_text = parent.get_text(strip=True)
                            match = re.search(r'Grant agreement ID:\s*(\S+)', parent_text)
                            if match:
                                ga_id = match.group(1)
                                logger.info(f"Found Grant Agreement ID ({ga_id}) via parent element text.")

                # If still not found, log a warning
                if ga_id == "Unknown":
                    logger.warning(f"Grant Agreement ID could not be reliably extracted from the page content for {url}. Setting to 'Unknown'.")

            except Exception as e:
                logger.warning(f"Error occurred during Grant Agreement ID extraction for {url}: {e}")
                ga_id = "Unknown" # Ensure it's unknown on error


            # Find Coordinator - Slightly more robust check
            coordinator_name = "Unknown Coordinator"
            try:
                coordinator_dt = soup.find('dt', string='Coordinated by')
                if coordinator_dt:
                    coordinator_dd = coordinator_dt.find_next_sibling('dd')
                    if coordinator_dd:
                        coordinator_name = coordinator_dd.get_text(strip=True)
            except Exception as e:
                 logger.warning(f"Error extracting Coordinator from {url}: {e}")
                
            # project_id_from_url stores the direct result of URL parsing (ID string or None)
            project_id_from_url = extract_project_id_from_url(url)

            # ga_id now holds the scraped ID or "Unknown"
            # project_id holds the ID from the URL or "Unknown"

            metadata = {
                "source": url,
                "project_id": project_id_from_url or "Unknown", # ID from URL is project_id
                "grant_agreement_id": ga_id, # Scraped ID (or "Unknown") is grant_agreement_id
                "title": title,
                "coordinator": coordinator_name,
                # Add more metadata fields as needed
            }

            # --- Detailed Logging for ID Extraction ---
            if metadata["project_id"] == "Unknown":
                logger.warning(
                    f"For URL {url}, the 'project_id' (derived from URL) in metadata is 'Unknown'. "
                    f"URL pattern '.../project/id/...' likely not matched."
                )
            else:
                 logger.info(f"For URL {url}, 'project_id' (derived from URL) set to: {metadata['project_id']}")

            if metadata["grant_agreement_id"] == "Unknown":
                logger.warning(
                    f"For URL {url}, the 'grant_agreement_id' (scraped from page) in metadata is 'Unknown'. "
                    f"It was not found in the page content."
                )
            else:
                 logger.info(f"For URL {url}, 'grant_agreement_id' (scraped from page) set to: {metadata['grant_agreement_id']}")


            # logger.info(f"Extracted metadata from {url}: {metadata}") # Combined log below is sufficient

            logger.info(f"Final extracted metadata for {url}: {metadata}")


            # --- Extract Summary Text ---
            # Refined approach: Find specific H2/H3 headers and collect text between them
            texts = []
            processed_content = False # Flag to check if specific sections were found

            # Define headers to look for (lowercase for case-insensitive comparison)
            summary_headers = [
                "summary of the context and overall objectives", # Simplified and lowercased
            ]
            work_headers = [
                "work performed", # Simplified and lowercased
                "main results achieved",
            ]
            progress_headers = [
                "progress beyond the state of the art", # Simplified and lowercased
                "expected potential impact",
            ]

            # Combine all target header keywords for easier checking
            all_target_keywords = summary_headers + work_headers + progress_headers

            all_sections_data = [] # Store tuples of (header_text, content_text)

            # Find all H2 and H3 tags which might indicate sections
            potential_headers = soup.find_all(['h2', 'h3'])

            for i, header in enumerate(potential_headers):
                header_text_lower = header.get_text(strip=True).lower()
                current_section_title = header.get_text(strip=True) # Keep original case for output
                matched_keyword = None

                # Check if this header contains any of our target keywords
                for keyword in all_target_keywords:
                    if keyword in header_text_lower:
                        matched_keyword = keyword # Found a match
                        # Refine section title based on keyword category
                        if keyword in summary_headers:
                             current_section_title = "Summary of the context and overall objectives"
                        elif keyword in work_headers:
                             current_section_title = "Work performed and main results"
                        elif keyword in progress_headers:
                             current_section_title = "Progress beyond the state of the art and expected potential impact"
                        break # Stop after first match for this header

                if matched_keyword:
                    content = []
                    # Iterate through siblings until the next h2/h3 or end of siblings
                    for sibling in header.find_next_siblings():
                        if sibling.name in ['h2', 'h3']:
                            # Stop if we hit the next potential header
                            break
                        # Collect text from relevant tags if they contain meaningful text
                        if sibling.name in ['p', 'ul', 'ol', 'div']:
                             sibling_text = sibling.get_text(separator=' ', strip=True)
                             if len(sibling_text) > 20: # Basic filter for meaningful content length
                                 content.append(sibling_text)

                    if content:
                        section_content = ' '.join(content)
                        all_sections_data.append((current_section_title, section_content))
                        processed_content = True # Mark that we found specific content

            # Format the collected texts
            if all_sections_data:
                 texts = [f"{title}:\\n{content}" for title, content in all_sections_data]
                 logger.info(f"Successfully extracted {len(all_sections_data)} specific summary section(s) from {url}")
            else:
                 logger.warning(f"Could not extract specific summary sections using headers from {url}. Trying fallback: searching for main content area.")
                 # Fallback 1: Try to find a common container ID or class if headers fail
                 # Example selectors (these might need adjustment based on CORDIS structure)
                 main_content_divs = soup.select('div#project-reporting, div.project-details, article.project, div.c-article__body') # Added common body class
                 if main_content_divs:
                      container = main_content_divs[0] # Use the first one found
                      # Find all paragraphs recursively, but filter them
                      paragraphs = container.find_all('p', recursive=True)
                      texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50] # Increased length filter
                      logger.info(f"Used fallback 1 (container div, recursive paragraphs) for text extraction from {url}. Found {len(texts)} paragraphs.")
                 else:
                      # Fallback 2: Original fallback - all paragraphs on page (use cautiously)
                      logger.warning(f"Fallback 1 failed. Using original fallback (all page paragraphs) for {url}.")
                      paragraphs = soup.find_all('p')
                      texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50] # Increased length filter

            # Combine and clean the extracted text
            page_content = "\\n\\n".join(texts)

            # --- Basic Boilerplate Removal ---
            boilerplate = [
                "This is a machine translation provided by the European Commission's eTranslation service to help you understand this page.",
                "Logging out of EU Login will log you out of any other services that use your EU Login account.",
                "Use the CORDIS log out button to remain logged in on other services.",
                # Add more common boilerplate phrases if needed
            ]
            for phrase in boilerplate:
                page_content = page_content.replace(phrase, "").strip()
            # --- End Boilerplate Removal ---


            if not page_content:
                 logger.warning(f"No meaningful text content extracted after filtering/cleaning from {url}")
                 return None # Skip if no content found


            logger.info(f"Successfully scraped text content (length: {len(page_content)}) from {url}")

            # Create a Langchain Document
            doc = Document(page_content=page_content, metadata=metadata)
            return doc

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Error scraping {url}: {str(e)}")
            return None
    def extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from project_data_v2.json file based on project ID in PDF filename."""
        try:
            # Extract project ID from filename using regex
            filename = os.path.basename(pdf_path)
            import re, json
            match = re.search(r'CORDIS_project_(\d+)_en\.pdf', filename)
            if not match:
                logger.error(f"Could not extract project ID from filename: {filename}")
                return {"source": filename}
            project_id = int(match.group(1))

            # Read project data from JSON file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(base_dir, 'data', 'processed', 'project_data_v2.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            project = next((p for p in projects if p.get('id') == project_id), None)
            if not project:
                logger.error(f"No project found with ID {project_id}")
                return {"source": filename, "project_id": str(project_id)}

            # Copy all fields from the project as metadata, plus the source filename
            metadata = dict(project)
            metadata['source'] = filename
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata for {pdf_path}: {str(e)}")
            return {"source": os.path.basename(pdf_path)}

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
            logger.error(f"Error processing {url}: {str(e)}")
            return None

    def load_data_from_urls(self) -> List[Document]:
        """Load data by scraping the list of CORDIS URLs."""
        documents = []
        if not self.cordis_urls:
            logger.error("No CORDIS URLs configured to load data from.")
            return documents # Return empty list

        logger.info(f"Loading data from {len(self.cordis_urls)} CORDIS URLs.")
        for url in self.cordis_urls:
            doc = self.scrape_cordis_reporting_page(url)
            if doc:
                documents.append(doc)

        logger.info(f"Successfully loaded {len(documents)} documents from CORDIS URLs.")
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

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            
            # Initialize embeddings
            embedding_function = OpenAIEmbeddings()
            
            # Clear existing database if it exists? (Optional - safer to create anew)
            if os.path.exists(CHROMA_PATH):
                 logger.warning(f"Existing Chroma database found at {CHROMA_PATH}. Removing it before creating a new one.")
                 try:
                      shutil.rmtree(CHROMA_PATH)
                      logger.info(f"Removed existing database at {CHROMA_PATH}")
                 except OSError as e:
                      logger.error(f"Error removing existing database {CHROMA_PATH}: {e.strerror}. Proceeding may overwrite or fail.")


            # Create new database
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embedding_function,
                collection_name="cordis_summaries", # Changed collection name
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
        """Run the complete database creation pipeline using CORDIS URLs."""
        try:
            logger.info("Starting database creation pipeline from CORDIS URLs")
            documents = self.load_data_from_urls() # New loading method
            if not documents:
                 logger.error("Failed to load any documents from CORDIS URLs. Aborting pipeline.")
                 raise ValueError("No documents loaded from CORDIS URLs.")
            chunks = self.split_documents(documents)
            if not chunks:
                 logger.error("No chunks were created from the loaded documents. Aborting pipeline.")
                 raise ValueError("No chunks created.")
            self.save_to_chroma(chunks)
            logger.info("Database creation from CORDIS URLs completed successfully")
        except Exception as e:
            logger.error(f"Error in database creation pipeline: {str(e)}")
            # Optionally re-raise or handle more gracefully
            raise # Re-raise the exception to signal failure

def create_database():
    """Create the database from CORDIS web summaries."""
    try:
        # Ensure CORDIS_URLS environment variable is set or provide a default list
        # Example: cordis_urls = ["https://cordis.europa.eu/project/id/101063162/reporting"]
        # creator = DatabaseCreator(cordis_urls=cordis_urls) # Pass URLs explicitly if not using env var
        creator = DatabaseCreator() # Uses CORDIS_URLS env var by default
        creator.run()
        return {"status": "success", "message": "Database created successfully from CORDIS summaries"}
    except Exception as e:
        logger.error(f"Error creating database from CORDIS summaries: {str(e)}")
        return {"status": "error", "message": str(e)}

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
        if sys.argv[1] == "--pdf-only":
            result = create_database(include_pdf=True, include_txt=False)
        elif sys.argv[1] == "--txt-only":
            result = create_database(include_pdf=False, include_txt=True)
        elif sys.argv[1] == "--add-txt" and len(sys.argv) > 2:
            result = add_txt_file(sys.argv[2])
        else:
            result = create_database(include_pdf=True, include_txt=True)
    else:
        result = create_database(include_pdf=True, include_txt=True)
    
    print(result)