from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    """Format source information from document metadata, utilizing richer data from project_data.json."""
    metadata = doc.metadata
    source_info = []

    # Core identifiers
    if metadata.get("title"):
        source_info.append(f"Title: {metadata['title']}")
    if metadata.get("project_id"):
        source_info.append(f"Project ID: {metadata['project_id']}")
    if metadata.get("acronym"):
        source_info.append(f"Acronym: {metadata.get('acronym')}")
    if metadata.get("source"):
        source_info.append(f"Source URL: {metadata['source']}")

    # Status and Dates
    if metadata.get("status"):
        source_info.append(f"Status: {metadata.get('status')}")
    if metadata.get("startDate"):
        source_info.append(f"Start Date: {metadata.get('startDate')}")
    if metadata.get("endDate"):
        source_info.append(f"End Date: {metadata.get('endDate')}")

    # Coordinator and Funding
    if metadata.get("coordinatorName"):
        source_info.append(f"Coordinator: {metadata.get('coordinatorName')}")
    elif metadata.get("coordinator"): # Fallback if coordinatorName is not present but 'coordinator' is
        source_info.append(f"Coordinator: {metadata.get('coordinator')}")
    
    if metadata.get("ecMaxContribution"):
        try:
            contribution = float(metadata["ecMaxContribution"])
            source_info.append(f"EU Max Contribution: €{contribution:,.2f}") #Formatted as Euro currency
        except ValueError:
            source_info.append(f"EU Max Contribution: {metadata["ecMaxContribution"]}") # Append as string if not a number

    # Topic and Legal Basis
    if metadata.get("topic"):
        source_info.append(f"Topic: {metadata.get('topic')}")
    if metadata.get("legalBasis"):
        source_info.append(f"Legal Basis: {metadata.get('legalBasis')}")

    # Grant Agreement ID from various potential keys
    ga_id = metadata.get("grantAgreement") or metadata.get("grantAgreementId") or metadata.get("grant_agreement_id")
    if ga_id:
        source_info.append(f"Grant Agreement ID: {ga_id}")

    # Display specific XML-derived content if available and concise
    # These might be too verbose for source summary, but can be useful.
    # Consider if these should be displayed or just used for ranking/context.
    # For example:
    # if metadata.get("xml_factsheet_objective"):
    #     source_info.append(f"Factsheet Objective: {metadata['xml_factsheet_objective'][:150]}...") # Show a snippet
    # if metadata.get("xml_reporting_summary"):
    #     source_info.append(f"Reporting Summary: {metadata['xml_reporting_summary'][:150]}...")

    # Fallbacks for older metadata fields (previously used in format_source_info)
    if metadata.get("author") and not (metadata.get("coordinatorName") or metadata.get("coordinator")):
        source_info.append(f"Author: {metadata['author']}") # If no coordinator, show author
    if metadata.get("page"):
        source_info.append(f"Page: {metadata['page']}") # Though less relevant for CORDIS data
    
    return " | ".join(info for info in source_info if info) if source_info else "Unknown source"

def query_database(query_text: str, k: int = 3, metadata_filter: Optional[Dict[str, str]] = None):
    """
    Query the Chroma vector store for similar documents based on the query text.
    Optionally filters results based on provided metadata.

    Args:
        query_text: The text to search for.
        k: The number of results to return.
        metadata_filter: A dictionary specifying metadata fields and values to filter by.
                         Example: {"author": "John Doe", "title": "Report Title"}

    Returns:
        The response text with detailed source information, or an error message.
    """
    try:
        if not os.path.exists(CHROMA_PATH):
            logger.error(f"Chroma database not found at {CHROMA_PATH}")
            return "Database not initialized. Please ensure the database has been created."

        logger.info(f"Initializing embeddings and database connection from {CHROMA_PATH}")
        embedding_function = OpenAIEmbeddings()
        db = Chroma(
            collection_name="horizon_europe",
            embedding_function=embedding_function,
            persist_directory=CHROMA_PATH
        )

        # Search the DB for relevant documents, applying metadata filter if provided
        logger.info(f"Searching database for query: {query_text} with filter: {metadata_filter}")
        results = db.similarity_search_with_relevance_scores(
            query_text, 
            k=k,
            filter=metadata_filter
        )
        logger.info(f"Found {len(results)} results after filtering")

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
        logger.error(f"Error in query_database: {str(e)}")
        raise Exception(f"Failed to process query: {str(e)}")

class QueryProcessor:
    def __init__(self):
        """Initialize the query processor."""
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.qa_chain = None

    def initialize_vector_store(self):
        """Initialize the Chroma vector store."""
        try:
            if not os.path.exists(CHROMA_PATH):
                logger.error(f"Chroma database not found at {CHROMA_PATH}")
                raise FileNotFoundError(f"Chroma database not found at {CHROMA_PATH}")

            self.vector_store = Chroma(
                collection_name="cordis_summaries",
                embedding_function=self.embeddings,
                persist_directory=CHROMA_PATH
            )
            logger.info("Successfully initialized Chroma vector store from cordis_summaries collection")
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

    def query(self, query_text: str, metadata_filter: Optional[Dict[str, str]] = None) -> str:
        """Process a query and return the response, potentially with metadata filtering."""
        try:
            if not self.qa_chain or not self.vector_store:
                self.initialize_qa_chain()
            
            # Configure retriever with filter if provided
            retriever = self.vector_store.as_retriever(
                search_kwargs={'k': 3, 'filter': metadata_filter} if metadata_filter else {'k': 3}
            )
            
            # Recreate chain with potentially filtered retriever for this query
            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0),
                chain_type="stuff",
                retriever=retriever 
            )

            response = qa_chain.invoke({"query": query_text})
            return response["result"]
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")
