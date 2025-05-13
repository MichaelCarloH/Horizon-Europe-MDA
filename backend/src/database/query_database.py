from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo, StructuredQueryOutputParser
import os
import logging
from dotenv import load_dotenv
from src.config import settings

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

# Define metadata field information (add all fields from your project_data_v2.json)
METADATA_FIELD_INFO = [
    AttributeInfo(name="id", description="The unique project ID as assigned by the CORDIS database. Used to uniquely identify each project.", type="string"),
    AttributeInfo(name="acronym", description="The official acronym of the project, typically a short memorable code.", type="string"),
    AttributeInfo(name="status", description="The current status of the project (e.g., SIGNED, ONGOING, COMPLETED).", type="string"),
    AttributeInfo(name="title", description="The full title of the project, describing its main focus.", type="string"),
    AttributeInfo(name="totalCost", description="The total cost of the project in euros, as a string.", type="string"),
    AttributeInfo(name="ecMaxContribution", description="The maximum contribution from the European Commission in euros, as a string.", type="string"),
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

def query_database(query_text: str, k: int = 3):
    """
    Query the Chroma vector store for similar documents based on the query text.
    Returns the response text with detailed source information.
    """
    try:
        if not os.path.exists(CHROMA_PATH):
            logger.error(f"Chroma database not found at {CHROMA_PATH}")
            return "Database not initialized. Please ensure the database has been created."

        logger.info(f"Initializing embeddings and database connection from {CHROMA_PATH}")
        embedding_function = OpenAIEmbeddings()
        db = Chroma(
            collection_name=settings.COLLECTION_NAME,
            embedding_function=embedding_function,
            persist_directory=CHROMA_PATH
        )

        # Search the DB for relevant documents
        logger.info(f"Searching database for query: {query_text}")
        results = db.similarity_search_with_relevance_scores(query_text, k=k)
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
        response_text = model.invoke(prompt)

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
        self.self_query_retriever = None

    def initialize_vector_store(self):
        """Initialize the Chroma vector store."""
        try:
            if not os.path.exists(CHROMA_PATH):
                logger.error(f"Chroma database not found at {CHROMA_PATH}")
                raise FileNotFoundError(f"Chroma database not found at {CHROMA_PATH}")

            self.vector_store = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=CHROMA_PATH
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

    def initialize_self_query_retriever(self):
        """Initialize the self-query retriever."""
        try:
            if not self.vector_store:
                self.initialize_vector_store()
            
            llm = ChatOpenAI(temperature=0)
            parser = StructuredQueryOutputParser.from_components()
            self.self_query_retriever = SelfQueryRetriever.from_llm(
                llm=llm,
                vectorstore=self.vector_store,
                document_contents=DOCUMENT_CONTENT_DESCRIPTION,
                metadata_field_info=METADATA_FIELD_INFO,
                structured_query_output_parser=parser,
                verbose=True
            )
            logger.info("Successfully initialized self-query retriever")
            return True
        except Exception as e:
            logger.error(f"Error initializing self-query retriever: {str(e)}")
            raise Exception(f"Failed to initialize self-query retriever: {str(e)}")

    def query(self, query_text: str, use_metadata: bool = True) -> str:
        """Process a query and return the response. Set use_metadata=True to use self-query retriever."""
        try:
            if use_metadata:
                if not self.self_query_retriever:
                    self.initialize_self_query_retriever()
                documents = self.self_query_retriever.invoke(query_text)
                if not documents:
                    return "No documents found matching the criteria."
                context_text = "\n\n---\n\n".join([doc.page_content for doc in documents])
                prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
                prompt = prompt_template.format(context=context_text, question=query_text)
                model = ChatOpenAI(temperature=0)
                response_text = model.invoke(prompt)
                # Only return the answer string, not the full object
                return response_text.content
            else:
                if not self.qa_chain:
                    self.initialize_qa_chain()
                response = self.qa_chain.invoke({"query": query_text})
                # Only return the answer string, not the full object
                return response["result"]
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")
