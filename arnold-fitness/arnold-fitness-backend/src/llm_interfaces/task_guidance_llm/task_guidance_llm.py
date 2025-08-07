from typing import List, Dict, Any
from src.llm_interfaces.clients.gemini_client import GeminiClient
from src.logger.logger import Logger
from src.db_fitness_interface.mock_fitness_retriever import MockFitnessRetriever as FitnessRetriever
import os


class TaskGuidanceLLM:
    def __init__(self, llm_client: GeminiClient, prompt_template_path: str, retriever: FitnessRetriever):
        self.llm_client = llm_client
        self.retriever = retriever
        self.logger = Logger("TaskGuidanceLLM")

        # K configurabile via environment, default 5
        self.retrieval_k = int(os.getenv("RETRIEVAL_K", "5"))

        if not os.path.exists(prompt_template_path):
            raise FileNotFoundError(f"Prompt file non trovato: {prompt_template_path}")

        with open(prompt_template_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def _format_documents(self, documents: List[Dict[str, Any]]) -> str:
        """
        Formatta i documenti per il prompt template.
        Mantiene il formato originale che funziona già bene.
        """
        chunks = []
        for i, doc in enumerate(documents, 1):
            payload = doc.get("payload", {})
            score = doc.get("score", 0)

            # Aggiungi score per trasparenza (utile per debug)
            content = f"- [{payload.get('metadata', {}).get('title', 'Untitled')}] (score: {score:.3f})\n"
            content += f"  Question: {payload.get('question', 'N/A')}\n"
            content += f"  Answer: {payload.get('answer', 'N/A')}\n"
            content += f"  Tags: {', '.join(payload.get('metadata', {}).get('tags', []))}"
            chunks.append(content)

        return "\n\n".join(chunks) if chunks else "Nessun documento trovato."

    def generate_guidance(
            self,
            context: Dict[str, Any],
            query_data: Dict[str, Any]
    ) -> str:
        query_text = query_data.get("query_text")
        filters = query_data.get("filters", {})

        self.logger.log_info("Avvio del retrieval in Qdrant", {
            "query_text": query_text,
            "filters": filters,
            "k": self.retrieval_k
        })

        # Retrieval con K configurabile
        retrieved_documents = self.retriever.search(query_text, limit=self.retrieval_k)

        # Log statistiche utili per tuning
        if retrieved_documents:
            scores = [doc.get("score", 0) for doc in retrieved_documents]
            self.logger.log_info("Statistiche retrieval", {
                "docs_retrieved": len(retrieved_documents),
                "max_score": max(scores),
                "min_score": min(scores),
                "avg_score": sum(scores) / len(scores)
            })

        # Costruzione prompt - il template gestisce TUTTA la logica
        prompt = self.prompt_template.format(
            context=context,
            retrieved_knowledge=self._format_documents(retrieved_documents)
        )

        self.logger.log_info("Prompt costruito per TaskGuidanceLLM", {
            "prompt_length": len(prompt)
        })

        # Chiamata LLM
        response = self.llm_client.generate_response(prompt)
        self.logger.log_info(f"Risposta ricevuta, lunghezza: {len(response)}")

        # ✅ Test rapido del JSON per logging/debug
        import json
        try:
            json.loads(response)
            self.logger.log_info("✅ JSON valido ricevuto da TaskGuidanceLLM")
        except json.JSONDecodeError as e:
            self.logger.log_error(f"❌ JSON non valido generato da LLM: {e}")
            self.logger.log_error(f"Ultimi 200 caratteri della risposta: ...{response[-200:]}")
            # Nota: non solleviamo eccezioni qui, lascia gestire all'orchestrator

        return response
