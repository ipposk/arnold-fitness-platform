# File: arnold-fitness-backend/src/orchestrator/orchestrator.py

import json
import os
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from src.logger.logger import Logger
from src.db_context_manager.db_manager import DbContextManager
from src.context_validator.context_validator import ContextValidator
from src.llm_interfaces.user_input_interpreter_llm.user_input_interpreter_llm import UserInputInterpreterLLM
from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM
from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM
from src.llm_interfaces.troubleshooting_llm.troubleshooting_llm import TroubleshootingLLM
from src.llm_interfaces.error_classifier_llm.error_classifier_llm import ErrorClassifierLLM
from src.llm_interfaces.clients.gemini_client import GeminiClient
from src.context_utils.context_filters import filter_current_in_progress_checklist


# ========================================
# UTILITY FUNCTIONS
# ========================================

def merge_context(base_context: dict, updated_fields: dict) -> dict:
    """
    Unisce il contesto base con i campi aggiornati dall'interprete.
    Gestisce findings, evidence e checklist con logica di merge intelligente.
    """
    merged = base_context.copy()

    # Campi semplici da sovrascrivere
    for field in ["meta", "scope", "credentials", "goal", "current_phase_id"]:
        if field in updated_fields:
            merged[field] = updated_fields[field]

    # Merge findings (evita duplicati per finding_id)
    if "findings" in updated_fields:
        merged_findings_ids = {finding["finding_id"] for finding in merged.get("findings", [])}
        for new_finding in updated_fields["findings"]:
            if new_finding["finding_id"] not in merged_findings_ids:
                merged.setdefault("findings", []).append(new_finding)

    # Merge evidence (evita duplicati per evidence_id)
    if "evidence" in updated_fields:
        merged_evidence_ids = {ev["evidence_id"] for ev in merged.get("evidence", [])}
        for new_ev in updated_fields["evidence"]:
            if new_ev["evidence_id"] not in merged_evidence_ids:
                merged.setdefault("evidence", []).append(new_ev)

    # Merge checklist (aggiorna solo check esistenti)
    if "checklist" in updated_fields and isinstance(updated_fields["checklist"], list):
        updated_check_details = {}
        for phase_update in updated_fields.get("checklist", []):
            for task_update in phase_update.get("tasks", []):
                for check_update in task_update.get("checks", []):
                    if "check_id" in check_update:
                        updated_check_details[check_update['check_id']] = check_update

        if updated_check_details:
            for phase in merged.get("checklist", []):
                for task in phase.get("tasks", []):
                    for check in task.get("checks", []):
                        if check['check_id'] in updated_check_details:
                            update_data = updated_check_details[check['check_id']]
                            check['state'] = update_data.get('state', check['state'])
                            check['notes'] = update_data.get('notes', check.get('notes'))
                            check['timestamp'] = update_data.get('timestamp', datetime.utcnow().isoformat() + "Z")
                            if 'related_finding_ids' in update_data:
                                check['related_finding_ids'] = update_data['related_finding_ids']

    return merged


def is_assessment_complete(context: dict) -> bool:
    """
    Verifica se tutti i check ASS-001 a ASS-022 sono completati (state = 'completed').
    Necessario prima di passare ai consigli nutrizionali.
    """
    if "checklist" not in context:
        return False
        
    for phase in context.get("checklist", []):
        if phase.get("phase_id") == "ASS":
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    check_id = check.get("check_id", "")
                    if check_id.startswith("ASS-") and check.get("state") != "completed":
                        print(f"[DEBUG] Assessment incompleto: {check_id} state={check.get('state')}")
                        return False
    
    print("[DEBUG] Assessment ASS-001 a ASS-022 completato!")
    return True


def get_next_assessment_check(context: dict) -> dict:
    """
    Trova il prossimo check ASS-xxx che deve essere completato in sequenza.
    Ritorna il check o None se assessment è completo.
    """
    if "checklist" not in context:
        return None
        
    for phase in context.get("checklist", []):
        if phase.get("phase_id") == "ASS":
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    check_id = check.get("check_id", "")
                    if check_id.startswith("ASS-") and check.get("state") != "completed":
                        print(f"[DEBUG] Prossimo assessment check: {check_id}")
                        return {
                            "check_id": check_id,
                            "description": check.get("description"),
                            "task_title": task.get("title"),
                            "phase_id": phase.get("phase_id")
                        }
    
    return None


