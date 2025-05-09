import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from .utils.logging_config import setup_logging
from .utils.directory_manager import DirectoryManager

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
        
    def process_excel_file(self, file_path: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Process an Excel file and convert it to a list of documents.
        
        Args:
            file_path: Path to the Excel file
            limit: Maximum number of entries to process
            
        Returns:
            List of dictionaries containing processed data
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Get file name without extension
            file_name = file_path.stem
            
            # Process each row
            documents = []
            for _, row in df.head(limit).iterrows():
                # Convert row to dictionary
                doc = row.to_dict()
                
                # Add metadata
                doc['source_file'] = file_name
                doc['processed_date'] = datetime.now().isoformat()
                doc['document_type'] = 'excel_data'
                
                # Create content from all fields
                content = []
                for key, value in doc.items():
                    if key not in ['source_file', 'processed_date', 'document_type']:
                        if pd.notna(value):  # Skip NaN values
                            content.append(f"{key}: {value}")
                
                doc['content'] = "\n".join(content)
                documents.append(doc)
                
            logger.info(f"Processed {len(documents)} entries from {file_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise
            
    def process_all_files(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Process all Excel files in the raw directory.
        
        Args:
            limit: Maximum number of entries to process per file
            
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
    
    # Process all files with 5 entries each
    documents = processor.process_all_files(limit=5)
    
    # Save processed data
    processor.save_processed_data(documents)
    
if __name__ == "__main__":
    main() 