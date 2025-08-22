"""
Enhanced LLM Interfaces - Estensioni per supportare prompt personalizzati
"""

from typing import Dict, Any, List
from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM
from src.llm_interfaces.user_input_interpreter_llm.user_input_interpreter_llm import UserInputInterpreterLLM
from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM


class EnhancedTaskGuidanceLLM(TaskGuidanceLLM):
    """Extended TaskGuidanceLLM che supporta prompt personalizzati"""
    
    def get_base_prompt(self) -> str:
        """Restituisce il prompt template base"""
        return self.prompt_template
    
    def process_with_custom_prompt(self,
                                 custom_prompt: str,
                                 user_input: str,
                                 context: Dict[str, Any],
                                 retrieved_docs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa usando un prompt personalizzato invece del template standard"""
        
        try:
            # Se non abbiamo documenti, recuperali
            if retrieved_docs is None:
                search_queries = [user_input]  # Semplificato
                all_documents = []
                
                for query in search_queries:
                    if query.strip():
                        documents = self.retriever.search(query, k=self.retrieval_k)
                        all_documents.extend(documents)
                
                # Rimuovi duplicati
                seen_ids = set()
                unique_documents = []
                for doc in all_documents:
                    doc_id = doc.get("id", str(doc))
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        unique_documents.append(doc)
                
                retrieved_docs = unique_documents[:self.retrieval_k]
            
            # Formatta documenti
            formatted_docs = self._format_documents(retrieved_docs)
            
            # Prepara il prompt finale sostituendo il template con quello personalizzato
            final_prompt = custom_prompt.replace(
                "{{RETRIEVED_DOCUMENTS}}", formatted_docs
            ).replace(
                "{{USER_INPUT}}", user_input
            ).replace(
                "{{CONTEXT}}", str(context)
            )
            
            # Log per debug
            self.logger.info(f"[ENHANCED] Using custom prompt for guidance generation")
            
            # Chiama l'LLM
            response = self.llm_client.call_llm(
                final_prompt, 
                model="gemini-1.5-flash",
                max_tokens=2000
            )
            
            # Log della risposta
            self.logger.info(f"[ENHANCED] Generated personalized guidance")
            
            return {
                "guidance_markdown": response.get("content", ""),
                "token_usage": response.get("token_usage", {}),
                "retrieved_documents": len(retrieved_docs),
                "personalized": True
            }
            
        except Exception as e:
            self.logger.error(f"[ENHANCED] Error in custom prompt processing: {str(e)}")
            
            # Fallback al metodo originale
            return self.generate_task_guidance(user_input, context)


class EnhancedUserInputInterpreterLLM(UserInputInterpreterLLM):
    """Extended UserInputInterpreterLLM che supporta prompt personalizzati"""
    
    def get_base_prompt(self) -> str:
        """Restituisce il prompt template base"""
        return self.prompt_template
    
    def process_with_custom_prompt(self,
                                 custom_prompt: str,
                                 user_input: str,
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa usando un prompt personalizzato"""
        
        try:
            # Prepara il prompt finale
            final_prompt = custom_prompt.replace(
                "{{USER_INPUT}}", user_input
            ).replace(
                "{{CURRENT_CONTEXT}}", str(context)
            )
            
            self.logger.info(f"[ENHANCED] Using custom prompt for input interpretation")
            
            # Chiama l'LLM
            response = self.llm_client.call_llm(
                final_prompt,
                model="gemini-1.5-flash",
                max_tokens=1500
            )
            
            # Parsa la risposta (usando la logica esistente)
            parsed_updates = self._parse_context_updates(response.get("content", ""))
            
            return {
                "context_updates": parsed_updates,
                "token_usage": response.get("token_usage", {}),
                "personalized": True
            }
            
        except Exception as e:
            self.logger.error(f"[ENHANCED] Error in custom interpretation: {str(e)}")
            
            # Fallback al metodo originale
            return self.update_context_with_observation(user_input, context)


class EnhancedQueryGeneratorLLM(QueryGeneratorLLM):
    """Extended QueryGeneratorLLM che supporta prompt personalizzati"""
    
    def get_base_prompt(self) -> str:
        """Restituisce il prompt template base"""
        return self.prompt_template
    
    def process_with_custom_prompt(self,
                                 custom_prompt: str,
                                 user_input: str,
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa usando un prompt personalizzato per la generazione di query"""
        
        try:
            # Prepara il prompt finale
            final_prompt = custom_prompt.replace(
                "{{USER_INPUT}}", user_input
            ).replace(
                "{{CONTEXT}}", str(context)
            )
            
            self.logger.info(f"[ENHANCED] Using custom prompt for query generation")
            
            # Chiama l'LLM
            response = self.llm_client.call_llm(
                final_prompt,
                model="gemini-1.5-flash",
                max_tokens=500
            )
            
            # Parsa le query (usando la logica esistente)
            queries = self._parse_queries(response.get("content", ""))
            
            return {
                "generated_queries": queries,
                "token_usage": response.get("token_usage", {}),
                "personalized": True
            }
            
        except Exception as e:
            self.logger.error(f"[ENHANCED] Error in custom query generation: {str(e)}")
            
            # Fallback al metodo originale
            return self.generate_search_queries(user_input, context)


def create_enhanced_llm_interfaces(original_task_guidance: TaskGuidanceLLM,
                                 original_interpreter: UserInputInterpreterLLM,
                                 original_query_gen: QueryGeneratorLLM) -> tuple:
    """
    Crea versioni enhanced degli LLM interfaces esistenti
    """
    
    # Crea enhanced task guidance
    enhanced_task_guidance = EnhancedTaskGuidanceLLM(
        original_task_guidance.llm_client,
        "", # Non usato, usiamo il template dall'originale
        original_task_guidance.retriever
    )
    enhanced_task_guidance.prompt_template = original_task_guidance.prompt_template
    enhanced_task_guidance.retrieval_k = original_task_guidance.retrieval_k
    
    # Crea enhanced interpreter
    enhanced_interpreter = EnhancedUserInputInterpreterLLM(
        original_interpreter.llm_client,
        "" # Non usato
    )
    enhanced_interpreter.prompt_template = original_interpreter.prompt_template
    
    # Crea enhanced query generator
    enhanced_query_gen = EnhancedQueryGeneratorLLM(
        original_query_gen.llm_client,
        "" # Non usato
    )
    enhanced_query_gen.prompt_template = original_query_gen.prompt_template
    
    return enhanced_task_guidance, enhanced_interpreter, enhanced_query_gen