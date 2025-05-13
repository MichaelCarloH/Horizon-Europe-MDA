import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi.responses import JSONResponse

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.database.database import get_db_connection
from src.processing.document_processor import DocumentProcessor
from src.processing.query_processor import QueryProcessor
from src.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

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
query_processor = QueryProcessor()
# Initialize vector store once
query_processor.initialize_vector_store()
query_processor.initialize_self_query_retriever()

# Pydantic models
class Query(BaseModel):
    text: str
    conversation_id: Optional[str] = None

class DocumentUpload(BaseModel):
    file_path: str
    metadata: Optional[dict] = None

class DocumentDelete(BaseModel):
    document_ids: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize services during startup."""
    try:
        logger.info("Starting up services...")
        # Ensure the vector store is initialized
        if not query_processor.vector_store:
            query_processor.initialize_vector_store()
            query_processor.initialize_self_query_retriever()
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        print(f"Warning: Error during startup: {e}")

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": app.version
    }

# Query endpoint
@app.post("/query")
async def query_endpoint(query: Query):
    """Process a query and return the response."""
    try:
        logger.info(f"Processing query: {query.text}")
        result = query_processor.query(query.text, query.conversation_id)
        logger.info("Query processed successfully")
        
        if "error" in result:
            logger.error(f"Query processing error: {result['error']}")
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
    """Upload a document to the vector store."""
    try:
        # Save file to upload directory
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        logger.info(f"Saving file to: {file_path}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document
        logger.info("Processing document")
        documents = document_processor.process_document(file_path)
        
        # Add to the shared vector store instance
        logger.info("Adding documents to vector store")
        query_processor.vector_store.add_documents(documents)
        
        logger.info(f"Successfully uploaded and processed document: {file.filename}")
        return {
            "message": "Document uploaded and processed successfully",
            "filename": file.filename,
            "chunks": len(documents),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents")
async def delete_documents(document_delete: DocumentDelete):
    try:
        query_processor.vector_store.delete_documents(document_delete.document_ids)
        return {"message": "Documents deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Vector store management endpoints
@app.get("/vector-store/stats")
async def get_vector_store_stats():
    try:
        stats = query_processor.vector_store.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting vector store stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-store/export-metadata")
async def export_metadata():
    try:
        metadata = query_processor.vector_store.export_metadata()
        return metadata
    except Exception as e:
        logger.error(f"Error exporting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation management endpoints
@app.post("/conversations/{conversation_id}/clear")
async def clear_conversation(conversation_id: str):
    """Clear conversation history."""
    try:
        query_processor.clear_conversation(conversation_id)
        return {"message": "Conversation cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history."""
    try:
        history = query_processor.get_conversation_history(conversation_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
