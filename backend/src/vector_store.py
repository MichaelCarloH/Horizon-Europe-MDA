import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use environment variable with default
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def format_source_info(doc):
    """Format source information from document metadata."""
    metadata = doc.metadata
    source_info = []
    
    if metadata.get("source"):
        source_info.append(f"Document: {metadata['source']}")
    if metadata.get("author"):
        source_info.append(f"Author: {metadata['author']}")
    if metadata.get("page"):
        source_info.append(f"Page: {metadata['page']}")
    if metadata.get("title"):
        source_info.append(f"Title: {metadata['title']}")
    
    return " | ".join(source_info) if source_info else "Unknown source"

class VectorStoreManager:
    def __init__(self):
        """Initialize the vector store manager."""
        try:
            # Ensure we have an OpenAI API key
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
            self.vector_store = None
            
            # Initialize vector store
            self.initialize()
                
            logger.info("VectorStoreManager initialized successfully")
        except Exception as e:
            logger.error(f"Error in VectorStoreManager initialization: {str(e)}")
            self.vector_store = None

    def initialize(self):
        """Initialize the Chroma vector store."""
        try:
            # Create Chroma directory if it doesn't exist
            os.makedirs(CHROMA_PATH, exist_ok=True)
            logger.info(f"Using Chroma directory: {CHROMA_PATH}")

            # Initialize Chroma with persistence
            self.vector_store = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=settings.COLLECTION_PATH
            )
            
            # Force collection creation
            if not hasattr(self.vector_store, '_collection'):
                self.vector_store._collection = self.vector_store._client.get_or_create_collection(
                    name=settings.COLLECTION_NAME,
                    embedding_function=self.embeddings
                )
            
            logger.info("Successfully initialized Chroma vector store")
            return True
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            self.vector_store = None
            return False

    def query(self, query_text: str, k: int = 3):
        """
        Query the Chroma vector store for similar documents based on the query text.
        Returns the response text with detailed source information.
        """
        try:
            if not self.vector_store:
                self.initialize()

            # Search the DB for relevant documents
            logger.info(f"Searching database for query: {query_text}")
            results = self.vector_store.similarity_search_with_relevance_scores(query_text, k=k)
            logger.info(f"Found {len(results)} results")

            # Handle case where no relevant results are found
            if len(results) == 0 or results[0][1] < 0.1:
                logger.warning("No relevant results found")
                return "Unable to find matching results."

            # Prepare context for the prompt by combining the results
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            logger.info(f"Prepared context with {len(results)} documents")

            # Format the prompt
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, question=query_text)

            # Generate the response using OpenAI model
            logger.info("Generating response with OpenAI model...")
            model = ChatOpenAI()
            response_text = model.predict(prompt)

            # Format sources with detailed information
            sources = [format_source_info(doc) for doc, _score in results]
            logger.info(f"Response generated with {len(sources)} sources")
            
            # Return the formatted response with detailed sources
            formatted_response = f"Response: {response_text}\n\nSources:\n" + "\n".join([f"- {source}" for source in sources])
            return formatted_response

        except Exception as e:
            logger.error(f"Error in query: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")

    def add_documents(self, documents):
        """Add documents to the vector store."""
        try:
            if not self.vector_store:
                self.initialize()
            
            self.vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise Exception(f"Failed to add documents: {str(e)}")

    def get_retriever(self):
        """Get the retriever for the vector store."""
        if not self.vector_store:
            self.initialize()
        return self.vector_store.as_retriever()

    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from the vector store."""
        try:
            self.vector_store.delete(ids=document_ids)
            logger.info(f"Successfully deleted {len(document_ids)} documents")
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}", exc_info=True)
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        try:
            if not self.vector_store or not hasattr(self.vector_store, '_collection'):
                return {
                    "total_documents": 0,
                    "collection_name": settings.COLLECTION_NAME,
                    "persist_directory": settings.COLLECTION_PATH,
                    "status": "not_initialized"
                }
            
            collection = self.vector_store._collection
            return {
                "total_documents": collection.count(),
                "collection_name": settings.COLLECTION_NAME,
                "persist_directory": settings.COLLECTION_PATH,
                "status": "initialized"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}", exc_info=True)
            return {
                "total_documents": 0,
                "collection_name": settings.COLLECTION_NAME,
                "persist_directory": settings.COLLECTION_PATH,
                "status": "error",
                "error": str(e)
            }

    def export_metadata(self) -> List[Dict[str, Any]]:
        """Export metadata for all documents."""
        try:
            collection = self.vector_store._collection
            return collection.get()["metadatas"]
            
        except Exception as e:
            logger.error(f"Error exporting metadata: {str(e)}", exc_info=True)
            raise 