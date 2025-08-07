# src/llm_interfaces/troubleshooting_llm/troubleshooting_llm.py
"""TroubleshootingLLM
--------------------
Gestisce la generazione di suggerimenti automatici durante la modalità
troubleshooting.

**Fix 2025‑06‑09 – v2**
~~~~~~~~~~~~~~~~~~~~~~
Risolto definitivamente il `KeyError` causato da placeholder con spazi o
newline (es. `{\n  message}`). Ora:
* Normalizziamo tutti i placeholder allʼinterno delle parentesi graffe
  rimuovendo spazi e newline prima della `str.format(...)`.
* Passiamo i parametri `error_message` e `message` per retro‑compatibilità.
* Log esteso nei punti critici.
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from typing import Any, Dict, List

from src.llm_interfaces.clients.gemini_client import GeminiClient

__all__ = ["TroubleshootingLLM"]


class TroubleshootingLLM:  # pylint: disable=too-few-public-methods
    """Interfaccia verso l'LLM per il troubleshooting."""

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------
    def __init__(self, client: GeminiClient, prompt_template_path: str) -> None:
        self.client = client
        if not os.path.exists(prompt_template_path):
            raise FileNotFoundError(
                f"File template prompt per TroubleshootingLLM non trovato: {prompt_template_path}"
            )
        with open(prompt_template_path, "r", encoding="utf-8") as file:
            self.prompt_template: str = file.read()
        print(
            f"[TroubleshootingLLM] Prompt template caricato da: {prompt_template_path}"
        )

    # ------------------------------------------------------------------
    # Helper: normalizza placeholder { message } -> {message}
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_placeholders(template: str) -> str:
        """Rimuove spazi e newline interni alle graffe dei placeholder."""

        def _repl(match: re.Match[str]) -> str:  # type: ignore[type-var]
            key = match.group(1).strip()
            return "{" + key + "}"

        return re.sub(r"{\s*([^{}]+?)\s*}", _repl, template)

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------
    def build_prompt(self, solver_context: Dict[str, Any], history: List[Dict[str, str]] | None) -> str:
        """Costruisce il prompt sostituendo tutti i placeholder richiesti."""

        history_block = ""
        if history:
            history_block = (
                "\nStorico Conversazione (Troubleshooting):\n" +
                "\n".join(
                    f"{i + 1}. {entry.get('role', 'user').capitalize()}: {entry.get('content', '')}"
                    for i, entry in enumerate(history)
                )
            )

        # Normalizza i placeholder prima di format()
        tmpl = self._normalize_placeholders(self.prompt_template)

        return tmpl.format(
            user_input=solver_context.get("user_input", "N/A"),
            command=solver_context.get("command", "N/D"),
            check_id=solver_context.get("check_id", "N/D"),
            error_message=solver_context.get("error_message", "N/A"),
            message=solver_context.get("error_message", "N/A"),  # compatibilità
            history_block=history_block,
        )

    # ------------------------------------------------------------------
    # LLM interaction & parsing
    # ------------------------------------------------------------------
    def get_suggestion(
        self,
        solver_context: Dict[str, Any],
        history: List[Dict[str, str]] | None = None,
    ) -> Dict[str, Any]:
        """Interroga l'LLM e restituisce un dizionario strutturato."""

        prompt = self.build_prompt(solver_context, history or [])
        print("[DEBUG] Prompt Troubleshooting:\n" + prompt)

        # Chiamata al modello
        response_str: str = self.client.generate_response(prompt)
        print("[DEBUG] Raw response:\n" + response_str)

        # Estrai il primo blocco JSON valido
        match = re.search(r"{[\s\S]+?}", response_str.strip())
        if not match:
            raise ValueError("Nessun blocco JSON trovato nella risposta LLM.")

        try:
            llm_reply_dict: Dict[str, Any] = json.loads(match.group())
        except json.JSONDecodeError as exc:
            print("[ERROR] JSONDecodeError nella risposta LLM:", exc)
            raise

        # Validazione minima
        required_fields = {"message", "issue_resolved"}
        missing = required_fields - llm_reply_dict.keys()
        if missing:
            raise KeyError(f"Campi obbligatori mancanti nella risposta LLM: {missing}")

        return llm_reply_dict
