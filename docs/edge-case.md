# Edge Cases & Corner Scenarios: Mutual Fund FAQ Assistant (Free/Open-Source Stack)

This document outlines the potential edge cases and corner scenarios for the Mutual Fund FAQ Assistant across its entire lifecycle, aligned with the phases defined in the `implementation-plan.md` and the `architecture.md`, explicitly addressing the constraints of a 100% free, local open-source stack.

## Phase 1: Setup & Data Ingestion Pipeline

| Scenario | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **URL Unreachable (404/5xx)** | A target HDFC URL on Groww is temporarily down or has been moved. | Implement retry mechanisms with exponential backoff in the BeautifulSoup scraper. Alert administrators if a URL consistently fails. |
| **HTML Structure Changes** | The target website changes its DOM structure, breaking the scraper. | Use robust parsing strategies (e.g., semantic HTML tags rather than strict CSS selectors). Implement alerting when extracted text volume drops. |
| **HuggingFace Model Download Failure** | The embedding model (`all-MiniLM-L6-v2`) fails to download on the first run due to network issues. | Add try/catch blocks around the model initialization to retry the download, or require manual pre-downloading in setup instructions. |
| **ChromaDB Disk Space / Write Lock** | The local disk runs out of space, or ChromaDB experiences a SQLite write lock during concurrent indexing. | Ensure proper error handling for disk full errors. Use single-threaded batch ingestion to avoid SQLite lock contention. |
| **Missing Metadata** | The scraped page does not contain a clear "Last Updated" date. | Fallback to the date of scraping/indexing as the "Last Updated" date, clearly indicating this in the metadata and footer. |
| **Rate Limiting/IP Blocking** | The data source blocks the scraper during data extraction. | Implement rate limiting in the `requests` library, use random delays between requests. |

## Phase 2: RAG Backend Core & LLM Integration

| Scenario | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Ollama Service Down** | The local Ollama daemon is not running when FastAPI attempts to generate a response. | The backend should gracefully catch connection refused errors and return to the UI: _"The local LLM service is offline. Please start Ollama."_ |
| **OOM (Out of Memory) / VRAM Exhaustion** | The host machine lacks enough RAM/VRAM to run Llama 3/Mistral, leading to crashes or extreme latency. | Use quantized models (e.g., 4-bit quantization). Implement a strict timeout on the LLM generation call to prevent the backend from hanging forever. |
| **No Relevant Context Found** | The ChromaDB similarity score is below the acceptable threshold. | Return a default fallback message: _"I could not find information related to your query in the official documents."_ Do not pass empty context to the LLM. |
| **LLM Hallucinates Despite Instructions**| The local LLM uses its pre-trained knowledge instead of the provided context. | Use strict prompts: _"If the answer is not in the context, say 'I don't know'."_ Small local models require very strong, repetitive prompting to avoid hallucination. |

## Phase 3: Guardrails & Compliance Layer

| Scenario | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Implicit Advisory Queries** | User asks _"Is 2% a good expense ratio?"_ or _"Is this fund safe?"_ | Train the Python Guardrail heuristic/classifier to recognize subjective adjectives ("good", "safe", "best") as advisory, triggering a refusal. |
| **Comparative Factual Queries** | User asks _"Does the Mid Cap fund have a lower exit load than the Small Cap fund?"_ | Flag "compare" or "better/lower/higher than" queries in the Guardrail layer to enforce the "no comparisons" constraint. |
| **Prompt Injection Attacks** | User attempts to override system instructions (e.g., _"Ignore previous instructions"_). | The Python Guardrail layer should catch anomalous inputs before they reach Ollama. Use strict delimiters for user input. |
| **Missing Link in Post-Processing**| The retrieved chunk somehow lacks a source URL, causing the formatting step to crash. | The FastAPI backend should gracefully handle missing URLs by falling back to the root AMC/Groww URL or failing the response safely rather than crashing. |
| **Length Constraint Violation** | The local LLM ignores the 3-sentence limit instruction. | The FastAPI post-processing function must strictly truncate the text at the third period. |

## Phase 4: User Interface (Minimal Frontend)

| Scenario | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Streamlit Port Collision** | The default Streamlit port (8501) is already in use by another application. | Document instructions to run Streamlit on an alternative port (e.g., `streamlit run app.py --server.port 8502`). |
| **Backend Timeout** | The FastAPI backend takes too long to respond because the local LLM inference is slow. | The Streamlit UI should have a timeout limit (e.g., 30-45 seconds for local LLMs) and display a user-friendly "Processing taking longer than expected" message. |
| **Network Disconnection** | The user loses internet connection while waiting for a response. | Streamlit inherently handles disconnections via websockets, but add a clear error state if the FastAPI connection drops. |
| **Empty or Gibberish Queries** | User submits empty strings or random punctuation. | Streamlit validation should disable the submit action for empty inputs and reject strings composed entirely of non-alphanumeric characters. |
| **Malformed Backend Response** | Streamlit receives an HTML error page (e.g., 500 Server Error) instead of JSON from FastAPI. | Wrap the `requests.post()` in a try/catch block and display a generic "Service Error" in the chat rather than crashing Streamlit. |
