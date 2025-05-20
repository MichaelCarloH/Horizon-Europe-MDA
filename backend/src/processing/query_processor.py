import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
import os
import shutil

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo, StructuredQueryOutputParser

from src.config import settings
from src.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions about Horizon Europe projects. Use the following context and metadata to answer the question. If you cannot find the answer in the context, say "I don't have enough information to answer that question."

Context:
{context}

Metadata:
{metadata}

Question: {question}

Answer the question based only on the information above.
"""

# Define metadata field information (add all fields from your project_data_v2.json)
METADATA_FIELD_INFO = [
    AttributeInfo(name="id", description="The unique project ID as assigned by the CORDIS database. Used to uniquely identify each project.", type="string"),
    AttributeInfo(name="acronym", description="The official acronym of the project, typically a short memorable code.", type="string"),
    AttributeInfo(name="status", description="The current status of the project (e.g., SIGNED, ONGOING, COMPLETED).", type="string"),
    AttributeInfo(name="title", description="The full title of the project, describing its main focus.", type="string"),
    AttributeInfo(name="totalCost", description="The total cost of the project in euros, as a int.", type="int"),
    AttributeInfo(name="ecMaxContribution", description="The maximum contribution from the European Commission in euros, as a int.", type="int"),
    AttributeInfo(name="legalBasis", description="The legal basis or funding program under which the project is funded.", type="string"),
    AttributeInfo(name="topic", description="The main research topic(s) or keywords associated with the project.", type="string"),
    AttributeInfo(name="coordinatorName", description="The name of the main coordinating institution or organization.", type="string"),
    AttributeInfo(name="coordinatorID", description="The unique identifier for the coordinating institution.", type="string"),
    AttributeInfo(name="street", description="The street address of the coordinator institution.", type="string"),
    AttributeInfo(name="postCode", description="The postal code of the coordinator institution.", type="string"),
    AttributeInfo(name="city", description="The city where the coordinator institution is located.", type="string"),
    AttributeInfo(name="country", description="The country code (e.g., BE, FR) of the coordinator institution.", type="string"),
    AttributeInfo(name="geolocation", description="The latitude and longitude of the coordinator institution as a string.", type="string"),
    AttributeInfo(name="participants", description="A comma-separated list of all participating institutions in the project.", type="string"),
    AttributeInfo(name="startYear", description="The year the project started (e.g., 2023).", type="string"),
    AttributeInfo(name="startMonth", description="The month (1-12) the project started.", type="string"),
    AttributeInfo(name="startDay", description="The day (1-31) the project started.", type="string"),
    AttributeInfo(name="endYear", description="The year the project ended or is expected to end.", type="string"),
    AttributeInfo(name="endMonth", description="The month (1-12) the project ended or is expected to end.", type="string"),
    AttributeInfo(name="endDay", description="The day (1-31) the project ended or is expected to end.", type="string"),
]

DOCUMENT_CONTENT_DESCRIPTION = (
    "This document contains information about Horizon Europe research projects. "
    "Each document includes project details such as title, acronym, status, total cost, EC max contribution, legal basis, "
    "main research topic, coordinator and participants, and project timeline (startYear, startMonth, startDay, endYear, endMonth, endDay). "
    "All metadata fields are available for filtering and retrieval. "

)


class QueryProcessor:
    def __init__(self):
        """Initialize the query processor with self-querying capability."""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector_store = None
        self.self_query_retriever = None
        self.llm = ChatOpenAI(temperature=0)

    def initialize_vector_store(self):
        """Initialize the Chroma vector store."""
        try:
            # Handle dimension mismatch by recreating the database if needed
            if os.path.exists(settings.CHROMA_PATH):
                try:
                    self.vector_store = Chroma(
                        collection_name=settings.COLLECTION_NAME,
                        embedding_function=self.embeddings,
                        persist_directory=settings.CHROMA_PATH
                    )
                    test_embedding = self.embeddings.embed_query("test")
                    if len(test_embedding) != 1536:
                        raise ValueError("Unexpected embedding dimension")
                except Exception as e:
                    logger.warning(f"Dimension mismatch detected, recreating database: {str(e)}")
                    shutil.rmtree(settings.CHROMA_PATH)
                    os.makedirs(settings.CHROMA_PATH, exist_ok=True)

            self.vector_store = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PATH
            )
            logger.info("Successfully initialized vector store")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise Exception(f"Failed to initialize vector store: {str(e)}")

    def initialize_self_query_retriever(self):
        """Initialize the self-query retriever."""
        if not self.vector_store:
            self.initialize_vector_store()
        
        parser = StructuredQueryOutputParser.from_components()
        self.self_query_retriever = SelfQueryRetriever.from_llm(
            llm=self.llm,
            vectorstore=self.vector_store,
            document_contents=DOCUMENT_CONTENT_DESCRIPTION,
            metadata_field_info=METADATA_FIELD_INFO,
            structured_query_output_parser=parser,
            verbose=True
        )
        logger.info("Successfully initialized self-query retriever")

    def format_metadata(self, metadata: dict) -> str:
        """Format metadata into a readable string."""
        formatted = []
        for key, value in metadata.items():
            if value and key != "page_content":
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)

    def query(self, text: str, conversation_id: Optional[str] = None, k: int = 15) -> Dict[str, Any]:
        """Process a query using self-query retriever and return formatted results."""
        try:
            if not self.self_query_retriever:
                self.initialize_self_query_retriever()

            logger.info(f"Processing query: {text}")
            
            # Log the structured query being generated
            try:
                # Get the structured query before execution
                structured_query = self.self_query_retriever.llm_chain.run(text)
                logger.info(f"Generated structured query: {structured_query}")
            except Exception as e:
                logger.warning(f"Could not log structured query: {str(e)}")
            
            # Get documents with the structured query
            documents = self.self_query_retriever.get_relevant_documents(text)
            
            # Log the retrieved documents' metadata
            logger.info("Retrieved documents metadata:")
            for i, doc in enumerate(documents[:k]):
                logger.info(f"Document {i + 1} metadata: {doc.metadata}")

            if not documents:
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": [],
                    "timestamp": datetime.now(UTC).isoformat()
                }

            # Prepare context and metadata
            contexts = []
            all_metadata = []
            sources = []

            for doc in documents[:k]:
                contexts.append(doc.page_content)
                metadata_str = self.format_metadata(doc.metadata)
                if metadata_str:
                    all_metadata.append(metadata_str)
                
                # Prepare source information
                source_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source_info)

            # Format the prompt
            prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            formatted_prompt = prompt.format(
                context="\n\n---\n\n".join(contexts),
                metadata="\n\n---\n\n".join(all_metadata),
                question=text
            )

            # Generate response
            response = self.llm.invoke(formatted_prompt)

            logger.info(f"Successfully processed query with {len(sources)} relevant documents")
            
            return {
                "answer": response.content if hasattr(response, 'content') else str(response),
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