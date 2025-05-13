import os
import argparse
import logging
import json
from typing import List, Optional
from .xml_scraper import CordisXmlScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PROJECT_DATA_PATH = "data/processed/project_data.json"  # Relative to backend directory

def load_project_ids(filepath: str = PROJECT_DATA_PATH) -> List[str]:
    """Load project IDs from the project_data.json file."""
    project_ids = []
    try:
        if os.path.exists(filepath):
            logger.info(f"Loading project IDs from {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for project_item in data:
                    if isinstance(project_item, dict) and 'id' in project_item:
                        # Convert ID to string
                        project_ids.append(str(project_item['id']))
            
            logger.info(f"Loaded {len(project_ids)} project IDs from {filepath}")
        else:
            logger.error(f"Project data file not found: {filepath}")
    except Exception as e:
        logger.error(f"Error loading project IDs from {filepath}: {e}")
    
    return project_ids

def scrape_projects(project_ids: List[str], factsheet_only: bool = False, limit: Optional[int] = None):
    """
    Scrape project data from CORDIS.
    
    Args:
        project_ids: List of project IDs to scrape
        factsheet_only: Whether to only scrape factsheet data
        limit: Maximum number of projects to scrape
    """
    if not project_ids:
        logger.error("No project IDs provided.")
        return
    
    # Apply limit if specified
    if limit and limit > 0:
        project_ids = project_ids[:limit]
        logger.info(f"Limited to {limit} projects")
    
    logger.info(f"Starting scraping for {len(project_ids)} projects")
    
    # Initialize scraper
    scraper = CordisXmlScraper()
    
    # Process each project
    for i, project_id in enumerate(project_ids):
        try:
            logger.info(f"Processing project {i+1}/{len(project_ids)}: {project_id}")
            
            # Scrape factsheet
            factsheet_result = scraper.scrape_factsheet_xml(project_id)
            
            # Print results
            if factsheet_result.get("saved_files"):
                logger.info(f"Factsheet files saved: {factsheet_result['saved_files']}")
            else:
                logger.warning(f"No factsheet data saved for project {project_id}")
            
            # Scrape reporting if not factsheet_only
            if not factsheet_only:
                reporting_result = scraper.scrape_reporting_xml(project_id)
                
                # Print results
                if reporting_result.get("saved_files"):
                    logger.info(f"Reporting files saved: {reporting_result['saved_files']}")
                else:
                    logger.info(f"No reporting data saved for project {project_id}")
        
        except Exception as e:
            logger.error(f"Error processing project {project_id}: {e}")
    
    logger.info(f"Finished scraping {len(project_ids)} projects")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Scrape data from CORDIS projects")
    parser.add_argument('--factsheet-only', action='store_true', help='Only scrape factsheet data')
    parser.add_argument('--limit', type=int, help='Limit number of projects to scrape')
    parser.add_argument('--project-id', help='Scrape a specific project ID')
    args = parser.parse_args()
    
    if args.project_id:
        # Scrape a specific project
        scrape_projects([args.project_id], factsheet_only=args.factsheet_only)
    else:
        # Scrape all projects
        project_ids = load_project_ids()
        scrape_projects(project_ids, factsheet_only=args.factsheet_only, limit=args.limit) 