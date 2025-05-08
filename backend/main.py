from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from src.create_database import DocumentProcessor
from src.query_database import query_database

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
if not os.path.exists(CHROMA_PATH):
    print("Database not found. Creating database...")
    processor = DocumentProcessor()
    processor.create_database_pipeline()
    print("Database created successfully.")
else:
    print("Database already exists. Skipping creation.")

class Question(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"message": "MDA Horizon Backend API is running"}

@app.post("/query")
async def query(question: Question):
    try:
        response = query_database(question.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
