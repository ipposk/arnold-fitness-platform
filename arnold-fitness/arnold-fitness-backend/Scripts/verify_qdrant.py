# scripts/verify_qdrant_config.py
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

print("🔍 VERIFICA CONFIGURAZIONE QDRANT")
print("=" * 60)

# Configurazione Locale
print("\n📁 CONFIGURAZIONE LOCALE (.env):")
print(f"QDRANT_URL: {os.getenv('QDRANT_URL')}")
print(
    f"QDRANT_API_KEY: {'***' + os.getenv('QDRANT_API_KEY', '')[-4:] if os.getenv('QDRANT_API_KEY') else 'NON PRESENTE'}")
print(f"QDRANT_COLLECTION: {os.getenv('QDRANT_COLLECTION', 'pentesting_chunks')}")

# Configurazione AWS (da serverless.yml)
print("\n☁️ CONFIGURAZIONE AWS (serverless.yml):")
print("QDRANT_URL: ${env:QDRANT_URL}")
print("QDRANT_API_KEY: ${env:QDRANT_API_KEY}")
print("QDRANT_COLLECTION: pentesting_chunks")

# Test retrieval
print("\n🧪 TEST RETRIEVAL CON QUERY STANDARD:")
from src.db_fitness_interface.fitness_retriever import FitnessRetriever

retriever = FitnessRetriever()
test_query = "vorrei testare esempio.com"

try:
    results = retriever.search(test_query, limit=5)
    print(f"\n✅ Retrieval riuscito! Trovati {len(results)} risultati")

    if results:
        print("\nPrimo risultato:")
        first = results[0]
        print(f"Score: {first.get('score', 0):.4f}")
        print(f"Question: {first.get('payload', {}).get('question', 'N/A')[:100]}...")
        print(f"Answer: {first.get('payload', {}).get('answer', 'N/A')[:100]}...")
except Exception as e:
    print(f"\n❌ Errore retrieval: {e}")