import os
import logging
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.responses import JSONResponse

from src.config import Settings
from src.database import get_db_connection
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.query_processor import QueryProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="API for document-based question answering using RAG",
    version=settings.API_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStoreManager()
query_processor = QueryProcessor()

# Pydantic models
class Query(BaseModel):
    text: str
    conversation_id: Optional[str] = None

class DocumentUpload(BaseModel):
    file_path: str
    metadata: Optional[dict] = None

class DocumentDelete(BaseModel):
    document_ids: List[str]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

# Query endpoint
@app.post("/query")
async def query_endpoint(query: Query):
    """Process a query and return the response."""
    try:
        result = query_processor.query(query.text, query.conversation_id)
        if "error" in result:
            return JSONResponse(
                status_code=500,
                content=result
            )
        return result
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Document management endpoints
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document
        documents = document_processor.process_document(file_path)
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        return {"message": "Document processed and added successfully"}
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents")
async def delete_documents(document_delete: DocumentDelete):
    try:
        vector_store.delete_documents(document_delete.document_ids)
        return {"message": "Documents deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Vector store management endpoints
@app.get("/vector-store/stats")
async def get_vector_store_stats():
    try:
        stats = vector_store.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting vector store stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-store/export-metadata")
async def export_metadata():
    try:
        metadata = vector_store.export_metadata()
        return metadata
    except Exception as e:
        logger.error(f"Error exporting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation management endpoints
@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    try:
        query_processor.clear_conversation(conversation_id)
        return {"message": "Conversation cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    try:
        history = query_processor.get_conversation_history(conversation_id)
        return history
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
