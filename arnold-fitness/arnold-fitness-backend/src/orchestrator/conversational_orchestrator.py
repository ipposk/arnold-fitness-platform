"""
Conversational Orchestrator - Enhanced orchestrator con sistema conversazionale personalizzato
"""

import json
import os
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Import esistenti
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

# Import nuovi componenti conversazionali
from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter
from src.conversation_director import QuestionSelector, FlowManager, ContextBridge
from src.adaptive_prompting import PromptPersonalizer, ToneAdjuster, QuestionGenerator

# Import utilities esistenti
from .orchestrator import merge_context, merge_checklist_state, calculate_total_tokens, setup_and_run_orchestrator

# Import enhanced interfaces
from src.llm_interfaces.enhanced_llm_interfaces import create_enhanced_llm_interfaces


class ConversationalOrchestrator:
    """
    Enhanced orchestrator che integra il sistema conversazionale personalizzato
    con l'architettura esistente di Arnold.
    """
    
    def __init__(self, session_id: str, db_manager: DbContextManager):
        self.session_id = session_id
        self.db_manager = db_manager
        self.logger = Logger()
        
        # Componenti esistenti
        self.context_validator = ContextValidator()
        
        # Inizializza componenti LLM (temporaneamente semplificato per il test)
        # TODO: Integrare correttamente con i parametri necessari
        try:
            # Per ora usa fallback a processing standard se gli LLM enhanced falliscono
            self.user_input_interpreter = UserInputInterpreterLLM()
            self.query_generator = QueryGeneratorLLM() 
            self.task_guidance = TaskGuidanceLLM()
            
            self.troubleshooting = TroubleshootingLLM()
            self.error_classifier = ErrorClassifierLLM()
            
        except Exception as e:
            self.logger.warning(f"[INIT] Could not initialize LLM components: {e}")
            # Inizializzazione semplificata per testing
            self.user_input_interpreter = None
            self.query_generator = None
            self.task_guidance = None
            self.troubleshooting = None
            self.error_classifier = None
        
        # Nuovi componenti conversazionali
        self.style_analyzer = StyleAnalyzer()
        self.personality_mapper = PersonalityMapper()
        self.empathy_adapter = EmpathyAdapter()
        self.question_selector = QuestionSelector()
        self.flow_manager = FlowManager()
        self.context_bridge = ContextBridge()
        self.prompt_personalizer = PromptPersonalizer()
        self.tone_adjuster = ToneAdjuster()
        self.question_generator = QuestionGenerator()
        
        # Stato conversazionale
        self.conversation_history = []
        self.current_personality_profile = None
        self.current_writing_style = None
        self.last_conversation_state = None
        
        # Token tracking
        self.token_stats = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "operation_breakdown": defaultdict(lambda: {"tokens": 0, "calls": 0, "cost_usd": 0.0})
        }
    
    def process_conversational_input(self, user_input: str) -> Dict[str, Any]:
        """
        Processa l'input utente usando il nuovo sistema conversazionale personalizzato
        """
        
        try:
            self.logger.info(f"[CONVERSATIONAL] Processing input for session {self.session_id}")
            
            # Step 1: Analizza e aggiorna il profilo dell'utente
            personality_profile, writing_style = self._analyze_and_update_user_profile(user_input)
            
            # Step 2: Ottieni il contesto attuale
            current_context = self.db_manager.get_context(self.session_id)
            
            # Step 3: Aggiorna la storia conversazionale
            self._update_conversation_history(user_input)
            
            # Step 4: Determina il prossimo step conversazionale
            conversational_step = self.context_bridge.get_next_conversational_step(
                current_context,
                self.conversation_history,
                personality_profile,
                writing_style
            )
            
            # Step 5: Processa l'input usando l'approccio personalizzato
            result = self._process_with_personalization(
                user_input,
                current_context,
                personality_profile,
                writing_style,
                conversational_step
            )
            
            # Step 6: Aggiorna il contesto con le nuove informazioni
            updated_context = self._update_context_conversationally(
                current_context,
                user_input,
                result,
                personality_profile,
                writing_style
            )
            
            # Step 7: Salva il contesto aggiornato
            self.db_manager.update_context(self.session_id, updated_context)
            
            # Step 8: Aggiorna token stats
            self._update_token_stats(result.get("token_usage", {}))
            
            self.logger.info("[CONVERSATIONAL] Processing completed successfully")
            
            return {
                **result,
                "conversation_insights": conversational_step,
                "personality_profile": personality_profile.to_dict(),
                "writing_style": writing_style.to_dict(),
                "conversation_state": conversational_step.get("conversation_state").__dict__ if conversational_step.get("conversation_state") else None
            }
            
        except Exception as e:
            self.logger.error(f"[CONVERSATIONAL] Error processing input: {str(e)}")
            self.logger.error(f"[CONVERSATIONAL] Traceback: {traceback.format_exc()}")
            
            # Fallback al sistema originale
            return self._fallback_to_original_processing(user_input)
    
    def _analyze_and_update_user_profile(self, user_input: str) -> Tuple[Any, Any]:
        """Analizza e aggiorna il profilo psicologico dell'utente"""
        
        try:
            # Analizza lo stile di scrittura attuale
            writing_style = self.style_analyzer.analyze_text(user_input)
            
            # Se abbiamo una storia conversazionale, usa quella per un'analisi più accurata
            if len(self.conversation_history) > 1:
                user_messages = [msg.get("user", "") for msg in self.conversation_history[-5:]]  # Ultimi 5
                user_messages.append(user_input)
                writing_style = self.style_analyzer.analyze_conversation_history(user_messages)
            
            # Mappa lo stile a un profilo psicologico
            personality_profile = self.personality_mapper.map_style_to_personality(writing_style)
            
            # Aggiorna i profili correnti
            self.current_personality_profile = personality_profile
            self.current_writing_style = writing_style
            
            self.logger.info(f"[PROFILE] Updated profile: {personality_profile.primary_type}, style: {writing_style.emotional_tone}")
            
            return personality_profile, writing_style
            
        except Exception as e:
            self.logger.error(f"[PROFILE] Error analyzing user profile: {str(e)}")
            
            # Fallback a profili default
            from src.personality_profiler.style_analyzer import WritingStyle
            from src.personality_profiler.personality_mapper import PersonalityProfile
            
            default_style = WritingStyle(
                verbosity="moderate", emotional_tone="neutral", formality="semi_formal",
                technical_level="basic", openness="moderate", energy_level="moderate", concern_level="moderate"
            )
            default_profile = PersonalityProfile(
                primary_type="practical", communication_preference="encouraging",
                motivation_style="autonomy", support_needs="moderate", information_processing="step_by_step"
            )
            
            return default_profile, default_style
    
    def _update_conversation_history(self, user_input: str):
        """Aggiorna la storia conversazionale"""
        
        # Mantieni solo gli ultimi 20 scambi per gestione memoria
        if len(self.conversation_history) >= 20:
            self.conversation_history = self.conversation_history[-19:]
        
        # Aggiungi il nuovo input (la risposta verrà aggiunta dopo)
        self.conversation_history.append({
            "user": user_input,
            "timestamp": datetime.now().isoformat(),
            "arnold": None  # Verrà popolato dopo la generazione
        })
    
    def _process_with_personalization(self,
                                    user_input: str,
                                    context: Dict[str, Any],
                                    personality_profile: Any,
                                    writing_style: Any,
                                    conversational_step: Dict[str, Any]) -> Dict[str, Any]:
        """Processa l'input utilizzando la personalizzazione"""
        
        results = {
            "token_usage": defaultdict(int),
            "operation_results": {}
        }
        
        try:
            # Step 1: Interpreta l'input con personalizzazione
            interpretation_result = self._personalized_input_interpretation(
                user_input, context, personality_profile, writing_style
            )
            results["operation_results"]["interpretation"] = interpretation_result
            results["token_usage"]["interpretation"] = interpretation_result.get("token_usage", {})
            
            # Step 2: Genera query personalizzate se necessario
            if self._should_generate_queries(interpretation_result, conversational_step):
                query_result = self._personalized_query_generation(
                    user_input, personality_profile, context
                )
                results["operation_results"]["query_generation"] = query_result
                results["token_usage"]["query_generation"] = query_result.get("token_usage", {})
            
            # Step 3: Genera guidance personalizzata
            guidance_result = self._personalized_guidance_generation(
                user_input,
                context,
                personality_profile,
                writing_style,
                conversational_step,
                interpretation_result
            )
            results["operation_results"]["guidance"] = guidance_result
            results["token_usage"]["guidance"] = guidance_result.get("token_usage", {})
            
            # Step 4: Prepara output finale
            final_guidance = guidance_result.get("guidance_markdown", "")
            
            # Step 5: Aggiusta il tono finale
            adjusted_guidance = self.tone_adjuster.adjust_response_tone(
                final_guidance,
                personality_profile,
                writing_style,
                conversational_step.get("conversation_state"),
                conversational_step.get("context_insights", {})
            )
            
            results["last_output"] = {
                "guidance_markdown": adjusted_guidance,
                "operation_type": "conversational_guidance",
                "personalization_applied": True
            }
            
            # Aggiorna la storia conversazionale con la risposta
            if self.conversation_history:
                self.conversation_history[-1]["arnold"] = adjusted_guidance
            
            return results
            
        except Exception as e:
            self.logger.error(f"[PERSONALIZATION] Error in personalized processing: {str(e)}")
            
            # Fallback a guidance standard
            return self._generate_fallback_guidance(user_input, context, personality_profile)
    
    def _personalized_input_interpretation(self,
                                         user_input: str,
                                         context: Dict[str, Any],
                                         personality_profile: Any,
                                         writing_style: Any) -> Dict[str, Any]:
        """Interpreta l'input con personalizzazione"""
        
        try:
            # Personalizza il prompt per l'interpretazione
            base_prompt = self.user_input_interpreter.get_base_prompt()
            personalized_prompt = self.prompt_personalizer.personalize_context_update_prompt(
                base_prompt,
                user_input,
                personality_profile,
                writing_style,
                context
            )
            
            # Esegui l'interpretazione con prompt personalizzato
            result = self.user_input_interpreter.process_with_custom_prompt(
                personalized_prompt,
                user_input,
                context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"[INTERPRETATION] Error in personalized interpretation: {str(e)}")
            
            # Fallback al metodo originale
            return self.user_input_interpreter.update_context_with_observation(user_input, context)
    
    def _personalized_query_generation(self,
                                     user_input: str,
                                     personality_profile: Any,
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera query personalizzate per la ricerca"""
        
        try:
            base_prompt = self.query_generator.get_base_prompt()
            personalized_prompt = self.prompt_personalizer.personalize_query_generation_prompt(
                base_prompt,
                user_input,
                personality_profile,
                context
            )
            
            result = self.query_generator.process_with_custom_prompt(
                personalized_prompt,
                user_input,
                context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"[QUERY_GEN] Error in personalized query generation: {str(e)}")
            
            # Fallback al metodo originale
            return self.query_generator.generate_search_queries(user_input, context)
    
    def _personalized_guidance_generation(self,
                                        user_input: str,
                                        context: Dict[str, Any],
                                        personality_profile: Any,
                                        writing_style: Any,
                                        conversational_step: Dict[str, Any],
                                        interpretation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera guidance personalizzata"""
        
        try:
            # Determina se usare una domanda conversazionale o guidance standard
            next_question = conversational_step.get("next_question")
            conversation_state = conversational_step.get("conversation_state")
            
            if next_question and self._should_use_conversational_question(conversation_state, context):
                # Genera una domanda conversazionale personalizzata
                personalized_question = self.question_generator.generate_question(
                    next_question,
                    personality_profile,
                    writing_style,
                    conversation_state
                )
                
                return {
                    "guidance_markdown": personalized_question,
                    "guidance_type": "conversational_question",
                    "token_usage": {"prompt_tokens": 0, "completion_tokens": len(personalized_question.split())}
                }
            else:
                # Genera guidance personalizzata standard
                base_prompt = self.task_guidance.get_base_prompt()
                personalized_prompt = self.prompt_personalizer.personalize_guidance_prompt(
                    base_prompt,
                    user_input,
                    personality_profile,
                    writing_style,
                    conversation_state,
                    context
                )
                
                result = self.task_guidance.process_with_custom_prompt(
                    personalized_prompt,
                    user_input,
                    context
                )
                
                return result
            
        except Exception as e:
            self.logger.error(f"[GUIDANCE] Error in personalized guidance generation: {str(e)}")
            
            # Fallback al metodo originale
            return self.task_guidance.generate_task_guidance(user_input, context)
    
    def _should_generate_queries(self, interpretation_result: Dict[str, Any], conversational_step: Dict[str, Any]) -> bool:
        """Determina se generare query di ricerca"""
        
        # Non generare query nelle fasi iniziali (warmup, profiling)
        conversation_state = conversational_step.get("conversation_state")
        if conversation_state and conversation_state.phase.value in ["warmup", "profiling"]:
            return False
        
        # Genera query se l'interpretazione ha identificato bisogni informativi
        context_updates = interpretation_result.get("context_updates", {})
        needs_research = any(
            "research" in str(update).lower() or "information" in str(update).lower()
            for update in context_updates.values()
        )
        
        return needs_research
    
    def _should_use_conversational_question(self, conversation_state: Any, context: Dict[str, Any]) -> bool:
        """Determina se usare una domanda conversazionale invece di guidance standard"""
        
        if not conversation_state:
            return True
        
        # Usa domande conversazionali nelle fasi iniziali
        if conversation_state.phase.value in ["warmup", "profiling", "assessment"]:
            return True
        
        # Usa domande se la completezza è bassa
        if conversation_state.information_completeness < 0.7:
            return True
        
        return False
    
    def _update_context_conversationally(self,
                                       current_context: Dict[str, Any],
                                       user_input: str,
                                       processing_result: Dict[str, Any],
                                       personality_profile: Any,
                                       writing_style: Any) -> Dict[str, Any]:
        """Aggiorna il contesto usando l'approccio conversazionale"""
        
        try:
            # Usa il context bridge per aggiornare la checklist
            updated_context = self.context_bridge.update_checklist_from_conversation(
                current_context,
                user_input,
                processing_result.get("current_topic", "general"),
                personality_profile
            )
            
            # Aggiungi metadata conversazionali
            if "conversation_metadata" not in updated_context:
                updated_context["conversation_metadata"] = {}
            
            updated_context["conversation_metadata"].update({
                "personality_profile": personality_profile.to_dict(),
                "writing_style": writing_style.to_dict(),
                "last_update": datetime.now().isoformat(),
                "conversation_turn": len(self.conversation_history)
            })
            
            # Integra risultati dall'interpretazione standard se presenti
            interpretation = processing_result.get("operation_results", {}).get("interpretation", {})
            if interpretation.get("context_updates"):
                updated_context = merge_context(updated_context, interpretation["context_updates"])
            
            return updated_context
            
        except Exception as e:
            self.logger.error(f"[CONTEXT_UPDATE] Error updating context conversationally: {str(e)}")
            
            # Fallback all'aggiornamento standard
            return current_context
    
    def _generate_fallback_guidance(self,
                                  user_input: str,
                                  context: Dict[str, Any],
                                  personality_profile: Any) -> Dict[str, Any]:
        """Genera guidance di fallback in caso di errori"""
        
        fallback_responses = {
            "analytical": "Comprendo la tua richiesta. Per fornirti un consiglio accurato, ho bisogno di qualche informazione aggiuntiva.",
            "emotional": "Ti ringrazio per aver condiviso questo con me. Come ti senti riguardo alla situazione che mi hai descritto?",
            "practical": "Ok, lavoriamo insieme per trovare una soluzione pratica. Qual è la prima cosa che vorresti affrontare?",
            "social": "È interessante quello che mi racconti. Come reagiscono le persone intorno a te a questa situazione?"
        }
        
        profile_type = personality_profile.primary_type if personality_profile else "practical"
        fallback_text = fallback_responses.get(profile_type, fallback_responses["practical"])
        
        return {
            "last_output": {
                "guidance_markdown": fallback_text,
                "operation_type": "fallback_guidance",
                "personalization_applied": True
            },
            "token_usage": {"prompt_tokens": 0, "completion_tokens": len(fallback_text.split())}
        }
    
    def _fallback_to_original_processing(self, user_input: str) -> Dict[str, Any]:
        """Fallback al sistema di processing originale"""
        
        self.logger.warning("[CONVERSATIONAL] Falling back to original processing")
        
        try:
            # Usa l'orchestrator originale
            from .orchestrator import setup_and_run_orchestrator
            return setup_and_run_orchestrator(self.session_id, user_input)
            
        except Exception as e:
            self.logger.error(f"[FALLBACK] Error in fallback processing: {str(e)}")
            
            return {
                "last_output": {
                    "guidance_markdown": "Mi dispiace, ho avuto un problema tecnico. Puoi riprovare con la tua richiesta?",
                    "operation_type": "error_fallback"
                },
                "error": str(e)
            }
    
    def _update_token_stats(self, token_usage: Dict[str, Any]):
        """Aggiorna le statistiche dei token"""
        
        for operation, usage in token_usage.items():
            if isinstance(usage, dict):
                self.token_stats["operation_breakdown"][operation]["tokens"] += usage.get("total_tokens", 0)
                self.token_stats["operation_breakdown"][operation]["calls"] += 1
                
                # Calcolo costi (esempio, da adattare)
                cost = usage.get("total_tokens", 0) * 0.00001  # $0.00001 per token
                self.token_stats["operation_breakdown"][operation]["cost_usd"] += cost
        
        # Aggiorna totali
        total_input = sum(usage.get("prompt_tokens", 0) for usage in token_usage.values() if isinstance(usage, dict))
        total_output = sum(usage.get("completion_tokens", 0) for usage in token_usage.values() if isinstance(usage, dict))
        
        self.token_stats["total_input_tokens"] += total_input
        self.token_stats["total_output_tokens"] += total_output
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Restituisce un summary della conversazione attuale"""
        
        if not self.current_personality_profile or not self.conversation_history:
            return {"status": "no_conversation_data"}
        
        current_context = self.db_manager.get_context(self.session_id)
        
        return self.context_bridge.get_conversation_summary(
            self.conversation_history,
            current_context,
            self.current_personality_profile
        )
    
    def get_token_stats(self) -> Dict[str, Any]:
        """Restituisce le statistiche sui token"""
        
        return {
            **self.token_stats,
            "total_tokens": self.token_stats["total_input_tokens"] + self.token_stats["total_output_tokens"],
            "total_cost_estimate": sum(
                breakdown["cost_usd"] for breakdown in self.token_stats["operation_breakdown"].values()
            )
        }