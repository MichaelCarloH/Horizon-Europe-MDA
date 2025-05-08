import sys
import os
import sqlite3
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database creator and query processor
processor = DatabaseCreator()
query_processor = QueryProcessor()

# Create database on startup
try:
    processor.create_database_pipeline()
except Exception as e:
    logger.error(f"Error creating database: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Failed to create database: {str(e)}")

class Query(BaseModel):
    query_text: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
