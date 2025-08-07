#!/usr/bin/env python3
"""
Script to setup the arnold_fitness_chunks collection in Qdrant.
This script creates the collection with the proper vector configuration.
"""

import os
import json
import requests
from pathlib import Path

def setup_environment():
    """Load environment variables from .env file."""
    parent_dir = Path(__file__).parent.parent
    env_path = parent_dir / '.env'
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('"').strip("'")

def check_collection_exists(qdrant_url: str, qdrant_api_key: str, collection_name: str) -> bool:
    """Check if collection exists."""
    headers = {}
    if qdrant_api_key:
        headers["api-key"] = qdrant_api_key
    
    try:
        response = requests.get(f"{qdrant_url}/collections/{collection_name}", headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Error checking collection: {e}")
        return False

def create_collection(qdrant_url: str, qdrant_api_key: str, collection_name: str) -> bool:
    """Create collection with proper configuration."""
    headers = {"Content-Type": "application/json"}
    if qdrant_api_key:
        headers["api-key"] = qdrant_api_key
    
    # Configuration for Gemini embedding-001 model (768 dimensions)
    config = {
        "vectors": {
            "size": 768,
            "distance": "Cosine"
        },
        "optimizers_config": {
            "default_segment_number": 2
        },
        "replication_factor": 1
    }
    
    try:
        response = requests.put(
            f"{qdrant_url}/collections/{collection_name}",
            headers=headers,
            json=config
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("status") == "ok"
        
    except Exception as e:
        print(f"Error creating collection: {e}")
        return False

def main():
    """Main function to setup Qdrant collection."""
    print("=== Arnold Fitness Qdrant Collection Setup ===\\n")
    
    setup_environment()
    
    qdrant_url = os.environ.get("QDRANT_URL", "").rstrip('/')
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    collection_name = os.environ.get("QDRANT_COLLECTION", "arnold_fitness_chunks")
    
    print(f"Qdrant URL: {qdrant_url}")
    print(f"Collection name: {collection_name}")
    
    if not qdrant_url:
        print("Error: QDRANT_URL not set in environment")
        return
    
    # Check if collection exists
    print(f"\\nChecking if collection '{collection_name}' exists...")
    if check_collection_exists(qdrant_url, qdrant_api_key, collection_name):
        print(f"✅ Collection '{collection_name}' already exists!")
        return
    
    # Create collection
    print(f"Creating collection '{collection_name}'...")
    success = create_collection(qdrant_url, qdrant_api_key, collection_name)
    
    if success:
        print(f"✅ Collection '{collection_name}' created successfully!")
    else:
        print(f"❌ Failed to create collection '{collection_name}'")

if __name__ == "__main__":
    main()