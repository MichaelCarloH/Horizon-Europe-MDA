import os
import sys
import argparse
import asyncio
from src.create_database import DocumentProcessor
from src.query_database import query_database
CHROMA_PATH = "chroma"

async def main():
    
    # Step 1: Create the databasea
    #if it doesn't exist
    if not os.path.exists(CHROMA_PATH):
        print("Database not found. Creating database...")
        processor = DocumentProcessor()
        processor.create_database_pipeline()
        print("Database created successfully.")
    else:
        print("Database already exists. Skipping creation.")

    while True:
        question = input("\nEnter your question: ")
        
        # Exit condition
        if question.lower() == "exit":
            print("Exiting...")
            break
        
        print("Thinking...")
        
        # Query the database with the question
        response = query_database(question)
        
        # Print the response
        print("\nAnswer:\n", response)
        print("Done!")     
    
  

if __name__ == "__main__":
    asyncio.run(main())
