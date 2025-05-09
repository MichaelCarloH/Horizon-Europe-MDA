import os
import logging
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC, timezone
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path

from src.config import Settings
from src.database import get_db_connection
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.query_processor import QueryProcessor
from src.utils.logging_config import setup_logging
from src.utils.excel_importer import import_excel_to_documents, validate_excel_structure

# Setup logging
setup_logging()
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

@app.on_event("startup")
async def startup_event():
    """Initialize services during startup."""
    try:
        logger.info("Starting up services...")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Log error but don't fail startup - services can initialize later
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
    """Upload a document to the vector store."""
    try:
        # Save file to upload directory
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document and add to vector store
        documents = document_processor.process_document(file_path)
        vector_store.add_documents(documents)
        
        logger.info(f"Successfully uploaded document: {file.filename}")
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Upload an Excel file and import its contents into the vector store.
    The Excel file should have at least 'Question' and 'Answer' columns.
    Optional columns: 'Source', 'Category'
    """
    try:
        # Validate file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Validate Excel structure
            validation = validate_excel_structure(temp_path)
            if validation['missing_columns']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Excel file is missing required columns: {validation['missing_columns']}"
                )
            
            if validation['empty_rows']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Excel file has empty rows at indices: {validation['empty_rows']}"
                )
            
            # Import documents
            documents = import_excel_to_documents(temp_path)
            
            # Add to vector store
            vector_store.add_documents(documents)
            
            return {
                "message": "Excel file imported successfully",
                "stats": {
                    "total_documents": len(documents),
                    "has_source": validation['has_source'],
                    "has_category": validation['has_category']
                }
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
