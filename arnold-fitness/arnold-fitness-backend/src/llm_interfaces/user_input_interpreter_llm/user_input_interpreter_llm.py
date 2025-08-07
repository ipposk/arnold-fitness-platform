import os
import json
import re
from datetime import datetime
from src.logger.logger import Logger

def extract_relevant_phases(context: dict, window_size: int = 3) -> dict:
    current_phase_id = context.get("current_phase_id")
    all_phases = context.get("checklist", [])

    # Trova l'indice della fase corrente
    current_index = next((i for i, phase in enumerate(all_phases) if phase["phase_id"] == current_phase_id), None)

    if current_index is None:
        return context  # fallback in caso di errore

    # Determina gli indici della finestra: max 3 elementi (prev, current, next)
    start_index = max(current_index - 1, 0)
    end_index = min(current_index + 2, len(all_phases))  # +2 perché end è esclusivo

    reduced_checklist = all_phases[start_index:end_index]

    # Costruisci un nuovo contesto filtrato
    return {
        **context,
        "checklist": reduced_checklist
    }

class UserInputInterpreterLLM:
    def __init__(self, llm_client, prompt_templates_dir: str, component_name="UserInputInterpreterLLM"):
        self.llm_client = llm_client
        self.prompt_templates_dir = prompt_templates_dir
        self.logger = Logger(component_name)

    def safe_parse_json(self, text: str) -> dict:
        try:
            json_start = text.find("{")
            json_part = text[json_start:]
            return json.loads(json_part)
        except Exception as e:
            self.logger.log_error("Errore durante il parsing JSON", {"error": str(e)})
            return {}

    def process_input(self, user_input: str, current_context: dict, test_id: str, pt_type: str) -> dict:
        prompt_template_path = os.path.join(self.prompt_templates_dir, "update_context_with_observation.txt")

        filtered_context = extract_relevant_phases(current_context)
        # DEBUG: Verifica contesto prima della costruzione del prompt
        print("🔍 DEBUG - CONTESTO PER L'INTERPRETE:")
        print(f"   Test ID: {test_id}")
        print(f"   User input: '{user_input}'")
        if "last_output" in current_context:
            last_output = current_context["last_output"]
            guidance_markdown = last_output.get("guidance_markdown", "")
            print(f"   Last output presente: {len(guidance_markdown)} caratteri")
            print(f"   Ultimi suggerimenti (primi 300 caratteri):")
            print(f"   {guidance_markdown[:300]}...")
        else:
            print("   ❌ PROBLEMA: Last output NON presente nel contesto!")
        print("   ---")
        prompt = self._build_prompt(
            prompt_template_path=prompt_template_path,
            user_input=user_input,
            current_context=filtered_context,
            test_id=test_id,
            pt_type=pt_type
        )
        # DEBUG: Prompt finale che viene inviato al modello
        print("🔍 DEBUG - PROMPT FINALE PER L'INTERPRETE:")
        print(f"   Prompt length: {len(prompt)} caratteri")
        print("   Cerca 'last_output' nel prompt:")
        if "last_output" in prompt.lower():
            print("   ✅ 'last_output' menzionato nel prompt")
        else:
            print("   ❌ 'last_output' NON menzionato nel prompt")

        # Mostra una porzione del prompt che dovrebbe contenere il last_output
        print("   Porzione del prompt (caratteri 2000-2500):")
        print(f"   {prompt[2000:2500]}...")
        print("   ---")
        self.logger.log_info("Prompt costruito per UserInputInterpreterLLM", {"prompt": prompt})

        try:
            response = self.llm_client.generate_response(prompt=prompt)
            # DEBUG: Risposta dell'interprete
            print("🔍 DEBUG - RISPOSTA DELL'INTERPRETE:")
            print(f"   Response length: {len(response)} caratteri")
            print(f"   Primi 300 caratteri: {response[:300]}...")
            print("   ---")
            self.logger.log_info(f"La risposta del UserInputInterpreterLLM è: {response}")

            if not response.strip().startswith("{"):
                self.logger.log_error("La risposta non sembra JSON valido", {"response": response})
                return {}

            parsed = self.safe_parse_json(response)
            return parsed

        except Exception as e:
            self.logger.log_error("Errore durante la chiamata o parsing della risposta LLM", {"error": str(e)})
            return {}

    def _build_prompt(self, prompt_template_path: str, user_input: str, current_context: dict, test_id: str,
                      pt_type: str) -> str:
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            template = f.read()

        current_timestamp = datetime.utcnow().isoformat() + "Z"

        params = {
            "{user_input}": user_input,
            "{current_context}": json.dumps(current_context, indent=2),
            "{test_id}": test_id,
            "{pt_type}": pt_type,
            "{current_timestamp}": current_timestamp
        }

        for placeholder, value in params.items():
            template = template.replace(placeholder, value)

        return template
