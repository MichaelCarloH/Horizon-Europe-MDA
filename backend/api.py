import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.create_database import DocumentProcessor
from src.query_database import query_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for the frontend (make sure to replace this with your frontend's URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development URL
        "https://horizon-europe-mda.vercel.app/",  # Your deployed frontend URL
    ],  # Your frontend's URL, adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

try:
    # Initialize the document processing pipeline
    processor = DocumentProcessor()
    processor.create_database_pipeline()
    logger.info("Database pipeline successfully initialized.")
except Exception as e:
    logger.error(f"Failed to initialize database pipeline: {str(e)}")

class QueryRequest(BaseModel):
    query_text: str
    k: int = 3  # Default top-k results

@app.get("/")
def home():
    return {"message": "RAG API is running!"}

@app.post("/query/")
def query_db(request: QueryRequest):
    try:
        response = query_database(request.query_text, request.k)
        return {"query": request.query_text, "response": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# To run: uvicorn api:app --reload
