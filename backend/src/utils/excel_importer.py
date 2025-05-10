import pandas as pd
from pathlib import Path
from typing import List
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

def import_excel_to_documents(excel_path: str | Path) -> List[Document]:
    """Import data from an Excel file and convert it to Document objects."""
    try:
        df = pd.read_excel(excel_path)
        documents = []
        
        for index, row in df.iterrows():
            metadata = {col: str(val) if pd.notna(val) else None for col, val in row.items()}
            metadata.update({
                'source_file': str(excel_path),
                'file_type': 'excel',
                'row_index': index
            })
            
            content_parts = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
            content = "\n".join(content_parts)
            
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
            
        return documents
    except Exception as e:
        logger.error(f"Error importing Excel file: {str(e)}")
        raise 