# src/llm_interfaces/error_classifier_llm/error_classifier_llm.py
import os
import json
from src.llm_interfaces.clients.gemini_client import GeminiClient


# La funzione _parse_response può rimanere qui se usata solo da questa classe,
# oppure potrebbe essere spostata in un modulo di utility se usata da più classi LLM.
def _parse_response(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == -1:
        # Potresti voler loggare 'text' qui per debug se non è JSON
        print(
            f"[ErrorClassifierLLM._parse_response] WARN: Risposta non sembra contenere JSON valido. Testo: {text[:200]}...")  # Logga inizio testo
        raise ValueError("Risposta non contiene JSON valido")
    return json.loads(text[start:end])


class ErrorClassifierLLM:
    # Nome del parametro modificato per coerenza con serverless.yml e lambda_handlers.py
    def __init__(self, client: GeminiClient, prompt_template_path: str):  # Era prompt_template_file_path
        self.client = client
        if not os.path.exists(prompt_template_path):
            raise FileNotFoundError(f"File template prompt per ErrorClassifierLLM non trovato: {prompt_template_path}")
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
        print(f"[ErrorClassifierLLM] Prompt template caricato da: {prompt_template_path}")

    def is_error(self, user_input: str) -> bool:
        prompt = self.prompt_template.format(user_input=user_input)

        print(f"[ErrorClassifier] Input da classificare: '{user_input}'")

        response_text = self.client.generate_response(prompt)
        print(f"[ErrorClassifier] Risposta LLM: {response_text}")

        try:
            result = _parse_response(response_text)
            is_error_value = result.get("is_error", False)
            print(f"[ErrorClassifier] Classificato come errore: {is_error_value}")
            return is_error_value
        except Exception as e:
            print(f"[ErrorClassifier] ⚠️ Errore parsing: {e}")
            return False