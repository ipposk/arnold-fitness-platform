import os
import requests
import google.generativeai as genai

# Esegui la configurazione una sola volta all'import
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class FitnessRetriever:
    def __init__(self, collection_name=None):
        self.qdrant_url = os.environ["QDRANT_URL"]
        self.qdrant_api_key = os.environ.get("QDRANT_API_KEY")
        self.collection_name = collection_name or os.environ.get("QDRANT_COLLECTION", "arnold_fitness_chunks")

    def _encode_query(self, query_text: str) -> list:
        response = genai.embed_content(
            model="models/embedding-001",
            content=query_text,
            task_type="retrieval_query"
        )
        return response["embedding"]

    def search(self, query_text: str, limit=5, filters=None) -> list:
        query_vector = self._encode_query(query_text)
        url = f"{self.qdrant_url}collections/{self.collection_name}/points/search"
        headers = {"Content-Type": "application/json"}
        if self.qdrant_api_key:
            headers["api-key"] = self.qdrant_api_key

        body = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True  # <-- AGGIUNGI QUESTA RIGA!
        }
        if filters:
            body["filter"] = filters

        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        results = response.json()["result"]

        # Restituisce una lista di dict standardizzati (id, score, payload)
        return [
            {
                "id": r["id"],
                "score": r["score"],
                "payload": r.get("payload", {})
            } for r in results
        ]