def should_block_nutrition_advice(context: dict) -> bool:
    """
    Determina se i consigli nutrizionali devono essere bloccati.
    True = blocca (assessment incompleto), False = permetti.
    """
    assessment_complete = is_assessment_complete(context)
    
    if not assessment_complete:
        print("[DEBUG] BLOCCANDO consigli nutrizionali - assessment incompleto")
        return True
    else:
        print("[DEBUG] PERMETTENDO consigli nutrizionali - assessment completo")
        return False


def format_suggested_actions_to_markdown(suggested_actions: list, intro: str = None, outro: str = None) -> str:
    """
    Converte le azioni suggerite dall'LLM in formato markdown strutturato.
    Raggruppa le azioni per task/check e formatta con numerazione e comandi.
    """
    grouped = defaultdict(list)

    if isinstance(suggested_actions, list):
        for action_group in suggested_actions:
            if isinstance(action_group,
                          dict) and "actions" in action_group and "task_id" in action_group and "check_id" in action_group:
                key = f"{action_group.get('task_id', 'N/A')} / {action_group.get('check_id', 'N/A')}"
                if isinstance(action_group["actions"], list):
                    grouped[key].extend(action_group["actions"])
            else:
                print(f"[format_suggested_actions_to_markdown] WARN: Ignorato action_group malformato: {action_group}")

    md_lines = ["## 📌 Suggerimenti LLM\n"]
    if intro:
        md_lines.append(f"> {intro}\n")

    if not grouped:
        md_lines.append("Nessuna azione specifica suggerita al momento.\n")
    else:
        for idx, (key, actions_list) in enumerate(grouped.items(), start=1):
            md_lines.append(f"### {idx}. Task: `{key}`\n")
            if isinstance(actions_list, list) and actions_list:
                for i, step in enumerate(actions_list, start=1):
                    if isinstance(step, dict):
                        description = step.get('description', 'Azione non descritta')
                        command = step.get('command', 'Nessun comando specifico')
                        md_lines.append(f"{i}. {description}")
                        md_lines.append(f"   Comando: ✅ `{command}`")
                    else:
                        md_lines.append(f"{i}. Azione malformata: {step}")
                md_lines.append("")
            else:
                md_lines.append("  Nessuna sotto-azione dettagliata per questo task.\n")

    if outro:
        md_lines.append(f"> {outro}\n")

    return "\n".join(md_lines)


# ========================================
# MAIN ORCHESTRATOR CLASS
# ========================================

