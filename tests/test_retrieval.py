import unittest
import shutil
from src.retrieval import ProjectRetriever

class TestProjectRetriever(unittest.TestCase):
    def setUp(self):
        """Set up a temporary database for testing."""
        self.db_path = "test_chromadb"
        self.retriever = ProjectRetriever(db_path=self.db_path)
        self.test_projects = [
            "AI for climate change adaptation in agriculture.",
            "Quantum computing for next-generation cybersecurity.",
            "Renewable energy storage solutions in Europe.",
        ]
        self.test_metadata = [
            {"title": "AI in Agriculture"},
            {"title": "Quantum Computing"},
            {"title": "Renewable Energy"},
        ]
        self.retriever.add_documents(docs=self.test_projects, metadata=self.test_metadata)

    def tearDown(self):
        """Clean up the test database."""
        shutil.rmtree(self.db_path, ignore_errors=True)

    def test_add_documents(self):
        """Test if documents are added to the database."""
        # Check if the correct number of documents were added
        self.assertEqual(len(self.test_projects), 3)

    def test_query(self):
        """Test if the query retrieves the correct documents."""
        results = self.retriever.query("climate and agriculture", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("AI for climate change adaptation in agriculture.", results)

    def test_query_no_results(self):
        """Test if the query handles no results gracefully."""
        results = self.retriever.query("nonexistent topic", top_k=1)
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()