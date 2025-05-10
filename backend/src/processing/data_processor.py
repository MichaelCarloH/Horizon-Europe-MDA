import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from src.utils.logging_config import setup_logging
from src.utils.directory_manager import DirectoryManager
from src.utils.excel_importer import import_excel_to_documents

logger = setup_logging()

class DataProcessor:
    def __init__(self, data_dir: str = None):
        """
        Initialize the data processor.
        
        Args:
            data_dir: Path to the data directory. If None, uses default location.
        """
        self.dir_manager = DirectoryManager(data_dir)
        self.dir_manager.create_directories(["data/raw", "data/processed"])
        
    def process_excel_file(self, file_path: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Process an Excel file and convert it to a list of documents.
        Each row becomes a document with all columns as metadata.
        
        Args:
            file_path: Path to the Excel file
            limit: Maximum number of entries to process (None for all)
            
        Returns:
            List of dictionaries containing processed data
        """
        try:
            # Import Excel file to documents
            documents = import_excel_to_documents(file_path)
            
            # Apply limit if specified
            if limit is not None:
                documents = documents[:limit]
            
            # Convert documents to dictionaries
            processed_docs = []
            for doc in documents:
                processed_doc = {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                processed_docs.append(processed_doc)
            
            logger.info(f"Processed {len(processed_docs)} entries from {file_path}")
            return processed_docs
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise
            
    def process_all_files(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Process all Excel files in the raw directory.
        
        Args:
            limit: Maximum number of entries to process per file (None for all)
            
        Returns:
            List of all processed documents
        """
        all_documents = []
        
        # Process each Excel file
        for file_path in self.dir_manager.raw_data_dir.glob("*.xlsx"):
            try:
                documents = self.process_excel_file(file_path, limit)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                continue
                    
        logger.info(f"Processed total of {len(all_documents)} documents")
        return all_documents
        
    def save_processed_data(self, documents: List[Dict[str, Any]], output_file: str = "processed_data.json"):
        """
        Save processed data to a JSON file.
        
        Args:
            documents: List of processed documents
            output_file: Name of the output file
        """
        import json
        
        output_path = self.dir_manager.processed_data_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved processed data to {output_path}")

def main():
    # Initialize processor
    processor = DataProcessor()
    
    # Process all files
    documents = processor.process_all_files()
    
    # Save processed data
    processor.save_processed_data(documents)
    
if __name__ == "__main__":
    main() 