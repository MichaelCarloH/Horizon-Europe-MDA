import openai
import os
from retrieval import ProjectRetriever

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Store in .env or config file

class RAGModel:
    def __init__(self):
        """Initialize the retriever and LLM."""
        self.retriever = ProjectRetriever()

    def generate_response(self, query: str):
        """Retrieve relevant projects and use LLM to generate an answer."""
        retrieved_docs = self.retriever.query(query)
        
        if not retrieved_docs:
            return "No relevant projects found."

        context = "\n".join(retrieved_docs)
        prompt = f"Based on the following research projects:\n{context}\n\nAnswer the question: {query}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]

# Example Usage
if __name__ == "__main__":
    rag = RAGModel()
    print(rag.generate_response("How is AI used in agriculture?"))
