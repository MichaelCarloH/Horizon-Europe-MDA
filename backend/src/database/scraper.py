import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
import os
import re
from langchain.schema import Document

from ..xml_scraper import CordisXmlScraper, OUTPUT_DIR
from ..utils.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

CORDIS_BASE_URL = "https://cordis.europa.eu/project/id"

def extract_project_id_from_url(url: str) -> Optional[str]:
    """Extract Project ID from URL."""
    match = re.search(r'/project/id/(\d+)', url)
    if match:
        return match.group(1)
    logger.warning(f"Could not extract project ID from URL: {url}")
    return None

class CordisWebScraper:
    def __init__(self, project_metadata_store: Dict[str, Any] = None):
        """Initialize the CORDIS web scraper."""
        self.project_metadata_store = project_metadata_store or {}
        self.xml_scraper = CordisXmlScraper()

    def scrape_cordis_reporting_page(self, url: str) -> Optional[Document]:
        """Scrape summary text and metadata from a CORDIS reporting page."""
        try:
            logger.info(f"Scraping CORDIS page: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract Metadata
            project_id = extract_project_id_from_url(url)
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

            # Find Grant Agreement ID
            ga_id = "Unknown"
            try:
                ga_id_label_tag = soup.find(lambda tag: tag.name in ['strong', 'b', 'span'] and "Grant agreement ID:" in tag.get_text())
                if ga_id_label_tag:
                    potential_id = ga_id_label_tag.next_sibling
                    if potential_id and isinstance(potential_id, str) and potential_id.strip():
                        ga_id = potential_id.strip()
                    else:
                        parent = ga_id_label_tag.parent
                        if parent:
                            parent_text = parent.get_text(strip=True)
                            match = re.search(r'Grant agreement ID:\s*(\S+)', parent_text)
                            if match:
                                ga_id = match.group(1)
            except Exception as e:
                logger.warning(f"Error extracting Grant Agreement ID from {url}: {e}")

            # Find Coordinator
            coordinator_name = "Unknown Coordinator"
            try:
                coordinator_dt = soup.find('dt', string='Coordinated by')
                if coordinator_dt:
                    coordinator_dd = coordinator_dt.find_next_sibling('dd')
                    if coordinator_dd:
                        coordinator_name = coordinator_dd.get_text(strip=True)
            except Exception as e:
                logger.warning(f"Error extracting Coordinator from {url}: {e}")

            metadata = {
                "source": url,
                "project_id": project_id or "Unknown",
                "grant_agreement_id": ga_id,
                "title": title,
                "coordinator": coordinator_name,
            }

            # Extract Summary Text
            texts = []
            summary_headers = ["summary of the context and overall objectives"]
            work_headers = ["work performed", "main results achieved"]
            progress_headers = ["progress beyond the state of the art", "expected potential impact"]
            all_target_keywords = summary_headers + work_headers + progress_headers
            all_sections_data = []

            potential_headers = soup.find_all(['h2', 'h3'])
            for header in potential_headers:
                header_text_lower = header.get_text(strip=True).lower()
                current_section_title = header.get_text(strip=True)
                matched_keyword = None

                for keyword in all_target_keywords:
                    if keyword in header_text_lower:
                        matched_keyword = keyword
                        if keyword in summary_headers:
                            current_section_title = "Summary of the context and overall objectives"
                        elif keyword in work_headers:
                            current_section_title = "Work performed and main results"
                        elif keyword in progress_headers:
                            current_section_title = "Progress beyond the state of the art and expected potential impact"
                        break

                if matched_keyword:
                    content = []
                    for sibling in header.find_next_siblings():
                        if sibling.name in ['h2', 'h3']:
                            break
                        if sibling.name in ['p', 'ul', 'ol', 'div']:
                            sibling_text = sibling.get_text(separator=' ', strip=True)
                            if len(sibling_text) > 20:
                                content.append(sibling_text)

                    if content:
                        section_content = ' '.join(content)
                        all_sections_data.append((current_section_title, section_content))

            if all_sections_data:
                texts = [f"{title}:\n{content}" for title, content in all_sections_data]
            else:
                logger.warning(f"No specific sections found in {url}. Trying fallback methods.")
                main_content_divs = soup.select('div#project-reporting, div.project-details, article.project, div.c-article__body')
                if main_content_divs:
                    container = main_content_divs[0]
                    paragraphs = container.find_all('p', recursive=True)
                    texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
                else:
                    paragraphs = soup.find_all('p')
                    texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]

            page_content = "\n\n".join(texts)

            # Remove boilerplate text
            boilerplate = [
                "This is a machine translation provided by the European Commission's eTranslation service to help you understand this page.",
                "Logging out of EU Login will log you out of any other services that use your EU Login account.",
                "Use the CORDIS log out button to remain logged in on other services.",
            ]
            for phrase in boilerplate:
                page_content = page_content.replace(phrase, "").strip()

            if not page_content:
                logger.warning(f"No meaningful text content extracted from {url}")
                return None

            logger.info(f"Successfully scraped text content (length: {len(page_content)}) from {url}")
            return Document(page_content=page_content, metadata=metadata)

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def scrape_project(self, project_id: str) -> List[Document]:
        """Scrape all available data for a project."""
        documents = []
        
        # 1. Scrape XML data
        try:
            # Scrape factsheet XML
            factsheet_result = self.xml_scraper.scrape_factsheet_xml(project_id)
            if factsheet_result.get("saved_files"):
                for file_path in factsheet_result["saved_files"]:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        metadata = {
                            "source": f"{CORDIS_BASE_URL}/{project_id}",
                            "project_id": project_id,
                            "data_type": "factsheet",
                            "file_source": file_path
                        }
                        if project_id in self.project_metadata_store:
                            metadata.update(self.project_metadata_store[project_id])
                        documents.append(Document(page_content=content, metadata=metadata))

            # Scrape reporting XML
            reporting_result = self.xml_scraper.scrape_reporting_xml(project_id)
            if reporting_result.get("saved_files"):
                for file_path in reporting_result["saved_files"]:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        metadata = {
                            "source": f"{CORDIS_BASE_URL}/{project_id}",
                            "project_id": project_id,
                            "data_type": "reporting",
                            "file_source": file_path
                        }
                        if project_id in self.project_metadata_store:
                            metadata.update(self.project_metadata_store[project_id])
                        documents.append(Document(page_content=content, metadata=metadata))

        except Exception as e:
            logger.error(f"Error scraping XML data for project {project_id}: {e}")

        # 2. Scrape web page if no XML data was found
        if not documents:
            url = f"{CORDIS_BASE_URL}/{project_id}/reporting"
            doc = self.scrape_cordis_reporting_page(url)
            if doc:
                documents.append(doc)

        return documents

    def scrape_projects(self, project_ids: List[str]) -> List[Document]:
        """Scrape multiple projects."""
        all_documents = []
        for project_id in project_ids:
            try:
                project_docs = self.scrape_project(project_id)
                all_documents.extend(project_docs)
                logger.info(f"Successfully scraped project {project_id}")
            except Exception as e:
                logger.error(f"Error scraping project {project_id}: {e}")
                continue
        return all_documents 