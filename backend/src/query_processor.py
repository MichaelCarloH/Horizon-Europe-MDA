import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
import os
import shutil

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate

from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions about Horizon Europe projects. Use the following context to answer the question. If you cannot find the answer in the context, say "I don't have enough information to answer that question."

Context: {context}

Question: {question}

Answer the question based on the above context. If the question is about a specific project ID, make sure to mention that ID in your response. Include relevant details like:
- Project title
- Project acronym
- Start and end dates
- Total cost
- Project objective
- Any other relevant information from the context
"""

class QueryProcessor:
    def __init__(self):
        """Initialize the query processor."""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector_store = None
        self.qa_chain = None

    def initialize_vector_store(self):
        """Initialize the Chroma vector store."""
        try:
            # If there's a dimension mismatch, delete and recreate the database
            if os.path.exists(settings.CHROMA_PATH):
                try:
                    self.vector_store = Chroma(
                        collection_name=settings.COLLECTION_NAME,
                        embedding_function=self.embeddings,
                        persist_directory=settings.CHROMA_PATH
                    )
                    # Test the embeddings to check for dimension mismatch
                    test_embedding = self.embeddings.embed_query("test")
                    if len(test_embedding) != 1536:
                        raise ValueError("Unexpected embedding dimension")
                except Exception as e:
                    logger.warning(f"Dimension mismatch detected, recreating database: {str(e)}")
                    shutil.rmtree(settings.CHROMA_PATH)
                    os.makedirs(settings.CHROMA_PATH, exist_ok=True)

            # Create new vector store
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
            
            prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0),
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
            logger.info("Successfully initialized QA chain")
            return True
        except Exception as e:
            logger.error(f"Error initializing QA chain: {str(e)}")
            raise Exception(f"Failed to initialize QA chain: {str(e)}")

    def query(self, text: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a query and return the response."""
        try:
            # Initialize vector store if needed
            if not self.vector_store:
                self.initialize_vector_store()
            
            # Search for relevant documents
            results = self.vector_store.similarity_search_with_relevance_scores(text, k=5)
            
            if not results:
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": [],
                    "timestamp": datetime.now(UTC).isoformat()
                }

            # Filter results by relevance score
            relevant_results = [(doc, score) for doc, score in results if score > 0.1]
            if not relevant_results:
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": [],
                    "timestamp": datetime.now(UTC).isoformat()
                }

            # Prepare context
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in relevant_results])
            
            # Format the prompt
            prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            formatted_prompt = prompt.format(context=context_text, question=text)
            
            # Generate response
            model = ChatOpenAI(temperature=0)
            response = model.predict(formatted_prompt)
            
            # Format sources
            sources = []
            for doc, score in relevant_results:
                source_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                }
                sources.append(source_info)
            
            logger.info(f"Successfully processed query: {text}")
            logger.info(f"Found {len(sources)} relevant documents")
            
            return {
                "answer": response,
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
            if hasattr(self, 'memory'):
                self.memory.clear()
            logger.info(f"Successfully cleared conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}", exc_info=True)
            raise

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get the conversation history for a given conversation ID."""
        try:
            if hasattr(self, 'memory'):
                history = self.memory.chat_memory.messages
                return [
                    {
                        "role": "user" if i % 2 == 0 else "assistant",
                        "content": msg.content
                    }
                    for i, msg in enumerate(history)
                ]
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
            raise 