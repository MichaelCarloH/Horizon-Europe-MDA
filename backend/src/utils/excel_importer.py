import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

def import_excel_to_documents(excel_path: str | Path) -> List[Document]:
    """
    Import data from an Excel file and convert it to Document objects.
    Uses 'title' + 'objective' as the main content, all other columns as metadata.
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Validate required columns
        required_columns = ['title', 'objective']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel file is missing required columns: {missing_columns}")
        
        # Convert rows to documents
        documents = []
        for _, row in df.iterrows():
            # Combine title and objective for main content
            title = str(row['title']) if not pd.isna(row['title']) else ''
            objective = str(row['objective']) if not pd.isna(row['objective']) else ''
            content = f"{title}\n{objective}".strip()
            
            # All other columns as metadata
            metadata = {}
            for col in df.columns:
                if col not in ['title', 'objective']:
                    metadata[col] = row[col] if not pd.isna(row[col]) else None
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        logger.info(f"Successfully imported {len(documents)} documents from Excel file")
        return documents
        
    except Exception as e:
        logger.error(f"Error importing Excel file: {str(e)}")
        raise

def validate_excel_structure(excel_path: str | Path) -> Dict[str, Any]:
    """
    Validate the structure of an Excel file.
    Requires 'title' and 'objective' columns.
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Check required columns
        required_columns = ['title', 'objective']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        # Check for empty rows
        empty_rows = df[df['title'].isna() | df['objective'].isna()].index.tolist()
        
        # Get basic statistics
        stats = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'missing_columns': missing_columns,
            'empty_rows': empty_rows,
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error validating Excel file: {str(e)}")
        raise 