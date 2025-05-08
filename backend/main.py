from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from src.create_database import DocumentProcessor
from src.query_database import query_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database if it doesn't exist
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma")
DATA_PATH = os.getenv("DATA_PATH", "data/pdf")

if not os.path.exists(CHROMA_PATH):
    logger.info("Database not found. Creating database...")
    try:
        processor = DocumentProcessor(data_path=DATA_PATH, chroma_path=CHROMA_PATH)
        processor.create_database_pipeline()
        logger.info("Database created successfully.")
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create database: {str(e)}")
else:
    logger.info("Database already exists. Skipping creation.")

class Question(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"message": "MDA Horizon Backend API is running"}

@app.post("/query")
async def query(question: Question):
    try:
        logger.info(f"Received query: {question.text}")
        response = query_database(question.text)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
