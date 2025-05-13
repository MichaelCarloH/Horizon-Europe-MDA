import requests
from bs4 import BeautifulSoup
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from dotenv import load_dotenv
import shutil
import re  # Added for extracting project ID
import json # Import json
import glob # For finding saved text files

from .xml_scraper import CordisXmlScraper, OUTPUT_DIR # Added XML Scraper and output directory

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

class DatabaseCreator:
    def __init__(self, project_data_path: str = PROJECT_DATA_PATH):
        """Initialize the database creator with project data from JSON file."""
        self.project_data_path = project_data_path
        self.cordis_urls = []
        self.project_metadata_store = {}  # Store for project_data.json

        # Load project data and initialize URLs
        self._load_project_json_data()
        self._initialize_cordis_urls()

        self.xml_scraper = CordisXmlScraper() # Initialize XML scraper
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
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            return None

    def load_data_from_urls(self) -> List[Document]:
        """
        Scrape data from CORDIS URLs and create Document objects.
        Includes processing of XML data and saved text files.
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

        # Process URLs for projects that don't have saved text files
        for url in self.cordis_urls:
            try:
                project_id = extract_project_id_from_url(url)
                
                # Skip if we've already processed this project from text files
                if project_id and project_id in processed_project_ids:
                    logger.info(f"Skipping URL scrape for project {project_id} as data was loaded from text files")
                    continue
                
                # Perform normal scraping for projects without text files
                if project_id:
                    # Get XML data first - use separate functions for factsheet and reporting
                    logger.info(f"Scraping XML data for project {project_id}")
                    
                    # 1. Scrape factsheet XML
                    factsheet_result = self.xml_scraper.scrape_factsheet_xml(project_id)
                    if factsheet_result.get("saved_files"):
                        logger.info(f"Factsheet XML data for project {project_id} was saved to files: {factsheet_result['saved_files']}")
                        
                        # Load the newly created factsheet text files
                        for file_path in factsheet_result.get("saved_files", []):
                            if os.path.exists(file_path):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Create metadata for factsheet
                                metadata = {
                                    "source": f"{CORDIS_BASE_URL}/{project_id}",
                                    "project_id": project_id,
                                    "data_type": "factsheet",
                                    "file_source": file_path
                                }
                                
                                # Add project metadata if available
                                if project_id in self.project_metadata_store:
                                    metadata.update(self.project_metadata_store[project_id])
                                
                                # Create document
                                document = Document(page_content=content, metadata=metadata)
                                documents.append(document)
                                logger.info(f"Added factsheet XML data from text file for project {project_id}")
                    
                    # 2. Scrape reporting XML (using rcn from reportSummaries.xlsx if available)
                    reporting_result = self.xml_scraper.scrape_reporting_xml(project_id)
                    if reporting_result.get("saved_files"):
                        logger.info(f"Reporting XML data for project {project_id} was saved to files: {reporting_result['saved_files']}")
                        
                        # Load the newly created reporting text files
                        for file_path in reporting_result.get("saved_files", []):
                            if os.path.exists(file_path):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Create metadata for reporting
                                metadata = {
                                    "source": f"{CORDIS_BASE_URL}/{project_id}",
                                    "project_id": project_id,
                                    "data_type": "reporting",
                                    "file_source": file_path
                                }
                                
                                # Add project metadata if available
                                if project_id in self.project_metadata_store:
                                    metadata.update(self.project_metadata_store[project_id])
                                
                                # Create document
                                document = Document(page_content=content, metadata=metadata)
                                documents.append(document)
                                logger.info(f"Added reporting XML data from text file for project {project_id}")
                    
                    # Skip web scraping if at least one type of XML data was successfully scraped
                    if factsheet_result.get("saved_files") or reporting_result.get("saved_files"):
                        continue
                    
                    # Legacy combined approach - if neither individual scrape worked, try using the legacy combined method
                    # This is a fallback and should generally not be needed
                    logger.warning(f"No XML data scraped using separate scrapers for project {project_id}. Trying legacy combined approach.")
                    xml_result = self.xml_scraper.scrape_project_data(project_id)
                    
                    # If XML scraping saved files, don't scrape page content (files will be picked up next run)
                    if xml_result.get("saved_files"):
                        logger.info(f"XML data for project {project_id} was saved to files: {xml_result['saved_files']}")
                        
                        # Load the newly created text files
                        for file_path in xml_result.get("saved_files", []):
                            if os.path.exists(file_path):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Determine data type from filename
                                filename = os.path.basename(file_path)
                                data_type = "unknown"
                                if "factsheet" in filename:
                                    data_type = "factsheet"
                                elif "reporting" in filename:
                                    data_type = "reporting"
                                
                                # Create metadata
                                metadata = {
                                    "source": f"{CORDIS_BASE_URL}/{project_id}",
                                    "project_id": project_id,
                                    "data_type": data_type,
                                    "file_source": file_path
                                }
                                
                                # Add project metadata if available
                                if project_id in self.project_metadata_store:
                                    metadata.update(self.project_metadata_store[project_id])
                                
                                # Create document
                                document = Document(page_content=content, metadata=metadata)
                                documents.append(document)
                                logger.info(f"Added newly scraped XML data from text file for project {project_id} ({data_type})")
                        
                        # Skip web scraping for this URL
                continue
            
                # Web page scraping (fallback if XML scraping didn't save files)
                logger.info(f"Scraping web page for {url}")
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
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
                         continue # Skip if no content found


                    logger.info(f"Successfully scraped text content (length: {len(page_content)}) from {url}")

                    # Create document with extracted text
                    document = Document(page_content=page_content, metadata=metadata)
                    documents.append(document)
                    
                    if project_id:
                        processed_project_ids.add(project_id)
                else:
                    logger.warning(f"Failed to retrieve {url}: Status code {response.status_code}")
            
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")

        logger.info(f"Created {len(documents)} documents from XML files and web scraping")
        return documents

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

def create_database():
    """Create the database."""
    db_creator = DatabaseCreator()
    db_creator.run()
    return True

if __name__ == "__main__":
    create_database()

