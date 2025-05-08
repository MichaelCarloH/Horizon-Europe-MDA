import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.create_database import DocumentProcessor
from src.query_database import query_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure deployment ready - Updated for deployment
app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database if it doesn't exist
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
if not os.path.exists(CHROMA_PATH):
    logger.info("Database not found. Creating database...")
    try:
        processor = DocumentProcessor()
        processor.create_database_pipeline()
        logger.info("Database created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database: {str(e)}")
else:
    logger.info("Database already exists. Skipping creation.")

class QueryRequest(BaseModel):
    query_text: str
    k: int = 3  # Default top-k results

@app.get("/")
def home():
    return {"message": "MDA Horizon Backend API is running!"}

@app.post("/query/")
def query_db(request: QueryRequest):
    try:
        logger.info(f"Processing query: {request.query_text}")
        response = query_database(request.query_text, request.k)
        logger.info("Query processed successfully")
        return {"query": request.query_text, "response": response}
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# To run: uvicorn api:app --reload
