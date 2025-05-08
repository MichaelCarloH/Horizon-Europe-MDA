from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import logging
from dotenv import load_dotenv

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
            collection_name="horizon_europe",
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
                collection_name="horizon_europe",
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
