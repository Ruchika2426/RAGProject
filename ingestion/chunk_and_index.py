import os
import json
import glob
import chromadb
from chromadb.utils import embedding_functions

def index_data():
    parsed_dir = os.path.join("data", "parsed")
    if not os.path.exists(parsed_dir):
        print(f"Directory {parsed_dir} does not exist.")
        return
        
    db_path = os.path.join("data", "vector_db")
    os.makedirs(db_path, exist_ok=True)
    
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    # Using BAAI/bge-small-en-v1.5 as it is state-of-the-art for short retrieval chunks
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
    
    collection = client.get_or_create_collection(
        name="mutual_funds",
        embedding_function=sentence_transformer_ef
    )
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in glob.glob(os.path.join(parsed_dir, "*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        fund_name = data.get("fund_name", os.path.basename(file_path).replace(".json", ""))
        
        # Document-Level Chunking Strategy
        # Combine all non-null values into a single dense context string
        chunk_parts = [f"Fund Name: {fund_name}"]
        for key, value in data.items():
            if key != "fund_name" and value is not None:
                friendly_key = key.replace("_", " ").title()
                chunk_parts.append(f"{friendly_key}: {value}")
                
        document_text = "\n".join(chunk_parts)
        
        # Metadata
        metadata = {
            "source": f"https://groww.in/mutual-funds/{fund_name}",
            "fund_name": fund_name
        }
        
        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(fund_name)
        
        print(f"Prepared document for: {fund_name}")
        
    if documents:
        print(f"Indexing {len(documents)} documents into ChromaDB...")
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Indexing complete.")
    else:
        print("No documents found to index.")

if __name__ == "__main__":
    index_data()
