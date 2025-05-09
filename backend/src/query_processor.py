import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
import os

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        """Initialize the query processor."""
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.qa_chain = None

    def initialize_vector_store(self):
        """Initialize the Chroma vector store."""
        try:
            if not os.path.exists(settings.CHROMA_PATH):
                logger.error(f"Chroma database not found at {settings.CHROMA_PATH}")
                raise FileNotFoundError(f"Chroma database not found at {settings.CHROMA_PATH}")

            self.vector_store = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PATH
            )
            logger.info("Successfully initialized Chroma vector store")
            return True
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise Exception(f"Failed to initialize vector store: {str(e)}")

    def initialize_qa_chain(self):
        """Initialize the QA chain."""
        try:
            if not self.vector_store:
                self.initialize_vector_store()
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0),
                chain_type="stuff",
                retriever=self.vector_store.as_retriever()
            )
            logger.info("Successfully initialized QA chain")
            return True
        except Exception as e:
            logger.error(f"Error initializing QA chain: {str(e)}")
            raise Exception(f"Failed to initialize QA chain: {str(e)}")

    def query(self, query_text: str) -> str:
        """Process a query and return the response."""
        try:
            if not self.qa_chain:
                self.initialize_qa_chain()
            
            response = self.qa_chain.invoke({"query": query_text})
            return response["result"]
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")

    def _get_qa_prompt(self, query: str) -> str:
        """Get the formatted prompt for the QA chain."""
        return f"""
        Answer the following question based on the provided context. 
        If you cannot find the answer in the context, say "I don't have enough information to answer that question."
        If the question is unclear or ambiguous, ask for clarification.
        
        Question: {query}
        """

    def query(self, text: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a query and return the response."""
        try:
            # Initialize chain if needed
            chain = self._initialize_chain()
            
            # Format the query
            formatted_query = self._get_qa_prompt(text)
            
            # Get response from QA chain
            result = chain({"question": formatted_query})
            
            # Format source documents
            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            logger.info(f"Successfully processed query: {text}")
            return {
                "answer": result["answer"],
                "sources": sources,
                "timestamp": datetime.now(UTC).isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear the conversation history for a given conversation ID."""
        try:
            self.memory.clear()
            logger.info(f"Successfully cleared conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}", exc_info=True)
            raise

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get the conversation history for a given conversation ID."""
        try:
            history = self.memory.chat_memory.messages
            return [
                {
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": msg.content
                }
                for i, msg in enumerate(history)
            ]
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
            raise 