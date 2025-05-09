import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions
from langchain.schema import Document

from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        """Initialize the vector store manager."""
        try:
            self._initialize_vector_store()
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}", exc_info=True)
            raise

    def _initialize_vector_store(self):
        """Initialize the Chroma vector store using the new API."""
        try:
            # Use the new Chroma client API (in-memory)
            self.client = chromadb.Client()

            # Initialize OpenAI embedding function
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-ada-002"
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )

            logger.info("Successfully initialized Chroma vector store (new API)")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}", exc_info=True)
            raise

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents (List[Document]): List of documents to add
        """
        try:
            ids = [doc.metadata.get("id", str(i)) for i, doc in enumerate(documents)]
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)
            raise

    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Delete documents from the vector store.
        
        Args:
            document_ids (List[str]): List of document IDs to delete
        """
        try:
            self.collection.delete(ids=document_ids)
            logger.info(f"Successfully deleted {len(document_ids)} documents from vector store")
        except Exception as e:
            logger.error(f"Error deleting documents from vector store: {str(e)}", exc_info=True)
            raise

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query (str): Query text
            k (int): Number of results to return
            
        Returns:
            List[Document]: List of similar documents
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            documents = []
            for i in range(len(results["ids"][0])):
                doc = Document(
                    page_content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i]
                )
                documents.append(doc)
            
            logger.info(f"Successfully performed similarity search for query: {query}")
            return documents
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}", exc_info=True)
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            count = self.collection.count()
            stats = {
                "total_documents": count,
                "embedding_dimension": 1536,  # OpenAI ada-002 dimension
                "last_updated": datetime.utcnow().isoformat()
            }
            logger.info("Successfully retrieved collection statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}", exc_info=True)
            raise

    def export_metadata(self) -> Dict[str, Any]:
        """
        Export metadata from the vector store.
        
        Returns:
            Dict[str, Any]: Collection metadata
        """
        try:
            results = self.collection.get()
            metadata = {
                "documents": results["metadatas"],
                "ids": results["ids"],
                "export_time": datetime.utcnow().isoformat()
            }
            logger.info("Successfully exported collection metadata")
            return metadata
        except Exception as e:
            logger.error(f"Error exporting metadata: {str(e)}", exc_info=True)
            raise

    def get_retriever(self, search_kwargs: Optional[Dict[str, Any]] = None):
        """
        Get a retriever interface to the vector store.
        
        Args:
            search_kwargs (Optional[Dict[str, Any]]): Search parameters
            
        Returns:
            BaseRetriever: Retriever interface
        """
        try:
            from langchain_community.vectorstores import Chroma
            search_kwargs = search_kwargs or {"k": settings.MAX_RESULTS}
            vectorstore = Chroma(
                client=self.client,
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            return vectorstore.as_retriever(search_kwargs=search_kwargs)
        except Exception as e:
            logger.error(f"Error getting retriever: {str(e)}", exc_info=True)
            raise 