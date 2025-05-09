import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from uuid import uuid4

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
            
            # Initialize embeddings with text-embedding-ada-002 (1536 dimensions)
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Create Chroma directory if it doesn't exist
            os.makedirs(settings.CHROMA_PATH, exist_ok=True)
            logger.info(f"Using Chroma directory: {settings.CHROMA_PATH}")

            # Initialize Chroma with proper configuration
            self.vector_store = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PATH,
                collection_metadata={
                    "_type": "collection",
                    "hnsw:space": "cosine",
                    "hnsw:construction_ef": 100,
                    "hnsw:search_ef": 100,
                    "hnsw:M": 16
                }
            )
            
            logger.info("VectorStoreManager initialized successfully")
        except Exception as e:
            logger.error(f"Error in VectorStoreManager initialization: {str(e)}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store with unique IDs."""
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return []

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
            )
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")

            # Generate unique IDs for each chunk
            ids = [str(uuid4()) for _ in range(len(chunks))]
            
            # Add documents with IDs
            self.vector_store.add_documents(documents=chunks, ids=ids)
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def update_documents(self, ids: List[str], documents: List[Document]) -> None:
        """Update existing documents in the vector store."""
        try:
            if len(ids) != len(documents):
                raise ValueError("Number of IDs must match number of documents")
            
            self.vector_store.update_documents(ids=ids, documents=documents)
            logger.info(f"Successfully updated {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error updating documents: {str(e)}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store."""
        try:
            self.vector_store.delete(ids=ids)
            logger.info(f"Successfully deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 3, filter: Optional[Dict] = None) -> List[Document]:
        """Perform similarity search with optional filtering."""
        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise

    def similarity_search_with_score(self, query: str, k: int = 3, filter: Optional[Dict] = None) -> List[tuple]:
        """Perform similarity search and return scores."""
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            logger.info(f"Found {len(results)} results with scores for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with score: {str(e)}")
            raise

    def get_retriever(self, search_type: str = "similarity", **kwargs):
        """Get a retriever for the vector store with specified search type."""
        try:
            return self.vector_store.as_retriever(
                search_type=search_type,
                search_kwargs=kwargs
            )
        except Exception as e:
            logger.error(f"Error creating retriever: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        try:
            collection = self.vector_store._collection
            return {
                "total_documents": collection.count(),
                "collection_name": settings.COLLECTION_NAME,
                "persist_directory": settings.CHROMA_PATH,
                "status": "initialized"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}", exc_info=True)
            return {
                "total_documents": 0,
                "collection_name": settings.COLLECTION_NAME,
                "persist_directory": settings.CHROMA_PATH,
                "status": "error",
                "error": str(e)
            }

    def query(self, query_text: str, k: int = 3):
        """
        Query the Chroma vector store for similar documents based on the query text.
        Returns the response text with detailed source information.
        """
        try:
            if not self.vector_store:
                self.save_to_chroma([])

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

    def export_metadata(self) -> List[Dict[str, Any]]:
        """Export metadata for all documents."""
        try:
            collection = self.vector_store._collection
            return collection.get()["metadatas"]
            
        except Exception as e:
            logger.error(f"Error exporting metadata: {str(e)}", exc_info=True)
            raise 