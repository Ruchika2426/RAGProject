import os
import json
import requests
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

# Explicitly load .env from the parent directory and override any stale environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path, override=True)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize FastAPI App
app = FastAPI(title="HDFC Mutual Funds RAG API")

# Phase 3: Guardrail Keywords
ADVISORY_KEYWORDS = [
    r"\bshould i invest\b", r"\brecommend\b", r"\bbest fund\b", 
    r"\bwhere to invest\b", r"\bbuy\b", r"\bsell\b", r"\bportfolio advice\b",
    r"\bwhich fund\b", r"\badvice\b", r"\bgood investment\b"
]

def is_advisory_query(query: str) -> bool:
    query_lower = query.lower()
    for keyword in ADVISORY_KEYWORDS:
        if re.search(keyword, query_lower):
            return True
    return False


# Initialize ChromaDB
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "vector_db")
client = chromadb.PersistentClient(path=db_path)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")

try:
    collection = client.get_collection(name="mutual_funds", embedding_function=sentence_transformer_ef)
except Exception as e:
    print("Warning: Collection 'mutual_funds' not found. Make sure to run the ingestion script first.")
    collection = None

# Define Request Model
class ChatRequest(BaseModel):
    query: str
    model: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile") # Default Groq model

# Define the Prompt Template
PROMPT_TEMPLATE = """You are a helpful, factual financial chatbot for HDFC Mutual Funds. 
You must follow these strict rules:
1. Provide facts only. Do not give any investment advice or opinions.
2. Limit your response to a maximum of 3 sentences.
3. Include exactly one markdown citation link at the end of the text.
4. You must append this exact footer on a new line at the very end: "Last updated from sources: {date}"

Context from the Knowledge Base:
{context}

User Query:
{query}

Your Response:"""

@app.post("/chat")
def chat(request: ChatRequest):
    if not collection:
        raise HTTPException(status_code=500, detail="Vector DB not initialized.")
        
    query = request.query
    
    # Phase 3 Guardrail: Pre-Retrieval Advisory Check
    if is_advisory_query(query):
        return {
            "query": query,
            "response": "I can only provide factual information. For investment advice, please consult a SEBI registered advisor or visit AMFI.",
            "sources": ["https://www.amfiindia.com/"]
        }
    
    # Step 1: Semantic Search in ChromaDB (Retrieve-All Strategy)
    results = collection.query(
        query_texts=[query],
        n_results=5 # Retrieve all 5 chunks to guarantee entity accuracy
    )
    
    if not results['documents'][0]:
        return {"response": "I'm sorry, I couldn't find any relevant information about that in the HDFC funds knowledge base."}
        
    # Combine retrieved context
    retrieved_chunks = results['documents'][0]
    metadata_list = results['metadatas'][0]
    
    context = ""
    for idx, (chunk, meta) in enumerate(zip(retrieved_chunks, metadata_list)):
        context += f"--- Document {idx+1} (Source: {meta.get('source', 'Unknown')}) ---\n"
        context += chunk + "\n\n"
        
    # Build prompt
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = PROMPT_TEMPLATE.format(context=context, query=query, date=current_date)
    
    # Step 2: Call Groq API
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=request.model,
        )
        llm_output = chat_completion.choices[0].message.content.strip()
        
        # Phase 3 Formatting: Force exact footer and one source
        primary_source = metadata_list[0].get('source') if metadata_list else "Unknown Source"
        # Check if LLM included a link, if not, append it
        if "[Source]" not in llm_output and "http" not in llm_output:
            llm_output += f"\n\n[Source]({primary_source})"
            
        if f"Last updated from sources: {current_date}" not in llm_output:
            llm_output += f"\nLast updated from sources: {current_date}"
            
        return {
            "query": query,
            "response": llm_output,
            "sources": [meta.get('source') for meta in metadata_list]
        }
    except Exception as e:
        print(f"Groq API Error: {e}")
        # Fallback if Groq is not available
        return {
            "query": query,
            "response": "I found the information, but the Groq LLM is currently unavailable to summarize it. Please check your API key.",
            "sources": [meta.get('source') for meta in metadata_list],
            "raw_context": context
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