class Orchestrator:
    """
    Orchestratore principale del sistema RAG per coaching fitness.
    Coordina il flusso tra interpretazione input, generazione query,
    retrieval semantico e creazione guidance personalizzata.
    """

    def __init__(self,
                 db_manager: DbContextManager,
                 validator: ContextValidator,
                 interpreter: UserInputInterpreterLLM,
                 query_generator_llm: QueryGeneratorLLM,
                 task_guidance_llm: TaskGuidanceLLM,
                 troubleshooter_llm: TroubleshootingLLM,
                 error_classifier_llm: ErrorClassifierLLM,
                 client: GeminiClient):
        self.db_manager = db_manager
        self.validator = validator
        self.interpreter = interpreter
        self.query_generator_llm = query_generator_llm
        self.task_guidance_llm = task_guidance_llm
        self.troubleshooter_llm = troubleshooter_llm
        self.error_classifier_llm = error_classifier_llm
        self.client = client
        self.logger = Logger("Orchestrator")

    # ========================================
    # DEBUG UTILITIES
    # ========================================

    def _debug_database_context(self, current_context: dict, test_id: str) -> None:
        """Debug: Verifica contenuto recuperato dal database."""
        print("🔍 DEBUG - CONTESTO RECUPERATO DAL DATABASE:")
        if current_context and "last_output" in current_context:
            last_output = current_context["last_output"]
            print(f"   Last output trovato!")
            print(f"   Guidance markdown length: {len(last_output.get('guidance_markdown', ''))}")
            print(f"   Primi 200 caratteri: {last_output.get('guidance_markdown', '')[:200]}...")
            print(f"   Raw guidance presente: {'raw_guidance' in last_output}")
        else:
            print("   ❌ PROBLEMA: Last output NON trovato nel contesto!")
        print("   ---")

    def _debug_error_classification(self, user_input: str, is_error_result: bool) -> None:
        """Debug: Traccia il processo di classificazione errori."""
        print("🔍 DEBUG - ROUTING TROUBLESHOOTING:")
        print(f"   User input per error classifier: '{user_input}'")
        print(f"   Error classifier result: {is_error_result}")
        print(f"   Tipo del risultato: {type(is_error_result)}")

        if is_error_result:
            print("   ✅ DOVREBBE ENTRARE IN TROUBLESHOOTING MODE")
        else:
            print("   ✅ FLUSSO NORMALE - NO TROUBLESHOOTING")
        print("   ---")

    def _debug_solver_context(self, solver_context: dict) -> None:
        """Debug: Mostra il contesto preparato per il troubleshooter."""
        print("🔍 DEBUG - SOLVER CONTEXT PREPARATO:")
        for key, value in solver_context.items():
            print(f"   {key}: {value}")
        print("   ---")

    def _debug_output_saving(self, markdown_guidance: str, guidance_dict: dict) -> None:
        """Debug: Verifica contenuto dell'ultimo output prima del salvataggio."""
        print("🔍 DEBUG - ULTIMO OUTPUT CHE VIENE SALVATO:")
        print(f"   Markdown length: {len(markdown_guidance)} caratteri")
        print(f"   Primi 200 caratteri: {markdown_guidance[:200]}...")
        print(f"   Raw guidance keys: {guidance_dict.keys() if guidance_dict else 'None'}")
        print("   ---")

    # ========================================
    # TROUBLESHOOTING LOGIC
    # ========================================

    def _extract_solver_context_from_last_output(self, user_input: str, current_context: dict) -> dict:
        """
        Estrae informazioni dall'ultimo output per creare un solver_context ricco.
        """
        solver_context = {
            "user_input": user_input,
            "error_message": user_input,
            "command": "",  # Stringa vuota invece di "N/D"
            "check_id": "",  # Stringa vuota invece di "N/D"
            "test_id": current_context.get("test_id", "")  # IMPORTANTE: aggiungi il test_id
        }

        print(f"[DEBUG] Extract solver context per: '{user_input}'")

        # Estrai informazioni dall'ultimo output se disponibile
        if current_context and "last_output" in current_context:
            last_output = current_context["last_output"]
            raw_guidance = last_output.get("raw_guidance", {})

            print(f"[DEBUG] Raw guidance keys: {raw_guidance.keys()}")

            # Cerca comandi correlati nell'ultimo output
            suggested_actions = raw_guidance.get("suggested_actions", [])
            print(f"[DEBUG] Numero di action groups: {len(suggested_actions)}")

            for action_group in suggested_actions:
                check_id = action_group.get("check_id", "")

                for action in action_group.get("actions", []):
                    command = action.get("command", "")
                    description = action.get("description", "")

                    print(f"[DEBUG] Analizzando: cmd='{command[:50]}...', desc='{description[:50]}...'")

                    # Cerca "shodan" in modo più flessibile
                    user_input_lower = user_input.lower()
                    if "shodan" in user_input_lower:
                        if "shodan" in command.lower() or "shodan" in description.lower():
                            solver_context["command"] = command
                            solver_context["check_id"] = check_id
                            solver_context["description"] = description
                            print(f"[DEBUG] ✅ Trovata correlazione Shodan!")
                            return solver_context  # Esci appena trovi una corrispondenza

        print(f"[DEBUG] Solver context finale: {solver_context}")
        return solver_context

    def run_troubleshooter_loop(self, solver_context: dict, history: list) -> dict:
        test_id = solver_context.get("test_id")
        if not test_id:
            self.logger.log_error("test_id mancante nel solver_context")
            return {}

        current_context = self.db_manager.get_current(test_id)

        try:
            llm_reply_dict = self.troubleshooter_llm.get_suggestion(solver_context, history)
            print(f"[DEBUG] Troubleshooter response: {json.dumps(llm_reply_dict, indent=2)}")

            # Se risolto, rilancia
            if llm_reply_dict.get("issue_resolved") is True and "final_user_input" in llm_reply_dict:
                print("[DEBUG] ✅ Problema risolto, rientro nel flusso principale")
                return self.process_single_input(test_id, llm_reply_dict["final_user_input"])

            # NUOVO: Se NON risolto ma c'è un messaggio, MOSTRALO ALL'UTENTE
            elif "message" in llm_reply_dict:
                print(f"[DEBUG] 💡 Assistenza troubleshooting attiva")

                # Crea una guidance speciale per il troubleshooting
                troubleshooting_guidance = {
                    "intro": "Assistenza Tecnica Attiva",
                    "suggested_actions": [{
                        "task_id": "TROUBLESHOOT",
                        "check_id": solver_context.get("check_id", "HELP"),
                        "phase_id": "SUPPORT",
                        "title": "Risoluzione Problema Shodan",
                        "actions": [{
                            "action_id": "HELP-01",
                            "description": llm_reply_dict.get("message", "Segui le istruzioni"),
                            "command": "Segui i passaggi sopra indicati"
                        }]
                    }],
                    "outro": "Dopo aver seguito questi passaggi, comunicami se funziona o se hai ancora problemi."
                }

                # Formatta in markdown
                markdown_guidance = f"""## Assistenza Troubleshooting

    {llm_reply_dict.get("message", "Nessun messaggio di aiuto disponibile")}

    **Problema originale:** {solver_context.get("error_message", "N/A")}
    **Comando correlato:** `{solver_context.get("command", "N/A")}`

    Rispondi indicando se hai risolto o se hai bisogno di ulteriore assistenza."""

                # Aggiorna il context con la guidance di troubleshooting
                current_context["last_output"] = {
                    "guidance_markdown": markdown_guidance,
                    "raw_guidance": troubleshooting_guidance
                }

                # Salva e ritorna il context aggiornato
                self.db_manager.update_context_and_version(test_id, current_context)
                return current_context

            else:
                print("[DEBUG] ❌ Risposta troubleshooter non valida o vuota")
                return current_context

        except Exception as e:
            print(f"[ERROR] Errore in troubleshooting: {str(e)}")
            import traceback
            traceback.print_exc()
            return current_context

    # ========================================
    # MAIN PROCESSING METHOD
    # ========================================

    def process_single_input(self, test_id: str, user_input: str) -> dict:
        """
        Processa un singolo input utente attraverso il pipeline completo.
        """
        self.logger.log_info(f"Orchestrator: Inizio process_single_input per test_id: {test_id}",
                             {"user_input_snippet": user_input[:100]})

        current_context = self.db_manager.get_current(test_id)
        self._debug_database_context(current_context, test_id)

        if not current_context:
            self.logger.log_error(f"Contesto non trovato per test_id: {test_id} in process_single_input")
            raise ValueError(f"Contesto non trovato per test_id: {test_id}. Impossibile processare l'input.")

        # NUOVO: Carica i contatori di token dal context
        self._load_token_counters_from_context(current_context)

        # Reset contatori del ciclo (NON della sessione)
        if hasattr(self.client, 'reset_cycle_counters'):
            self.client.reset_cycle_counters()

        pt_type = current_context.get("pt_type", "Unknown")

        # ===== GESTIONE SKIP =====
        if user_input.strip().lower() == "skip":
            # NUOVO: Imposta tipo operazione
            if hasattr(self.client, 'set_operation_type'):
                self.client.set_operation_type("skip")

            skip_result = self._handle_skip_command(test_id, current_context)
            if skip_result:
                # NUOVO: Salva i contatori prima di salvare
                self._save_token_counters_to_context(skip_result)

                # Salva immediatamente il context skippato
                self.db_manager.update_context_and_version(test_id, skip_result)

                # Genera guidance per il nuovo check attivo
                filtered_ctx = filter_current_in_progress_checklist(skip_result)
                query_data = self.query_generator_llm.generate_query(filtered_ctx) or {}
                guidance_json_str = self.task_guidance_llm.generate_guidance(filtered_ctx, query_data)

                try:
                    guidance_dict = json.loads(guidance_json_str)
                except:
                    guidance_dict = {
                        "intro": "Check skippato, procedi con il prossimo.",
                        "suggested_actions": [],
                        "outro": "Continua con il test."
                    }

                markdown_guidance = format_suggested_actions_to_markdown(
                    guidance_dict.get("suggested_actions", []),
                    intro=guidance_dict.get("intro"),
                    outro=guidance_dict.get("outro")
                )

                skip_result["last_output"] = {
                    "guidance_markdown": markdown_guidance,
                    "raw_guidance": guidance_dict
                }

                self.db_manager.update_context_and_version(test_id, skip_result)
                self._save_token_counters_to_context(skip_result)
                self.db_manager.update_context_and_version(test_id, skip_result)

                if hasattr(self.client, 'get_token_usage'):
                    skip_result["token_usage"] = self.client.get_token_usage()

                return skip_result
            else:
                print("[DEBUG] Nessun check da skippare, continuo normalmente")

        try:
            # === 2. Classificazione errore e troubleshooting ===
            # NUOVO: Imposta tipo operazione per error classification
            if hasattr(self.client, 'set_operation_type'):
                self.client.set_operation_type("error_classification")

            is_error_result = self.error_classifier_llm.is_error(user_input)
            self._debug_error_classification(user_input, is_error_result)

            if is_error_result:
                # NUOVO: Imposta tipo operazione per troubleshooting
                if hasattr(self.client, 'set_operation_type'):
                    self.client.set_operation_type("troubleshooting")

                self.logger.log_info(
                    f"Input classificato come errore tecnico per test_id: {test_id}. Avvio troubleshooting.",
                    {"user_input": user_input})

                solver_context = self._extract_solver_context_from_last_output(user_input, current_context)
                solver_context["test_id"] = test_id
                self._debug_solver_context(solver_context)

                print("[TROUBLESHOOTER] CHIAMANDO TROUBLESHOOTER...")

                history = []
                result = self.run_troubleshooter_loop(solver_context, history)

                if isinstance(result, str):
                    print(f"[DEBUG] ✅ Input risolto via troubleshooting: {result}")
                    user_input = result
                elif isinstance(result, dict):
                    print("[DEBUG] 📋 Troubleshooter ha fornito assistenza")
                    # NUOVO: Salva i contatori nel result
                    self._save_token_counters_to_context(result)
                    if hasattr(self.client, 'get_token_usage'):
                        result["token_usage"] = self.client.get_token_usage()
                    return result
                else:
                    print("[DEBUG] ❌ Risposta troubleshooter non valida")
                    return current_context

            # === 3. CHAT NORMALE ===
            # NUOVO: Imposta tipo operazione per chat normale
            if hasattr(self.client, 'set_operation_type'):
                self.client.set_operation_type("normal_chat")

            # === 3. Interpretazione input e aggiornamento contesto ===
            self.logger.log_info(f"Invio all'interprete per test_id: {test_id}",
                                 {"user_input_to_interpreter": user_input[:100]})

            llm_interpreted_update = self.interpreter.process_input(
                user_input=user_input,
                current_context=current_context,
                test_id=test_id,
                pt_type=pt_type
            )

            if not llm_interpreted_update:
                self.logger.log_error("UserInputInterpreterLLM non ha prodotto output.", {"test_id": test_id})
                raise ValueError("Interpretazione input fallita")

            if not self.validator.validate(llm_interpreted_update):
                self.logger.log_error("Output dell'Interpreter LLM non valido.",
                                      {"test_id": test_id,
                                       "output_snippet": json.dumps(llm_interpreted_update)[:200]})
                raise ValueError("Output interpretato non valido")

            updated_context = merge_context(current_context, llm_interpreted_update)

            # === 4. Generazione query semantica ===
            filtered_ctx = filter_current_in_progress_checklist(updated_context)
            query_data = self.query_generator_llm.generate_query(filtered_ctx) or {}

            # === 5. Generazione GUIDANCE con controllo assessment ===
            
            # Verifica se l'assessment è completo prima di generare guidance nutrizionale
            block_nutrition = should_block_nutrition_advice(updated_context)
            next_assessment_check = get_next_assessment_check(updated_context)
            
            # Aggiungi info di controllo al contesto per il TaskGuidanceLLM
            guidance_context = filtered_ctx.copy()
            guidance_context["assessment_status"] = {
                "is_complete": is_assessment_complete(updated_context),
                "block_nutrition_advice": block_nutrition,
                "next_check": next_assessment_check
            }
            
            guidance_json_str = self.task_guidance_llm.generate_guidance(guidance_context, query_data)

            if not guidance_json_str:
                self.logger.log_error("TaskGuidanceLLM non ha prodotto output.", {"test_id": test_id})
                raise ValueError("Generazione guida fallita")

            try:
                try:
                    guidance_dict = json.loads(guidance_json_str)
                except json.JSONDecodeError:
                    print(f"[DEBUG] Primo parsing fallito, provo pulizia JSON...")

                    cleaned = guidance_json_str
                    if "}}" in cleaned:
                        cleaned = cleaned[:cleaned.rfind("}}") + 2]
                    elif "}" in cleaned:
                        cleaned = cleaned[:cleaned.rfind("}") + 1]

                    cleaned = cleaned.replace("'", "'").replace(""", '"').replace(""", '"')
                    guidance_dict = json.loads(cleaned)

                required_keys = {"intro", "suggested_actions", "outro"}
                if not (isinstance(guidance_dict, dict) and required_keys.issubset(guidance_dict)):
                    self.logger.log_error("Output JSON malformato o chiavi mancanti.",
                                          {"test_id": test_id, "guidance_snippet": guidance_json_str[:200]})
                    raise ValueError("Chiavi 'intro', 'suggested_actions', 'outro' mancanti")

            except json.JSONDecodeError as jde:
                print(f"[DEBUG] JSON problematico (ultimi 200 char): ...{guidance_json_str[-200:]}")
                self.logger.log_error(f"Guidance non valida: {jde}",
                                      {"test_id": test_id, "guidance_received": guidance_json_str})

                fallback_guidance = {
                    "intro": "Si e' verificato un problema nel parsing della guidance.",
                    "suggested_actions": [{
                        "task_id": "UNKNOWN",
                        "check_id": "UNKNOWN",
                        "phase_id": "UNKNOWN",
                        "title": "Fallback",
                        "actions": [{
                            "action_id": "FALLBACK-01",
                            "description": "Verifica manuale richiesta",
                            "command": "Controlla la validita' della risposta LLM o rilancia il task"
                        }]
                    }],
                    "outro": "Riprova oppure contatta il supporto se il problema persiste."
                }
                guidance_dict = fallback_guidance

                # === Markdown e salvataggio ===
            markdown_guidance = format_suggested_actions_to_markdown(
                guidance_dict.get("suggested_actions", []),
                intro=guidance_dict.get("intro"),
                outro=guidance_dict.get("outro")
            )

            self.logger.log_info(f"Uso token Gemini per test_id {test_id} in questo ciclo",
                                 self.client.get_token_usage())

            final_context_to_save = updated_context
            final_context_to_save["last_output"] = {
                "guidance_markdown": markdown_guidance,
                "raw_guidance": guidance_dict
            }
            # NUOVO: Salva i contatori di token nel context
            self._save_token_counters_to_context(final_context_to_save)
            self._debug_output_saving(markdown_guidance, guidance_dict)

            if self.db_manager.update_context_and_version(test_id, final_context_to_save):
                self.logger.log_info(f"Contesto aggiornato e salvato per test_id: {test_id}")
                return final_context_to_save
            else:
                self.logger.log_error(f"Fallimento salvataggio per test_id: {test_id}")
                raise ValueError("Salvataggio contesto fallito")

        except Exception as e:
            self.logger.log_error(f"Eccezione catturata in process_single_input per test_id: {test_id}",
                                  {"error": str(e), "trace": traceback.format_exc()})
            raise

    def _load_token_counters_from_context(self, context: dict):
        """Carica i contatori di token dal context salvato"""
        if hasattr(self.client, 'session_input_tokens'):
            token_data = context.get('_token_tracking', {})
            self.client.session_input_tokens = token_data.get('session_input_tokens', 0)
            self.client.session_output_tokens = token_data.get('session_output_tokens', 0)
            self.client.session_start_time = datetime.fromisoformat(
                token_data.get('session_start_time', datetime.utcnow().isoformat())
            )
            self.client.operation_breakdown = token_data.get('operation_breakdown', {
                "normal_chat": {"input": 0, "output": 0, "count": 0},
                "skip": {"input": 0, "output": 0, "count": 0},
                "troubleshooting": {"input": 0, "output": 0, "count": 0},
                "error_classification": {"input": 0, "output": 0, "count": 0}
            })

    def _save_token_counters_to_context(self, context: dict):
        """Salva i contatori di token nel context"""
        if hasattr(self.client, 'session_input_tokens'):
            context['_token_tracking'] = {
                'session_input_tokens': self.client.session_input_tokens,
                'session_output_tokens': self.client.session_output_tokens,
                'session_start_time': self.client.session_start_time.isoformat(),
                'operation_breakdown': self.client.operation_breakdown
            }

    def _handle_skip_command(self, test_id: str, current_context: dict) -> dict:
        """
        Gestisce il comando 'skip': marca il check corrente come done e attiva il successivo.
        Ritorna il context aggiornato o None se non c'è nulla da skippare.
        """
        print("[DEBUG] 🎯 Comando SKIP rilevato")

        # Trova il check attualmente in_progress
        current_check_info = None
        for phase_idx, phase in enumerate(current_context.get("checklist", [])):
            for task_idx, task in enumerate(phase.get("tasks", [])):
                for check_idx, check in enumerate(task.get("checks", [])):
                    if check.get("state") == "in_progress":
                        current_check_info = {
                            "phase_idx": phase_idx,
                            "task_idx": task_idx,
                            "check_idx": check_idx,
                            "check": check,
                            "phase": phase,
                            "task": task
                        }
                        break
                if current_check_info:
                    break
            if current_check_info:
                break

        if not current_check_info:
            print("[DEBUG] ⚠️ Nessun check in_progress da skippare")
            return None

        # Marca il check corrente come done
        info = current_check_info
        checklist = current_context["checklist"]
        current_check = checklist[info["phase_idx"]]["tasks"][info["task_idx"]]["checks"][info["check_idx"]]

        current_check["state"] = "done"
        existing_notes = current_check.get("notes") or ""
        current_check["notes"] = (existing_notes + " | SKIPPED via comando skip").strip(" |")
        current_check["timestamp"] = datetime.utcnow().isoformat() + "Z"

        print(f"[DEBUG] ✅ Check {current_check['check_id']} marcato come done")

        # Trova il prossimo check pending a partire dal punto successivo
        next_check_found = False
        checklist_len = len(checklist)

        for phase_idx in range(info["phase_idx"], checklist_len):
            phase = checklist[phase_idx]
            task_start = info["task_idx"] if phase_idx == info["phase_idx"] else 0

            for task_idx in range(task_start, len(phase.get("tasks", []))):
                task = phase["tasks"][task_idx]
                check_start = info["check_idx"] + 1 if (
                        phase_idx == info["phase_idx"] and task_idx == info["task_idx"]) else 0

                for check_idx in range(check_start, len(task.get("checks", []))):
                    check = task["checks"][check_idx]
                    if check.get("state") == "pending":
                        check["state"] = "in_progress"
                        check["timestamp"] = datetime.utcnow().isoformat() + "Z"
                        print(f"[DEBUG] 🟢 Nuovo check attivo: {check['check_id']}")
                        next_check_found = True
                        break
                if next_check_found:
                    break
            if next_check_found:
                break

        if not next_check_found:
            print("[DEBUG] ℹ️ Nessun check pending trovato. Checklist completata?")

        # IMPORTANTE: NON impostare last_output qui!
        # Restituisci solo il context aggiornato
        return current_context