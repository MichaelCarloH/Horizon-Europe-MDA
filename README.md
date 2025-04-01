# Horizon-Europe-MDA

# Horizon Europe Analysis

## Project Structure

```plaintext
/horizon-europe-analysis
│── /data                # Raw and processed datasets
│── /notebooks           # Jupyter notebooks for exploration & testing
│── /src                 # Main source code
│   │── __init__.py
│   │── data_processing.py    # Preprocessing (cleaning, formatting)
│   │── topic_modeling.py     # LDA/BERT embeddings for themes
│   │── retrieval.py          # FAISS/ChromaDB for document search
│   │── rag_model.py          # Integration with OpenAI/LLM
│   │── api.py                # Flask/FastAPI for querying the dataset
│   │── dashboard.py          # Dash/Plotly app for visualization
│── /models              # Saved models (LDA, embeddings, etc.)
│── /config              # Configuration files (API keys, settings)
│── /deployment          # Azure deployment scripts (Docker, Terraform)
│── requirements.txt      # Dependencies
│── .gitignore           # Ignore unnecessary files
│── README.md            # Project documentation
```

## Step-by-Step Plan

### 1. Data Exploration (`notebooks/`)
- Load dataset using `pandas`
- Handle missing values and data inconsistencies
- Analyze distributions and key variables

### 2. Data Preprocessing (`src/data_processing.py`)
- Clean and structure the dataset
- Normalize text descriptions
- Standardize categorical variables

### 3. Topic Modeling & NLP (`src/topic_modeling.py`)
- Implement **LDA** for topic extraction
- Use `sentence-transformers` to generate embeddings
- Cluster projects based on research themes

### 4. Retrieval-Augmented Generation (RAG) (`src/retrieval.py` & `src/rag_model.py`)
- Store embeddings in **FAISS/ChromaDB**
- Develop a **retriever model** for document search
- Integrate **GPT/LLM** for natural language responses

### 5. API Development (`src/api.py`)
- Build a **Flask/FastAPI** backend to handle queries
- Expose endpoints for project search and summaries

### 6. Data Visualization & Dashboard (`src/dashboard.py`)
- Develop an interactive dashboard with **Dash/Plotly**
- Provide insights on funding distribution, research themes, and collaborations

### 7. Deployment (`/deployment/`)
- Deploy the API and dashboard on **Azure**
- Use **Docker & Terraform** for cloud infrastructure setup

## Goals & Impact
- Provide an **interactive, data-driven platform** for exploring Horizon Europe projects
- Enable **NLP-powered insights** into research themes and funding trends
- Improve **stakeholder accessibility** to research data using **RAG-LLM**

---

This roadmap ensures that all team members can contribute effectively to the project. 🚀

