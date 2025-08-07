#!/usr/bin/env python3
"""
Script to load fitness knowledge content into Qdrant vector database.
This script processes all JSON files in the fitness_knowledge directory
and uploads them as vector embeddings to the arnold_fitness_chunks collection.
"""

import os
import json
import uuid
from pathlib import Path
import google.generativeai as genai
import requests
from typing import List, Dict, Any

def setup_environment():
    """Configure API keys and environment."""
    # Load environment variables from parent directory .env if needed
    parent_dir = Path(__file__).parent.parent
    env_path = parent_dir / '.env'
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('\"').strip("'")
    
    # Configure Gemini
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def create_embedding(text: str) -> List[float]:
    """Create embedding for given text using Gemini."""
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

def load_knowledge_files(knowledge_dir: Path) -> List[Dict[str, Any]]:
    """Load all JSON knowledge files from directory structure."""
    documents = []
    
    for category_dir in knowledge_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        print(f"Loading category: {category_dir.name}")
        
        for json_file in category_dir.glob("*.json"):
            print(f"  Processing file: {json_file.name}")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                for item in content:
                    # Create comprehensive searchable text
                    searchable_text = f"{item['question']} {item['answer']}"
                    if 'tags' in item.get('metadata', {}):
                        searchable_text += " " + " ".join(item['metadata']['tags'])
                    
                    document = {
                        "id": str(uuid.uuid4()),
                        "text": searchable_text,
                        "question": item["question"],
                        "answer": item["answer"],
                        "metadata": item["metadata"],
                        "category_dir": category_dir.name
                    }
                    
                    documents.append(document)
                    
            except Exception as e:
                print(f"  Error processing {json_file}: {e}")
    
    print(f"\\nTotal documents loaded: {len(documents)}")
    return documents

def upload_to_qdrant(documents: List[Dict[str, Any]], 
                     qdrant_url: str, 
                     qdrant_api_key: str, 
                     collection_name: str) -> bool:
    """Upload documents to Qdrant collection."""
    
    print(f"Uploading to Qdrant collection: {collection_name}")
    
    # Prepare points for batch upload
    points = []
    
    for i, doc in enumerate(documents):
        print(f"Creating embedding for document {i+1}/{len(documents)}: {doc['question'][:50]}...")
        
        try:
            # Create embedding
            embedding = create_embedding(doc["text"])
            
            # Prepare point
            point = {
                "id": doc["id"],
                "vector": embedding,
                "payload": {
                    "question": doc["question"],
                    "answer": doc["answer"],
                    "category": doc["metadata"].get("category", ""),
                    "subcategory": doc["metadata"].get("subcategory", ""),
                    "checklist_ids": doc["metadata"].get("checklist_ids", []),
                    "difficulty": doc["metadata"].get("difficulty", "intermediate"),
                    "evidence_level": doc["metadata"].get("evidence_level", "medium"),
                    "tags": doc["metadata"].get("tags", []),
                    "category_dir": doc["category_dir"],
                    "text": doc["text"]
                }
            }
            
            points.append(point)
            
        except Exception as e:
            print(f"  Error creating embedding for document {i+1}: {e}")
            continue
    
    if not points:
        print("No points to upload!")
        return False
    
    # Upload in batches
    batch_size = 50
    total_batches = (len(points) + batch_size - 1) // batch_size
    
    headers = {
        "Content-Type": "application/json"
    }
    if qdrant_api_key:
        headers["api-key"] = qdrant_api_key
    
    url = f"{qdrant_url}/collections/{collection_name}/points"
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, len(points))
        batch_points = points[start_idx:end_idx]
        
        print(f"Uploading batch {batch_num + 1}/{total_batches} ({len(batch_points)} points)")
        
        payload = {
            "points": batch_points
        }
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("status") != "ok":
                print(f"  Warning: Batch {batch_num + 1} returned status: {result.get('status')}")
            else:
                print(f"  Batch {batch_num + 1} uploaded successfully")
                
        except Exception as e:
            print(f"  Error uploading batch {batch_num + 1}: {e}")
            return False
    
    print(f"\\nSuccessfully uploaded {len(points)} points to Qdrant!")
    return True

def verify_collection_info(qdrant_url: str, qdrant_api_key: str, collection_name: str):
    """Verify collection exists and show info."""
    headers = {}
    if qdrant_api_key:
        headers["api-key"] = qdrant_api_key
    
    try:
        # Get collection info
        response = requests.get(f"{qdrant_url}/collections/{collection_name}", headers=headers)
        response.raise_for_status()
        
        info = response.json()["result"]
        print(f"\\nCollection '{collection_name}' info:")
        print(f"  Status: {info.get('status', 'unknown')}")
        print(f"  Points count: {info.get('points_count', 'unknown')}")
        print(f"  Vector size: {info.get('config', {}).get('params', {}).get('vectors', {}).get('size', 'unknown')}")
        
    except Exception as e:
        print(f"Error getting collection info: {e}")

def main():
    """Main function to load fitness knowledge into Qdrant."""
    print("=== Arnold Fitness Knowledge Loader ===\\n")
    
    # Setup
    setup_environment()
    
    # Configuration
    qdrant_url = os.environ.get("QDRANT_URL", "").rstrip('/')
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    collection_name = os.environ.get("QDRANT_COLLECTION", "arnold_fitness_chunks")
    
    # Paths
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    knowledge_dir = backend_dir / "data" / "fitness_knowledge"
    
    print(f"Knowledge directory: {knowledge_dir}")
    print(f"Qdrant URL: {qdrant_url}")
    print(f"Collection name: {collection_name}")
    
    if not knowledge_dir.exists():
        print(f"Error: Knowledge directory not found: {knowledge_dir}")
        return
    
    if not qdrant_url:
        print("Error: QDRANT_URL not set in environment")
        return
    
    # Load knowledge files
    print("\\n--- Loading Knowledge Files ---")
    documents = load_knowledge_files(knowledge_dir)
    
    if not documents:
        print("No documents found to upload!")
        return
    
    # Upload to Qdrant
    print("\\n--- Uploading to Qdrant ---")
    success = upload_to_qdrant(documents, qdrant_url, qdrant_api_key, collection_name)
    
    if success:
        print("\\n--- Verification ---")
        verify_collection_info(qdrant_url, qdrant_api_key, collection_name)
        print("\\n✅ Fitness knowledge loading completed successfully!")
    else:
        print("\\n❌ Failed to load fitness knowledge")

if __name__ == "__main__":
    main()