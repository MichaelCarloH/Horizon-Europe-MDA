from langchain_openai import OpenAIEmbeddings
from langchain.evaluation import load_evaluator
from dotenv import load_dotenv
import openai
import os

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = os.environ['OPENAI_API_KEY']

def compare_embeddings(word1: str, word2: str) -> float:
    """
    Compare the embeddings of two words and return their similarity score.
    
    Args:
        word1: First word to compare
        word2: Second word to compare
        
    Returns:
        float: Similarity score between 0 and 1
    """
    try:
        # Initialize embeddings
        embeddings = OpenAIEmbeddings()
        
        # Get embeddings for both words
        embedding1 = embeddings.embed_query(word1)
        embedding2 = embeddings.embed_query(word2)
        
        # Load evaluator
        evaluator = load_evaluator("embedding_distance")
        
        # Compare embeddings
        result = evaluator.evaluate_strings(
            prediction=word1,
            reference=word2,
            embedding=embeddings
        )
        
        return result["score"]
    except Exception as e:
        print(f"Error comparing embeddings: {str(e)}")
        raise

def main():
    """Example usage of compare_embeddings."""
    # Example words to compare
    word1 = "technology"
    word2 = "innovation"
    
    # Get similarity score
    similarity = compare_embeddings(word1, word2)
    print(f"Similarity between '{word1}' and '{word2}': {similarity}")

if __name__ == "__main__":
    main()