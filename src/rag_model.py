import openai
from src.retrieval import ProjectRetriever
from dotenv import load_dotenv
import os
# Load OpenAI API Key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class RAGModel:
    def __init__(self):
        """Initialize the retriever and OpenAI model."""
        self.retriever = ProjectRetriever()

    def generate_summary(self, query: str):
        """Retrieve relevant documents and summarize them using OpenAI."""
        retrieved_docs = self.retriever.query(query)

        if not retrieved_docs:
            return "No relevant documents found."

        # Create a context for OpenAI
        context = "\n\n".join([doc["text"] for doc in retrieved_docs[:2]])  # Use the top 2 retrieved docs

        prompt = f"""
        Based on the following research documents:
        {context}

        Summarize the key information related to the query: "{query}"
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant summarizing research documents."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]