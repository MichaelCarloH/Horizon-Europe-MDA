import logging
from src.processing.data_processor import DataProcessor
from src.vector_store.vector_store import VectorStoreManager
from src.processing.document_processor import DocumentProcessor
from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def update_vector_store():
    """
    Update the vector store with processed data.
    """
    try:
        logger.info("Starting vector store update process")
        
        # Initialize components
        data_processor = DataProcessor()
        vector_store = VectorStoreManager()
        document_processor = DocumentProcessor()
        
        # Process data and get documents
        raw_documents = data_processor.process_all_files()
        
        if not raw_documents:
            logger.warning("No documents were processed")
            return
        
        # Process documents
        documents = document_processor.process_documents(raw_documents)
        
        # Update vector store
        logger.info(f"Adding {len(documents)} documents to vector store")
        vector_store.add_documents(documents)
        
        logger.info("Vector store update completed successfully")
        
    except Exception as e:
        logger.error(f"Error updating vector store: {str(e)}", exc_info=True)
        raise

def main():
    """Main function to run the update process."""
    update_vector_store()

if __name__ == "__main__":
    main() 