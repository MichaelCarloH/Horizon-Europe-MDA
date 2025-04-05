from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import shutil

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "backend/chroma"
DATA_PATH = "data/pdf"  # Path to the directory containing PDFs


class DocumentProcessor:
    def __init__(self, data_path: str = DATA_PATH, chroma_path: str = CHROMA_PATH):
        self.data_path = data_path
        self.chroma_path = chroma_path
        self.documents = []
        self.chunks = []

    def create_database_pipeline(self):
        print("Loading documents...")
        self.load_documents()
        print(f"Loaded {len(self.documents)} documents.")
        
        print("Splitting documents into chunks...")
        self.split_text()
        print(f"Split into {len(self.chunks)} chunks.")
        
        print("Saving to Chroma database...")
        self.save_to_chroma()
        print("Database pipeline complete!")
        return self  # Return self to allow further chaining, if needed

    def load_documents(self):
        """
        Load all PDF files from the specified directory and extract text.
        """
        documents = []
        if not os.path.exists(self.data_path):
            print(f"❌ Directory '{self.data_path}' does not exist.")
            return self

        for file_name in os.listdir(self.data_path):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(self.data_path, file_name)
                loader = PyPDFLoader(file_path)  # Use PyPDFLoader to extract text
                docs = loader.load()
                documents.extend(docs)  # Append all extracted documents

        self.documents = documents  # Store loaded documents
        print(f"Loaded {len(documents)} documents from {self.data_path}.")
        return self  # Return self to allow chaining

    def get_document_count(self):
        if os.path.exists(self.chroma_path):
            # You could list files or use Chroma API to get the count of saved documents.
            print(f"Documents in Chroma: {len(os.listdir(self.chroma_path))}")
        else:
            print("❌ Chroma database not found!")


    def split_text(self):
        """
        Split the loaded documents into smaller chunks for embedding.
        """
        if not self.documents:
            print("❌ No documents loaded to split.")
            return self

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        self.chunks = text_splitter.split_documents(self.documents)
        print(f"Split {len(self.documents)} documents into {len(self.chunks)} chunks.")

        # Print an example chunk for debugging
        if self.chunks:
            document = self.chunks[0]
            print("Example Chunk Content:", document.page_content[:200])  # Preview first 200 characters
            print("Example Chunk Metadata:", document.metadata)

        return self  # Return self for chaining

    def save_to_chroma(self):
        """
        Save the document chunks to a Chroma vector database.
        """
        if not self.chunks:
            print("❌ No chunks to save.")
            return self

        # Clear out the database first.
        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)

        # Create a new DB from the documents.
        chroma_database = Chroma.from_documents(
            self.chunks, OpenAIEmbeddings(), persist_directory=self.chroma_path
        )
        chroma_database.persist()
        print(f"Saved {len(self.chunks)} chunks to {self.chroma_path}.")
        return self  # Return self for chaining

