from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredHTMLLoader
)
from langchain.schema import Document
import os
import logging
from typing import List, Dict, Any, Optional, Union
import hashlib
from datetime import datetime
from src.config import settings
import json
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with configurable settings."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            add_start_index=True,
        )
        
        # Configure markdown header splitting
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
        
        # Load project metadata
        self.project_metadata = self._load_project_metadata()

    def _load_project_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load project metadata from project_data_v2.json."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(base_dir, 'data', 'processed', 'project_data_v2.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            # Create a dictionary with project IDs as keys for faster lookup
            return {str(p['id']): p for p in projects}
        except Exception as e:
            logger.error(f"Error loading project metadata: {str(e)}")
            return {}

    def _extract_cordis_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract CORDIS metadata based on project ID in filename."""
        try:
            filename = os.path.basename(file_path)
            match = re.search(r'CORDIS_project_(\d+)_en\.pdf', filename)
            if not match:
                logger.warning(f"Not a CORDIS project file: {filename}")
                return {}
                
            project_id = match.group(1)
            if project_id in self.project_metadata:
                metadata = dict(self.project_metadata[project_id])
                metadata['source'] = filename
                logger.info(f"Found metadata for project ID: {project_id}")
                return metadata
            else:
                logger.warning(f"No metadata found for project ID: {project_id}")
                return {"source": filename, "project_id": project_id}
                
        except Exception as e:
            logger.error(f"Error extracting CORDIS metadata: {str(e)}")
            return {}

    def _generate_document_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate a unique document ID based on content and metadata."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        source = metadata.get("source", "unknown")
        return f"{source}_{content_hash}"

    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a file."""
        # Start with basic metadata
        metadata = {
            "source": os.path.basename(file_path),
            "file_type": os.path.splitext(file_path)[1].lower(),
            "processed_date": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path),
        }
        
        # If it's a CORDIS PDF, get project metadata
        if "CORDIS_project" in os.path.basename(file_path):
            cordis_metadata = self._extract_cordis_metadata(file_path)
            metadata.update(cordis_metadata)
        
        # Add PDF-specific metadata
        if file_path.endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    info = pdf_reader.metadata
                    metadata.update({
                        "title": info.get('/Title', 'Unknown Title'),
                        "author": info.get('/Author', 'Unknown Author'),
                        "creation_date": info.get('/CreationDate', 'Unknown Date'),
                        "modification_date": info.get('/ModDate', 'Unknown Date'),
                    })
            except Exception as e:
                logger.warning(f"Could not extract PDF metadata: {str(e)}")
        
        return metadata

    def _load_document(self, file_path: str) -> List[Document]:
        """Load a document based on its file type."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
            elif file_extension in ['.doc', '.docx']:
                loader = UnstructuredWordDocumentLoader(file_path)
            elif file_extension in ['.html', '.htm']:
                loader = UnstructuredHTMLLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise

    def process_document(self, document: Union[str, Document]) -> List[Document]:
        """Process a single document and return its chunks."""
        try:
            # If document is a file path, load it
            if isinstance(document, str):
                documents = self._load_document(document)
                base_metadata = self._extract_metadata(document)
            else:
                # If it's already a Document, use it directly
                documents = [document]
                base_metadata = document.metadata.copy()
            
            # Process each page/section
            processed_chunks = []
            for doc in documents:
                # Add base metadata
                doc.metadata.update(base_metadata)
                
                # Try markdown splitting first if content looks like markdown
                if doc.page_content.strip().startswith('#'):
                    try:
                        markdown_splits = self.markdown_splitter.split_text(doc.page_content)
                        for split in markdown_splits:
                            split.metadata.update(doc.metadata)
                            processed_chunks.append(split)
                    except Exception as e:
                        logger.warning(f"Markdown splitting failed, falling back to regular splitting: {str(e)}")
                        chunks = self.text_splitter.split_documents([doc])
                        processed_chunks.extend(chunks)
                else:
                    # Regular text splitting
                    chunks = self.text_splitter.split_documents([doc])
                    processed_chunks.extend(chunks)
            
            # Add document IDs and limit chunks per document
            final_chunks = []
            for chunk in processed_chunks[:settings.MAX_CHUNKS_PER_DOCUMENT]:
                chunk.metadata["document_id"] = self._generate_document_id(
                    chunk.page_content,
                    chunk.metadata
                )
                final_chunks.append(chunk)
            
            logger.info(f"Processed document into {len(final_chunks)} chunks")
            return final_chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    def process_directory(self, directory_path: str) -> List[Document]:
        """Process all supported documents in a directory."""
        supported_extensions = {'.pdf', '.txt', '.doc', '.docx', '.html', '.htm'}
        all_chunks = []
        
        try:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in supported_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            chunks = self.process_document(file_path)
                            all_chunks.extend(chunks)
                        except Exception as e:
                            logger.error(f"Failed to process {file_path}: {str(e)}")
                            continue
            
            logger.info(f"Processed directory {directory_path} into {len(all_chunks)} total chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            raise

    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Document]:
        """Process multiple documents and return their chunks."""
        try:
            processed_chunks = []
            for doc in documents:
                # Convert dict to Document if needed
                if isinstance(doc, dict):
                    content = doc.get("content", "")
                    metadata = doc.get("metadata", {})
                    doc = Document(page_content=content, metadata=metadata)
                
                # Process the document
                chunks = self.process_document(doc)
                processed_chunks.extend(chunks)
            
            logger.info(f"Processed {len(documents)} documents into {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise 