#!/usr/bin/env python3
"""
Script to test Qdrant connectivity and list existing collections.
"""

import os
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

def test_qdrant_connection():
    """Test basic Qdrant connectivity."""
    setup_environment()
    
    qdrant_url = os.environ.get("QDRANT_URL", "").rstrip('/')
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    
    print(f"Testing Qdrant connection...")
    print(f"URL: {qdrant_url}")
    print(f"API Key: {'[SET]' if qdrant_api_key else '[NOT SET]'}")
    
    headers = {}
    if qdrant_api_key:
        headers["api-key"] = qdrant_api_key
    
    try:
        # Test basic connectivity
        print("\\n--- Testing Basic Connectivity ---")
        response = requests.get(f"{qdrant_url}/", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Connection successful!")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    try:
        # List collections
        print("\\n--- Listing Collections ---")
        response = requests.get(f"{qdrant_url}/collections", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            collections = result.get("result", {}).get("collections", [])
            print(f"Found {len(collections)} collections:")
            for collection in collections:
                name = collection.get("name", "unknown")
                status = collection.get("status", "unknown")
                print(f"  - {name} (status: {status})")
        else:
            print(f"Error listing collections: {response.text}")
            
    except Exception as e:
        print(f"Error listing collections: {e}")
    
    # Try to check specific collection
    collection_name = os.environ.get("QDRANT_COLLECTION", "arnold_fitness_chunks")
    try:
        print(f"\\n--- Checking Collection: {collection_name} ---")
        response = requests.get(f"{qdrant_url}/collections/{collection_name}", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()["result"]
            print(f"Collection exists!")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Points: {result.get('points_count', 'unknown')}")
        elif response.status_code == 404:
            print(f"Collection '{collection_name}' does not exist")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error checking collection: {e}")

if __name__ == "__main__":
    test_qdrant_connection()