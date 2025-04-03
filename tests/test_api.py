import pytest
from src.retrieval import ProjectRetriever

@pytest.fixture
def retriever():
    """Create a temporary in-memory database for testing."""
    return ProjectRetriever(db_path=":memory:")  # Use in-memory DB for tests

def test_add_and_query(retriever):
    """Test adding and retrieving documents."""
    retriever.add_documents(["AI for climate change"])
    results = retriever.query("climate")

    assert len(results) > 0
    assert "AI for climate change" in results[0]  # Check retrieval works
