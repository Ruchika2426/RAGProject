# Phase-Wise Implementation Plan: Mutual Fund FAQ Assistant (Free/Open-Source Stack)

This document outlines the step-by-step implementation strategy for building the RAG-based Mutual Fund FAQ Assistant, aligned with the defined architecture and problem statement constraints. All tools and dependencies specified are 100% free and open-source.

## Phase 1: Setup & Data Ingestion Pipeline
**Goal:** Establish the foundation and build the searchable knowledge base.

- **Step 1.1: Environment Setup:** Initialize the project repository, set up virtual environments, and install necessary dependencies (`langchain`, `huggingface-hub`, `chromadb`, `beautifulsoup4`, `fastapi`, `streamlit`, `ollama`).
- **Step 1.2: Web Scraper Development:** Build a lightweight scraper using **BeautifulSoup4** and **Requests** to target the 5 specific HDFC mutual fund URLs on Groww. Extract relevant text.
- **Step 1.3: Text Chunking:** Implement a **Document-Level Chunking** strategy. Because the JSON files are small, read the parsed JSON and format the key-value pairs into a single, cohesive string chunk per fund. This avoids context fragmentation.
- **Step 1.4: Embedding & Indexing:** Setup a free, local Embedding Model (**HuggingFace `BAAI/bge-small-en-v1.5`**) and a free, local Vector Database (**ChromaDB**). We explicitly chose ChromaDB over FAISS because our small dataset size (5 chunks) does not require FAISS's massive-scale optimizations, and ChromaDB natively stores the metadata and text documents. Embed the chunks and index them.

## Phase 2: RAG Backend Core & LLM Integration
**Goal:** Enable querying the Vector DB and generating responses using the LLM.

- **Step 2.1: Backend API Setup:** Create a robust backend service using **FastAPI** to handle incoming queries.
- **Step 2.2: Retrieval Mechanism:** Implement the logic to embed user queries and perform a **Retrieve-All (k=5)** search against ChromaDB. Because the database only contains 5 documents, retrieving all chunks guarantees the LLM receives the exact facts for the correct entity, bypassing the risk of dense embedding mismatch.
- **Step 2.3: Prompt Engineering:** Design a strict system prompt instructing the LLM to answer solely based on retrieved context, limit to 3 sentences, and fail gracefully.
- **Step 2.4: LLM Integration:** Connect a free, local LLM running via **Ollama** (e.g., `Llama 3 8B` or `Mistral`) to generate the response.

## Phase 3: Guardrails & Compliance Layer
**Goal:** Enforce the "Facts-only, No investment advice" constraints.

- **Step 3.1: Advisory Detection (Pre-Retrieval Guardrail):** Implement a Guardrail layer. Use a smaller, lightweight local model or heuristic keyword matching to analyze incoming queries for advisory intent *before* any database retrieval occurs.
- **Step 3.2: Refusal Handling & Short-Circuiting:** Configure the system to short-circuit the generation process for flagged queries, returning a polite, predefined refusal message and a link to AMFI/SEBI. For these queries, the retrieval step and LLM generation will be bypassed entirely.
- **Step 3.3: Output Formatting:** For factual queries that pass the guardrail, proceed with Retrieve-All (k=5) and build a Python post-processing function that enforces the inclusion of exactly one source link (from the retrieved metadata) and appends the required footer.

## Phase 4: User Interface (Minimal Frontend) & Groq Integration
**Goal:** Provide a clean, user-friendly interface and integrate Groq for fast LLM generation.

- **Step 4.1: UI Structure:** Build a lightweight frontend using **Streamlit** (100% free, Python-based).
- **Step 4.2: Mandatory Elements:** Add the welcome message, three clickable example factual questions, and the prominent disclaimer: _"Facts-only. No investment advice."_
- **Step 4.3: Groq LLM Integration:** Update the architecture to use **Groq** as the LLM provider instead of Ollama for faster inference, utilizing models like `llama3-8b-8192` via the Groq API.
- **Step 4.4: API Integration:** Connect the Streamlit interface to the FastAPI Backend using standard HTTP requests (`requests` library).

## Phase 5: Testing, Evaluation & Deployment
**Goal:** Ensure accuracy, stability, and prepare for release.

- **Step 5.1: Unit & Integration Testing:** Test the BeautifulSoup scraper, chunking logic, and Guardrail accuracy using `pytest` (Free).
- **Step 5.2: LLM Evaluation:** Run a test suite of factual queries against the Ollama local LLM to ensure it strictly adheres to the 3-sentence limit and does not hallucinate.
- **Step 5.3: Deployment:** Containerize the application using **Docker** and deploy using free tiers or self-hosted environments.
- **Step 5.4: Documentation:** Finalize the README.md with setup instructions, architecture overview, and known limitations.

## Phase 6: Automated Data Refresh (Scheduler)
**Goal:** Keep the mutual fund data fresh by scraping and re-indexing automatically.

- **Step 6.1: GitHub Actions Setup:** Create a GitHub Actions workflow (`.github/workflows/scheduler.yml`) to schedule the data ingestion pipeline.
- **Step 6.2: Timezone Configuration:** Configure a `cron` trigger in the workflow to execute exactly at **10:00 AM IST** (04:30 UTC) every day.
- **Step 6.3: Pipeline Execution:** The workflow will automatically set up Python, execute `fetch.py`, `parse.py`, and `chunk_and_index.py`, and then explicitly commit and push the updated ChromaDB `data/` folder back to the repository to persist the vector changes.
