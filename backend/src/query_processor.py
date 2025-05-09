import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_community.cache import InMemoryCache
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from src.vector_store import VectorStoreManager
from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        """Initialize the QueryProcessor with vector store and QA chain."""
        try:
            self.vector_store = VectorStoreManager()
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            self.qa_chain = self._initialize_chain()
            
            # Initialize cache if enabled
            if settings.ENABLE_CACHE:
                self.cache = {}
                self.cache_ttl = settings.CACHE_TTL
            else:
                self.cache = None
                
        except Exception as e:
            logger.error(f"Error initializing QueryProcessor: {str(e)}", exc_info=True)
            raise

    def _initialize_chain(self) -> ConversationalRetrievalChain:
        """Initialize the conversational retrieval chain."""
        try:
            # Initialize language model
            llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Create retrieval chain
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vector_store.get_retriever(),
                memory=self.memory,
                return_source_documents=True
            )
            
            return chain
            
        except Exception as e:
            logger.error(f"Error initializing chain: {str(e)}", exc_info=True)
            raise

    def _get_qa_prompt(self, query: str) -> str:
        """Get the formatted prompt for the QA chain."""
        return f"""
        Answer the following question based on the provided context. 
        If you cannot find the answer in the context, say "I don't have enough information to answer that question."
        
        Question: {query}
        """

    def query(self, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a query and return the response with source information.
        
        Args:
            query (str): The user's query
            conversation_id (Optional[str]): The ID of the conversation for context
            
        Returns:
            Dict[str, Any]: Response containing answer and source information
        """
        try:
            # Check cache first if enabled
            if self.cache is not None:
                cache_key = f"{conversation_id}:{query}" if conversation_id else query
                if cache_key in self.cache:
                    logger.info(f"Cache hit for query: {query}")
                    return self.cache[cache_key]

            # Format prompt
            formatted_query = self._get_qa_prompt(query)
            
            # Get response from chain
            response = self.qa_chain({"question": formatted_query})
            
            # Format source information
            sources = []
            if response.get("source_documents"):
                for doc in response["source_documents"]:
                    source = {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity": doc.metadata.get("similarity", None)
                    }
                    sources.append(source)
            
            # Format response with sources
            answer = response["answer"]
            if sources:
                answer += "\n\nSources:\n"
                for i, source in enumerate(sources, 1):
                    answer += f"{i}. {source['content']}\n"
            
            # Prepare response
            result = {
                "response": answer,
                "sources": sources,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache response if enabled
            if self.cache is not None:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear the conversation history for a given conversation ID."""
        try:
            if conversation_id in self.memory.chat_memory:
                self.memory.chat_memory.pop(conversation_id)
                logger.info(f"Cleared conversation history for ID: {conversation_id}")
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}", exc_info=True)
            raise

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get the conversation history for a given conversation ID."""
        try:
            if conversation_id in self.memory.chat_memory:
                return self.memory.chat_memory[conversation_id]
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
            raise 