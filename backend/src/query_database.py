from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Use environment variable with default
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def query_database(query_text: str, k: int = 3):
    """
    Query the Chroma vector store for similar documents based on the query text.
    Returns the response text.
    """
    try:
        logger.info(f"Initializing embeddings and database connection...")
        embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

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

        # Retrieve sources for the response
        sources = [doc.metadata.get("source", None) for doc, _score in results]
        logger.info(f"Response generated with {len(sources)} sources")
        
        # Return the formatted response with sources
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        return formatted_response

    except Exception as e:
        logger.error(f"Error in query_database: {str(e)}")
        raise Exception(f"Failed to process query: {str(e)}")

class QueryProcessor:
    def __init__(self):
        """Initialize the query processor."""
        self.chroma_database = Chroma(
            collection_name="horizon_europe",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=None  # Use in-memory storage
        )
