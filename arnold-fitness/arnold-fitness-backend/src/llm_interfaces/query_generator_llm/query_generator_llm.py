import os
from typing import Dict, Any
from src.llm_interfaces.clients.gemini_client import GeminiClient  # o altro LLM client
from src.logger.logger import Logger


class QueryGeneratorLLM:
    def __init__(self, llm_client: GeminiClient, prompt_templates_dir: str):
        self.client = llm_client
        self.prompt_templates_dir = prompt_templates_dir
        self.logger = Logger("QueryGeneratorLLM")

    def generate_query(self, context: dict) -> Dict[str, Any]:
        prompt_template_path = os.path.join(self.prompt_templates_dir, "query_generator.txt")
        prompt = self._build_prompt(context, prompt_template_path)

        self.logger.log_info("Prompt costruito per QueryGeneratorLLM", {"prompt": prompt})
        try:
            response = self.client.generate_response(prompt)
            self.logger.log_info("La risposta del QueryGeneratorLLM", {"response": response})
            # AGGIUNGI: Log della query generata
            parsed = self._parse_response(response)
            if parsed.get('query_text'):
                print(f"\n🔍 QUERY GENERATA: '{parsed['query_text']}'")
                print(f"   Filtri: {parsed.get('filters', {})}")
                
            return self._parse_response(response)
        except Exception as e:
            self.logger.log_error("Errore durante la generazione della query", {"error": str(e)})
            return {}

    def _build_prompt(self, context: dict, prompt_template_path: str) -> str:
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            template = f.read()

        return template.replace("{filtered_context}", str(context))

    def _parse_response(self, raw_response: str) -> Dict[str, Any]:
        import json
        try:
            response = json.loads(raw_response)
            if "query_text" in response:
                return response
            else:
                raise ValueError("La risposta non contiene 'query_text'")
        except Exception as e:
            self.logger.log_error("Errore nel parsing della risposta LLM", {"error": str(e)})
            return {}