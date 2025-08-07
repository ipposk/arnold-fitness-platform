# scripts/test_embedding.py
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

def test_embedding(query="vorrei testare esempio.com"):
    """Testa l'embedding della query"""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    print(f"🔍 Test embedding per: '{query}'")

    response = genai.embed_content(
        model="models/embedding-001",
        content=query,
        task_type="retrieval_query"
    )

    embedding = response["embedding"]

    print(f"✅ Embedding generato")
    print(f"   Dimensione: {len(embedding)}")
    print(f"   Primi 10 valori: {embedding[:10]}")
    print(f"   Hash (per confronto): {hash(tuple(embedding[:50]))}")

    return embedding

if __name__ == "__main__":
    # Test embedding standard
    test_embedding()

    # Test con variazioni
    print("\n" + "=" * 60 + "\n")
    test_embedding("vorrei testare google.com")