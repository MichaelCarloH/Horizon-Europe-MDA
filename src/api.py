from fastapi import FastAPI

app = FastAPI()

@app.post("/add_project/")
async def add_project(text: str, metadata: dict):
    return {"message": "Project added successfully!"}

@app.get("/query/")
async def query_project(q: str):
    return {"results": ["Renewable energy storage"]}  # Dummy response
