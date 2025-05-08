import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3

# Only use pysqlite3 in Azure environment
if os.getenv("AZURE_ENVIRONMENT"):
    import pysqlite3
    # Override the default sqlite3 with pysqlite3
    sys.modules['sqlite3'] = pysqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.create_database import DatabaseCreator
from src.query_database import QueryProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://mda-horizon-frontend.azurewebsites.net",  # Production frontend
    "https://mda-horizon-frontend-2025.azurewebsites.net",  # Alternative production URL
    "https://horizon-europe-mda.vercel.app"  # Vercel deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

def initialize_database():
    """Initialize the database with proper error handling."""
    try:
        # Create new database or append to existing
        processor = DatabaseCreator()
        processor.run()
        logger.info("Database initialization completed")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # If we're running locally, continue anyway
        if not os.getenv("AZURE_ENVIRONMENT"):
            logger.info("Running locally - continuing despite database error")
            return True
        return False

# Initialize the query processor
query_processor = QueryProcessor()

# Create or update database on startup - but don't fail if it doesn't work locally
if not initialize_database():
    logger.warning("Database initialization failed, but continuing startup")

class Query(BaseModel):
    query_text: str

@app.get("/health")
async def health_check():
    return {"message": "RAG API is running!"}

@app.post("/query")
async def query_endpoint(query: Query):
    try:
        response = query_processor.query(query.query_text)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
