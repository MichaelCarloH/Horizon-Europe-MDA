from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

CHROMA_PATH = "chroma"

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
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB for relevant documents
    results = db.similarity_search_with_relevance_scores(query_text, k=k)
    print(f"Query: {query_text}")
    print(f"Results: {results}")

    # Handle case where no relevant results are found
    if len(results) == 0 or results[0][1] < 0.1:
        return f"Unable to find matching results."

    # Prepare context for the prompt by combining the results
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Format the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Generate the response using OpenAI model
    model = ChatOpenAI()
    response_text = model.predict(prompt)

    # Retrieve sources for the response
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    
    # Return the formatted response with sources
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return formatted_response
