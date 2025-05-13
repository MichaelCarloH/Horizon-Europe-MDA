import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import logging
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urljoin
import re
import os
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CORDIS_BASE_URL = "https://cordis.europa.eu"
OUTPUT_DIR = "data/xml_data"  # Directory to save XML data as text files
REPORT_SUMMARIES_PATH = "data/raw/reportSummaries.xlsx"  # Path to report summaries Excel file

class CordisXmlScraper:

    def __init__(self):
        """Initialize the XML scraper without side effects."""
        # Don't load Excel or create directories during initialization
        self.report_data = None

    def _ensure_output_dir_exists(self):
        """Create output directory only when needed."""
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            logger.info(f"Created XML data directory at {OUTPUT_DIR}")

    def _load_report_data(self) -> Dict[str, Dict[str, Any]]:
        """Load report data from Excel file with rcn and id values."""
        # If already loaded, return the cached data
        if self.report_data is not None:
            return self.report_data
            
        report_data = {}
        try:
            if os.path.exists(REPORT_SUMMARIES_PATH):
                logger.info(f"Loading report data from {REPORT_SUMMARIES_PATH}")
                df = pd.read_excel(REPORT_SUMMARIES_PATH)
                
                # Check if required columns exist
                if 'id' in df.columns and 'rcn' in df.columns:
                    # Create dictionary with project_id as key
                    for _, row in df.iterrows():
                        if pd.notna(row['id']) and pd.notna(row['rcn']):
                            # Convert to string and strip any whitespace
                            project_id = str(row['id']).strip()
                            rcn = str(row['rcn']).strip()
                            
                            report_data[project_id] = {
                                'rcn': rcn,
                                'id': project_id
                            }
                            
                            # Add any other columns that might be useful
                            for col in df.columns:
                                if col not in ['id', 'rcn'] and pd.notna(row[col]):
                                    report_data[project_id][col] = row[col]
                    
                    logger.info(f"Loaded {len(report_data)} project entries from {REPORT_SUMMARIES_PATH}")
                else:
                    logger.error(f"Required columns 'id' and 'rcn' not found in {REPORT_SUMMARIES_PATH}")
            else:
                logger.warning(f"Report summaries file not found: {REPORT_SUMMARIES_PATH}")
        except Exception as e:
            logger.error(f"Error loading report data from {REPORT_SUMMARIES_PATH}: {e}")
        
        # Cache the loaded data
        self.report_data = report_data
        return report_data

    def _get_xml_download_url(self, page_url: str) -> Optional[str]:
        """
        Finds the XML download link on a CORDIS project page.
        """
        try:
            response = requests.get(page_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            xml_link_tag = None
            
            # Try finding within a common "Download" section structure
            # Example: <h2>Download ...</h2> <ul><li><a href="?format=xml...">XML</a></li></ul>
            download_header = soup.find(['h2', 'h3'], string=re.compile(r'Download', re.IGNORECASE))
            if download_header:
                parent_container = download_header.find_parent()
                if parent_container:
                    possible_links = parent_container.find_all('a', href=True)
                    for link in possible_links:
                        link_text = link.string
                        if link_text and 'xml' in link_text.lower():
                            xml_link_tag = link
                            break
            
            # Fallback to a more general search if the above fails
            if not xml_link_tag:
                possible_links = soup.find_all('a', href=True)
                for link in possible_links:
                    link_text = link.string
                    link_title = link.get('title')
                    href = link['href']
                    
                    is_xml_text = link_text and 'xml' in link_text.lower()
                    is_xml_title = link_title and 'xml' in link_title.lower()
                    is_xml_href = 'format=xml' in href or href.lower().endswith('.xml')

                    if (is_xml_text or is_xml_title) and is_xml_href:
                        xml_link_tag = link
                        break
            
            if xml_link_tag and xml_link_tag.get('href'):
                xml_href = xml_link_tag['href']
                
                if xml_href.startswith('http://') or xml_href.startswith('https://'):
                    full_xml_url = xml_href
                elif xml_href.startswith('?'):
                    # Handles query string relative URLs like "?format=xml"
                    base_page_for_query = page_url.split('?')[0].split('#')[0]
                    full_xml_url = base_page_for_query + xml_href
                else: # Other relative paths
                    full_xml_url = urljoin(page_url, xml_href)
                
                logger.info(f"Found XML download link: {full_xml_url} on page {page_url}")
                return full_xml_url
            else:
                logger.warning(f"Could not find XML download link on page {page_url}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {page_url} to find XML link: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while finding XML link on {page_url}: {e}")
            return None

    def _fetch_and_parse_xml(self, xml_url: str) -> Optional[ET.Element]:
        """
        Fetches XML content from a URL and parses it.
        """
        xml_content = "" # Initialize for logging in case of early failure
        try:
            logger.info(f"Fetching XML from: {xml_url}")
            response = requests.get(xml_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            xml_content = response.content 
            
            root = ET.fromstring(xml_content)
            logger.info(f"Successfully fetched and parsed XML from {xml_url}")
            return root
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching XML from {xml_url}: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"Error parsing XML from {xml_url}: {e}")
            content_sample = xml_content[:500] if isinstance(xml_content, bytes) else str(xml_content)[:500]
            logger.debug(f"XML content snippet (first 500 chars/bytes): {content_sample}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during XML fetch/parse from {xml_url}: {e}")
            return None

    def _extract_text_from_element(self, element: Optional[ET.Element]) -> Optional[str]:
        if element is not None and element.text:
            return element.text.strip()
        return None

    def _find_element_robustly(self, root: ET.Element, tag_names: List[str]) -> Optional[ET.Element]:
        for tag_name_to_find in tag_names:
            # Try direct find (case-sensitive, good for no namespace or explicit namespace in tag_name_to_find)
            el = root.find(f".//{tag_name_to_find}") # Search in descendants
            if el is not None: return el
            
            # Try finding with any namespace (local-name match, case-insensitive)
            for child in root.iter():
                local_name = child.tag.split('}')[-1]
                if local_name.lower() == tag_name_to_find.lower():
                    return child
        return None

    def _extract_factsheet_data(self, root: ET.Element) -> Dict[str, Optional[str]]:
        data = {"title": None, "objective": None}
        
        title_el = self._find_element_robustly(root, ["title", "projectTitle"])
        data["title"] = self._extract_text_from_element(title_el)

        objective_el = self._find_element_robustly(root, ["objective"])
        data["objective"] = self._extract_text_from_element(objective_el)
        
        logger.info(f"Extracted Factsheet Data: {data}")
        return data

    def _extract_reporting_data(self, root: ET.Element) -> Dict[str, Optional[str]]:
        data = {"summary": None, "workPerformed": None, "finalResults": None}
        
        # Headers from user: "summary", "workPerformed", "finalResults"
        # Corresponding CORDIS page sections:
        # "Summary of the context and overall objectives"
        # "Work performed from the beginning of the project to the end of the period covered by the report and main results achieved so far"
        # "Progress beyond the state of the art and expected potential impact"
        
        # First, try to identify if this is really a reporting document 
        # by checking for reporting-specific elements or attributes
        is_reporting_document = False
        
        # Example: Check for reporting-specific parent elements
        for element in root.iter():
            tag = element.tag.split('}')[-1].lower()
            if 'report' in tag or 'periodic' in tag or 'progress' in tag:
                is_reporting_document = True
                break
        
        # Look specifically for reporting content elements
        summary_el = self._find_element_robustly(root, [
            "summary", "projectSummary", "overallObjectives", 
            "contextAndOverallObjectives"
            # Removed "teaser" as it's often part of factsheet, not reporting
        ])
        data["summary"] = self._extract_text_from_element(summary_el)
        
        work_el = self._find_element_robustly(root, [
            "workPerformed", "workPerformedSoFar", "workProgressAndMainResults",
            "workPerformedFromBegOfTheProjectToEndOfThePeriodCoveredByTheReportAndMainResultsAchievedSoFar" 
        ])
        data["workPerformed"] = self._extract_text_from_element(work_el)

        results_el = self._find_element_robustly(root, [
            "finalResults", "results", "resultsHighlights", "achievements", 
            "progressBeyondTheStateOfTheArt", "expectedImpact", "progressBeyondStateOfTheArtAndExpectedPotentialImpact"
        ])
        data["finalResults"] = self._extract_text_from_element(results_el)
        
        # Check if any of the reporting-specific fields were found
        if data["workPerformed"] or data["finalResults"] or (data["summary"] and is_reporting_document):
            logger.info(f"Extracted Reporting Data: {data}")
            return data
        
        # If we get here, we didn't find enough evidence this is a reporting document
        if not is_reporting_document:
            logger.warning("The XML document doesn't appear to be a reporting document")
        
        return {"summary": None, "workPerformed": None, "finalResults": None}

    def _save_data_to_file(self, project_id: str, data_type: str, data: Dict[str, Optional[str]]) -> str:
        """
        Save the extracted XML data to a text file.
        
        Args:
            project_id: The project ID
            data_type: Type of data ('factsheet' or 'reporting')
            data: Dictionary of extracted data
            
        Returns:
            Path to the saved file
        """
        # Ensure output directory exists before saving
        self._ensure_output_dir_exists()
        
        # Create filename
        filename = f"{project_id}_{data_type}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Write data to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Project ID: {project_id}\n")
            f.write(f"Data Type: {data_type}\n")
            f.write("=" * 50 + "\n\n")
            
            for key, value in data.items():
                if value:
                    f.write(f"## {key}\n\n")
                    f.write(f"{value}\n\n")
                    f.write("-" * 40 + "\n\n")
        
        logger.info(f"Saved {data_type} data for project {project_id} to {filepath}")
        return filepath

    def scrape_factsheet_xml(self, project_id: str) -> Dict[str, Any]:
        """
        Scrape factsheet XML data for a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            Dictionary with factsheet data and saved file paths
        """
        if not project_id:
            logger.error("Project ID is required for factsheet scraping.")
            return {"error": "Project ID is required.", "factsheet_xml_data": None}
        
        logger.info(f"Starting factsheet XML scraping for project ID: {project_id}")
        result = {"project_id": project_id, "factsheet_xml_data": None, "saved_files": []}
        
        # Ensure project ID exists in the report data (lazy load)
        # This isn't strictly necessary for factsheet, but ensures consistency
        self._load_report_data()
        
        # Construct factsheet page URL
        factsheet_page_url = f"{CORDIS_BASE_URL}/project/id/{project_id}"
        
        # Scrape Fact Sheet XML
        logger.info(f"Attempting to scrape Fact Sheet XML for project {project_id} from {factsheet_page_url}")
        factsheet_xml_download_url = self._get_xml_download_url(factsheet_page_url)
        
        if factsheet_xml_download_url:
            factsheet_xml_root = self._fetch_and_parse_xml(factsheet_xml_download_url)
            if factsheet_xml_root is not None:
                factsheet_data = self._extract_factsheet_data(factsheet_xml_root)
                result["factsheet_xml_data"] = factsheet_data
                
                # Save factsheet data to file
                if any(factsheet_data.values()):
                    file_path = self._save_data_to_file(project_id, "factsheet", factsheet_data)
                    result["saved_files"].append(file_path)
        else:
            logger.warning(f"No XML download link found for Factsheet on {factsheet_page_url}")
        
        logger.info(f"Finished factsheet XML scraping for project ID: {project_id}. Files saved: {result['saved_files']}")
        return result

    def scrape_reporting_xml(self, project_id: str) -> Dict[str, Any]:
        """
        Scrape reporting XML data for a project using rcn and id from the Excel file.
        
        Args:
            project_id: The project ID
            
        Returns:
            Dictionary with reporting data and saved file paths
        """
        if not project_id:
            logger.error("Project ID is required for reporting scraping.")
            return {"error": "Project ID is required.", "reporting_xml_data": None}
        
        logger.info(f"Starting reporting XML scraping for project ID: {project_id}")
        result = {"project_id": project_id, "reporting_xml_data": None, "saved_files": []}
        
        # Get rcn and id from the report data if available - lazy load data
        report_info = self._load_report_data().get(project_id)
        
        if report_info and 'rcn' in report_info:
            rcn = report_info['rcn']
            logger.info(f"Using rcn {rcn} from Excel file for project {project_id}")
            
            # Construct reporting page URL with rcn
            reporting_page_url = f"{CORDIS_BASE_URL}/project/rcn/{rcn}/reporting"
        else:
            # Fallback to standard URL if no rcn found
            logger.warning(f"No rcn found in Excel for project {project_id}, using standard URL format")
            reporting_page_url = f"{CORDIS_BASE_URL}/project/id/{project_id}/reporting"
        
        # Check if reporting page exists
        reporting_page_exists = False
        try:
            logger.info(f"Checking reporting page for project {project_id} at {reporting_page_url}")
            reporting_response = requests.head(reporting_page_url, timeout=10, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
            
            if not reporting_response.ok:
                logger.info(f"HEAD request to {reporting_page_url} status: {reporting_response.status_code}. Trying GET.")
                reporting_response_get = requests.get(reporting_page_url, timeout=20, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
                reporting_page_exists = reporting_response_get.ok
                
                if reporting_page_exists:
                    # Verify this is actually a reporting page, not a redirect to the main project page
                    if "reporting" not in reporting_response_get.url:
                        logger.warning(f"Request was redirected to {reporting_response_get.url}, which is not a reporting page")
                        reporting_page_exists = False
                
                if not reporting_page_exists:
                    logger.info(f"GET request to {reporting_page_url} failed with status: {reporting_response_get.status_code}")
            else:
                reporting_page_exists = True
                # Verify the final URL is actually a reporting page
                if hasattr(reporting_response, 'url') and "reporting" not in reporting_response.url:
                    logger.warning(f"Request was redirected to {reporting_response.url}, which is not a reporting page")
                    reporting_page_exists = False
                else:
                    logger.info(f"HEAD request to {reporting_page_url} successful.")
            
            if not reporting_page_exists:
                logger.info(f"No reporting page found for project {project_id}. Only creating factsheet data.")
                return result
            
            # Proceed only if we're confident a reporting page exists
            logger.info(f"Reporting page {reporting_page_url} confirmed to exist. Attempting to scrape Reporting XML.")
            reporting_xml_download_url = self._get_xml_download_url(reporting_page_url)
            
            if not reporting_xml_download_url:
                logger.warning(f"No XML download link found for Reporting on {reporting_page_url}")
                return result
            
            reporting_xml_root = self._fetch_and_parse_xml(reporting_xml_download_url)
            if not reporting_xml_root:
                logger.warning(f"Failed to parse XML content from {reporting_xml_download_url}")
                return result
            
            # Extract reporting data
            reporting_data = self._extract_reporting_data(reporting_xml_root)
            
            # Check if meaningful reporting data was extracted (at least one non-empty field)
            has_meaningful_data = any(value for value in reporting_data.values() if value)
            if not has_meaningful_data:
                logger.warning(f"No meaningful reporting data extracted for project {project_id}")
                return result
            
            result["reporting_xml_data"] = reporting_data
            
            # Save reporting data to file only if meaningful data was extracted
            file_path = self._save_data_to_file(project_id, "reporting", reporting_data)
            result["saved_files"].append(file_path)
            logger.info(f"Reporting data saved to {file_path}")
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not access reporting page {reporting_page_url} (RequestException): {e}. Skipping Reporting XML.")
        except Exception as e:
            logger.error(f"Unexpected error when checking/processing reporting page {reporting_page_url}: {e}")
        
        logger.info(f"Finished reporting XML scraping for project ID: {project_id}. Files saved: {result['saved_files']}")
        return result

    def scrape_project_data(self, project_id: str) -> Dict[str, Any]:
        """
        Scrape both factsheet and reporting XML data for a project.
        This is a convenience method that calls both specialized scraping functions.
        
        Args:
            project_id: The project ID
            
        Returns:
            Dictionary with both factsheet and reporting data and saved file paths
        """
        if not project_id:
            logger.error("Project ID is required.")
            return {"error": "Project ID is required.", "factsheet_xml_data": None, "reporting_xml_data": None}

        logger.info(f"Starting XML scraping for project ID: {project_id}")
        
        # Lazy load report data just once for both operations
        self._load_report_data()
        
        # Scrape factsheet
        factsheet_result = self.scrape_factsheet_xml(project_id)
        
        # Scrape reporting
        reporting_result = self.scrape_reporting_xml(project_id)
        
        # Combine results
        combined_result = {
            "project_id": project_id,
            "factsheet_xml_data": factsheet_result.get("factsheet_xml_data"),
            "reporting_xml_data": reporting_result.get("reporting_xml_data"),
            "saved_files": factsheet_result.get("saved_files", []) + reporting_result.get("saved_files", [])
        }
        
        logger.info(f"Finished XML scraping for project ID: {project_id}. Files saved: {combined_result['saved_files']}")
        return combined_result

if __name__ == '__main__':
    scraper = CordisXmlScraper()
    
    # Test with a project ID known to have both factsheet and reporting XMLs
    test_project_id_1 = "101072693" 
    logger.info(f"--- Scraping CORDIS XML data for project ID: {test_project_id_1} ---")
    
    # Test individual scrapers
    factsheet_result = scraper.scrape_factsheet_xml(test_project_id_1)
    print(f"\n--- Factsheet Scraping Results for Project {test_project_id_1} ---")
    print(f"Saved Files: {factsheet_result.get('saved_files', [])}")
    
    if factsheet_result.get("factsheet_xml_data"):
        print("\nFactsheet XML Data:")
        for key, value in factsheet_result["factsheet_xml_data"].items():
            print(f"  {key}: {value}")
    else:
        print("\nNo Factsheet XML data found or extracted.")
    
    reporting_result = scraper.scrape_reporting_xml(test_project_id_1)
    print(f"\n--- Reporting Scraping Results for Project {test_project_id_1} ---")
    print(f"Saved Files: {reporting_result.get('saved_files', [])}")
    
    if reporting_result.get("reporting_xml_data"):
        print("\nReporting XML Data:")
        for key, value in reporting_result["reporting_xml_data"].items():
            print(f"  {key}: {value}")
    else:
        print("\nNo Reporting XML data found, page not accessible, or data not extracted.")
    
    # Test combined scraper (backwards compatibility)
    project_info = scraper.scrape_project_data(test_project_id_1)
    print(f"\n--- Combined Scraping Results for Project {test_project_id_1} ---")
    print(f"Project ID: {project_info.get('project_id')}")
    print(f"Saved Files: {project_info.get('saved_files', [])}")
    
    # Test with a project ID that might only have factsheet XML
    test_project_id_2 = "101172406"
    logger.info(f"\n--- Scraping CORDIS XML data for project ID: {test_project_id_2} ---")
    project_info_2 = scraper.scrape_project_data(test_project_id_2)
    
    print(f"\n--- Combined Scraping Results for Project {test_project_id_2} ---")
    print(f"Project ID: {project_info_2.get('project_id')}")
    print(f"Saved Files: {project_info_2.get('saved_files', [])}") 