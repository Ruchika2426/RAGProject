# HDFC Mutual Fund FAQ Assistant

A RAG-based AI assistant capable of answering factual questions about 5 specific HDFC mutual funds, strictly grounded in official documentation.

## Features
- **Facts-only**: Generates responses strictly based on the ingested knowledge base, with a 3-sentence limit.
- **Guardrails**: Built-in heuristic guardrail immediately rejects advisory questions (e.g., "should I invest?", "recommend").
- **Clear Sourcing**: Every answer provides exactly one direct markdown link to the source material and a final "last updated" footer.
- **Fast Generation**: Uses the Groq API (LLaMA-3 models) for incredibly fast inference.

## Architecture & Tech Stack
- **Ingestion**: BeautifulSoup4 (scraping)
- **Vector DB**: ChromaDB + `BAAI/bge-small-en-v1.5` HuggingFace Embeddings
- **Backend API**: FastAPI
- **LLM Engine**: Groq API
- **Frontend UI**: Streamlit

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Docker and Docker Compose (optional for containerized deployment)

### 2. Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_actual_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Local Installation (Without Docker)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Data Ingestion (Optional if data already exists):**
   ```bash
   python ingestion/chunk_and_index.py
   ```
3. **Run Backend:**
   ```bash
   python backend/api.py
   # Or using uvicorn: uvicorn backend.api:app --host 0.0.0.0 --port 8000
   ```
4. **Run Frontend (in a separate terminal):**
   ```bash
   streamlit run frontend/app.py
   ```

### 4. Running with Docker Compose

To spin up both the FastAPI backend and Streamlit frontend in containers:
```bash
docker-compose up --build
```
- Frontend will be available at: http://localhost:8501
- Backend API will be available at: http://localhost:8000

## Running Tests
Unit tests and Guardrail evaluations can be run via pytest:
```bash
pytest tests/
```
