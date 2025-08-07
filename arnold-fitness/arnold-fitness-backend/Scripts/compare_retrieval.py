# scripts/compare_retrieval.py
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.db_fitness_interface.fitness_retriever import FitnessRetriever


def test_retrieval(query_text="vorrei testare esempio.com"):
    """Testa il retrieval con la query standard"""
    retriever = FitnessRetriever()

    print(f"🔍 Test retrieval con query: '{query_text}'")
    print(f"Collection: {os.getenv('QDRANT_COLLECTION', 'pentesting_chunks')}")
    print(f"URL: {os.getenv('QDRANT_URL')}")
    print("=" * 60)

    try:
        # Esegui ricerca
        results = retriever.search(query_text, limit=5)

        print(f"\n✅ Trovati {len(results)} risultati\n")

        # Salva risultati per confronto
        output = {
            "query": query_text,
            "config": {
                "url": os.getenv('QDRANT_URL'),
                "collection": os.getenv('QDRANT_COLLECTION', 'pentesting_chunks')
            },
            "results": []
        }

        for i, res in enumerate(results, 1):
            payload = res.get('payload', {})
            result_data = {
                "position": i,
                "id": res.get('id'),
                "score": res.get('score', 0),
                "question": payload.get('question', 'N/A'),
                "answer": payload.get('answer', 'N/A')[:500],  # Primi 500 char
                "metadata": payload.get('metadata', {})
            }
            output["results"].append(result_data)

            print(f"Risultato {i}:")
            print(f"  Score: {result_data['score']:.4f}")
            print(f"  Q: {result_data['question'][:80]}...")
            print(f"  A: {result_data['answer'][:80]}...")
            print()

        # Salva output per confronto
        output_file = Path("local_run_data") / "qdrant_test_results.json"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Risultati salvati in: {output_file}")

        return results

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test con query standard
    test_retrieval()

    # Test con altre query comuni
    print("\n" + "=" * 60 + "\n")
    test_retrieval("nmap port scanning")