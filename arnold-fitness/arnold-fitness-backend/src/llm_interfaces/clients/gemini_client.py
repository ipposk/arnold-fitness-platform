import os
import google.generativeai as genai
from datetime import datetime


class GeminiClient:
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key per Gemini non trovata. Passarla nel costruttore o impostare GEMINI_API_KEY come variabile d'ambiente."
            )

        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name=self.model_name)

        # Contatori cumulativi per sessione
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self.session_start_time = datetime.utcnow()

        # Contatori per ciclo corrente
        self.cycle_input_tokens = 0
        self.cycle_output_tokens = 0

        # Tracking per tipo di operazione
        self.operation_breakdown = {
            "normal_chat": {"input": 0, "output": 0, "count": 0},
            "skip": {"input": 0, "output": 0, "count": 0},
            "troubleshooting": {"input": 0, "output": 0, "count": 0},
            "error_classification": {"input": 0, "output": 0, "count": 0}
        }

        # Tipo di operazione corrente
        self.current_operation_type = "normal_chat"

    def set_operation_type(self, operation_type: str):
        """Imposta il tipo di operazione corrente per il tracking"""
        if operation_type in self.operation_breakdown:
            self.current_operation_type = operation_type

    def reset_cycle_counters(self):
        """Reset dei contatori del ciclo, ma NON di quelli di sessione"""
        self.cycle_input_tokens = 0
        self.cycle_output_tokens = 0

    def get_token_usage(self) -> dict:
        """
        Ritorna un dizionario completo con:
        - Token del ciclo corrente
        - Token totali della sessione
        - Breakdown per tipo di operazione
        - Costi stimati
        """
        # Prezzi Gemini 1.5 Pro (≤ 128k token)
        input_rate = 1.25 / 1_000_000
        output_rate = 5.00 / 1_000_000

        # Costo del ciclo corrente
        cycle_cost = round(
            self.cycle_input_tokens * input_rate + self.cycle_output_tokens * output_rate, 6
        )

        # Costo totale della sessione
        session_cost = round(
            self.session_input_tokens * input_rate + self.session_output_tokens * output_rate, 4
        )

        # Calcola durata sessione
        session_duration = (datetime.utcnow() - self.session_start_time).total_seconds()

        return {
            # Token del ciclo corrente (per compatibilità)
            "prompt_tokens": self.cycle_input_tokens,
            "completion_tokens": self.cycle_output_tokens,
            "total_tokens": self.cycle_input_tokens + self.cycle_output_tokens,
            "estimated_cost": cycle_cost,

            # NUOVO: Token cumulativi della sessione
            "session_input_tokens": self.session_input_tokens,
            "session_output_tokens": self.session_output_tokens,
            "session_total_tokens": self.session_input_tokens + self.session_output_tokens,
            "session_total_cost_usd": session_cost,

            # NUOVO: Breakdown per operazione
            "operation_breakdown": {
                op_type: {
                    "input_tokens": data["input"],
                    "output_tokens": data["output"],
                    "total_tokens": data["input"] + data["output"],
                    "calls": data["count"],
                    "cost_usd": round(data["input"] * input_rate + data["output"] * output_rate, 6)
                }
                for op_type, data in self.operation_breakdown.items()
                if data["count"] > 0
            },

            # NUOVO: Statistiche sessione
            "session_stats": {
                "duration_seconds": int(session_duration),
                "duration_minutes": round(session_duration / 60, 1),
                "average_tokens_per_minute": round(
                    (self.session_input_tokens + self.session_output_tokens) / max(session_duration / 60, 1), 1),
                "cost_per_minute_usd": round(session_cost / max(session_duration / 60, 1), 4)
            }
        }

    def generate_response(self, prompt: str) -> str:
        """
        Manda un prompt a Gemini 1.5 Pro e aggiorna i token usati.
        Ritorna la risposta testuale.
        """
        response = self.model.generate_content(
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )

        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
            prompt_tokens = getattr(usage, "prompt_token_count", 0)
            candidates_tokens = getattr(usage, "candidates_token_count", 0)

            # Aggiorna contatori del ciclo
            self.cycle_input_tokens += prompt_tokens
            self.cycle_output_tokens += candidates_tokens

            # Aggiorna contatori cumulativi della sessione
            self.session_input_tokens += prompt_tokens
            self.session_output_tokens += candidates_tokens

            # Aggiorna breakdown per tipo di operazione
            if self.current_operation_type in self.operation_breakdown:
                self.operation_breakdown[self.current_operation_type]["input"] += prompt_tokens
                self.operation_breakdown[self.current_operation_type]["output"] += candidates_tokens
                self.operation_breakdown[self.current_operation_type]["count"] += 1

        if hasattr(response, "text"):
            return response.text.strip()
        else:
            raise RuntimeError(f"Errore nella risposta LLM: {response}")