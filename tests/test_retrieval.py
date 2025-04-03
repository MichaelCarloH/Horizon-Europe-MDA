import pytest
import shutil
from src.retrieval import ProjectRetriever

@pytest.fixture
def retriever():
    """Fixture to set up a temporary database for testing."""
    db_path = "/tests/test_chromadb"
    retriever = ProjectRetriever(db_path=db_path)
    test_projects = [
        "AI for climate change adaptation in agriculture.",
        "Quantum computing for next-generation cybersecurity.",
        "Renewable energy storage solutions in Europe.",
    ]
    test_metadata = [
        {"title": "AI in Agriculture"},
        {"title": "Quantum Computing"},
        {"title": "Renewable Energy"},
    ]
    retriever.add_documents(docs=test_projects, metadata=test_metadata)
    yield retriever  # Provide the retriever to the test
    shutil.rmtree(db_path, ignore_errors=True)  # Clean up the test database

def test_add_documents(retriever):
    """Test if documents are added to the database."""
    # Check if the correct number of documents were added
    assert len(retriever.collection.get()["documents"]) == 3

def test_query(retriever):
    """Test if the query retrieves the correct documents."""
    results = retriever.query("climate and agriculture", top_k=1)
    assert len(results) == 1
    assert "AI for climate change adaptation in agriculture." in results[0]