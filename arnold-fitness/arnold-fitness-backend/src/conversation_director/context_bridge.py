"""
Context Bridge - Collega il sistema di checklist con il nuovo flusso conversazionale
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import copy

from .question_selector import QuestionSelector, QuestionContext
from .flow_manager import FlowManager, ConversationState, ConversationPhase
from ..personality_profiler import PersonalityProfile, WritingStyle


class ContextBridge:
    """Ponte tra il sistema checklist esistente e il nuovo sistema conversazionale"""
    
    def __init__(self):
        self.question_selector = QuestionSelector()
        self.flow_manager = FlowManager()
    
    def get_next_conversational_step(self,
                                   checklist_context: Dict[str, Any],
                                   conversation_history: List[Dict[str, str]],
                                   personality_profile: PersonalityProfile,
                                   writing_style: WritingStyle) -> Dict[str, Any]:
        """Restituisce il prossimo step conversazionale basato su checklist e profilo"""
        
        # Valuta lo stato della conversazione
        conversation_state = self.flow_manager.assess_conversation_state(
            conversation_history, checklist_context, personality_profile
        )
        
        # Verifica se è necessario cambiare fase
        new_phase = self.flow_manager.should_transition_phase(
            conversation_state, checklist_context
        )
        
        if new_phase:
            conversation_state.phase = new_phase
        
        # Seleziona la prossima domanda
        next_question = self.question_selector.select_next_question(
            checklist_context, personality_profile, writing_style, conversation_history
        )
        
        # Ottieni guidance per la fase corrente
        phase_guidance = self.flow_manager.get_phase_guidance(
            conversation_state.phase, personality_profile
        )
        
        # Ottieni raccomandazioni per lo stile di interazione
        interaction_style = self.flow_manager.recommend_interaction_style(
            conversation_state, personality_profile
        )
        
        return {
            "conversation_state": conversation_state,
            "next_question": next_question,
            "phase_guidance": phase_guidance,
            "interaction_style": interaction_style,
            "context_insights": self._extract_context_insights(checklist_context),
            "recommendations": self._generate_recommendations(
                conversation_state, checklist_context, personality_profile
            )
        }
    
    def update_checklist_from_conversation(self,
                                         checklist_context: Dict[str, Any],
                                         user_response: str,
                                         current_topic: str,
                                         personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Aggiorna la checklist basandosi sulla risposta conversazionale dell'utente"""
        
        updated_context = copy.deepcopy(checklist_context)
        
        # Identifica quale check è stato affrontato
        affected_checks = self._identify_affected_checks(current_topic, user_response)
        
        # Aggiorna ogni check pertinente
        for check_id in affected_checks:
            self._update_specific_check(
                updated_context, check_id, user_response, personality_profile
            )
        
        # Estrai insight dalla risposta
        insights = self._extract_response_insights(user_response, personality_profile)
        
        # Aggiungi insight al contesto
        if "conversation_insights" not in updated_context:
            updated_context["conversation_insights"] = {}
        
        updated_context["conversation_insights"].update(insights)
        
        return updated_context
    
    def map_conversational_response_to_checklist(self,
                                                response: str,
                                                question_context: Dict[str, Any]) -> List[Tuple[str, str, Any]]:
        """Mappa una risposta conversazionale agli aggiornamenti della checklist"""
        
        updates = []
        
        # Identifica il tipo di domanda che è stata posta
        question_type = question_context.get("question_type", "")
        template_key = question_context.get("template_key", "")
        
        # Mapping per diversi tipi di domande
        if question_type == "demographic_info":
            updates.extend(self._extract_demographic_updates(response))
        elif question_type == "goal_exploration":
            updates.extend(self._extract_goal_updates(response))
        elif question_type == "habit_assessment":
            updates.extend(self._extract_habit_updates(response))
        elif question_type == "activity_assessment":
            updates.extend(self._extract_activity_updates(response))
        elif question_type == "followup":
            updates.extend(self._extract_followup_updates(response, template_key))
        
        return updates
    
    def get_conversation_summary(self,
                               conversation_history: List[Dict[str, str]],
                               checklist_context: Dict[str, Any],
                               personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Genera un riassunto dello stato conversazionale e dei progressi"""
        
        # Analizza il progresso della checklist
        checklist_progress = self._analyze_checklist_progress(checklist_context)
        
        # Analizza la qualità della conversazione
        conversation_quality = self._analyze_conversation_quality(
            conversation_history, personality_profile
        )
        
        # Identifica prossimi passi
        next_steps = self._identify_next_steps(
            checklist_progress, conversation_quality, personality_profile
        )
        
        # Estrai insight chiave
        key_insights = self._extract_key_insights(
            conversation_history, checklist_context, personality_profile
        )
        
        return {
            "checklist_progress": checklist_progress,
            "conversation_quality": conversation_quality,
            "next_steps": next_steps,
            "key_insights": key_insights,
            "recommendations": next_steps.get("recommendations", [])
        }
    
    def _identify_affected_checks(self, current_topic: str, user_response: str) -> List[str]:
        """Identifica quali check della checklist sono influenzati dalla risposta"""
        
        affected_checks = []
        response_lower = user_response.lower()
        
        # Mapping topic -> check_ids
        topic_check_mapping = {
            "demographics": ["basic_demographics", "personal_info"],
            "goals": ["health_goals", "fitness_goals", "weight_goals"],
            "eating_habits": ["current_eating_habits", "meal_patterns", "food_preferences"],
            "activity": ["activity_level", "exercise_habits", "physical_activity"],
            "lifestyle": ["lifestyle_factors", "schedule_constraints", "work_life"],
            "health": ["health_history", "medical_conditions", "medications"],
            "preferences": ["dietary_preferences", "food_restrictions", "cooking_skills"]
        }
        
        # Cerca match diretti per topic
        if current_topic in topic_check_mapping:
            affected_checks.extend(topic_check_mapping[current_topic])
        
        # Cerca match per keyword nella risposta
        keyword_mapping = {
            "età": ["basic_demographics"],
            "anni": ["basic_demographics"],
            "peso": ["weight_goals", "current_metrics"],
            "sport": ["activity_level", "exercise_habits"],
            "mangiare": ["current_eating_habits"],
            "cibo": ["food_preferences", "current_eating_habits"],
            "lavoro": ["lifestyle_factors", "schedule_constraints"],
            "stress": ["stress_factors", "lifestyle_factors"],
            "allergia": ["dietary_restrictions", "food_allergies"],
            "malattia": ["health_history", "medical_conditions"]
        }
        
        for keyword, checks in keyword_mapping.items():
            if keyword in response_lower:
                affected_checks.extend(checks)
        
        return list(set(affected_checks))  # Rimuovi duplicati
    
    def _update_specific_check(self,
                             context: Dict[str, Any],
                             check_id: str,
                             user_response: str,
                             personality_profile: PersonalityProfile):
        """Aggiorna un check specifico basandosi sulla risposta dell'utente"""
        
        checklist = context.get("checklist", [])
        
        # Trova il check nella struttura
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    if check.get("check_id") == check_id:
                        # Aggiorna lo stato del check
                        if check.get("state") == "pending":
                            check["state"] = "in_progress"
                        
                        # Aggiungi o aggiorna le note
                        current_notes = check.get("notes", "")
                        new_notes = self._extract_relevant_info(
                            user_response, check_id, personality_profile
                        )
                        
                        if new_notes:
                            if current_notes:
                                check["notes"] = f"{current_notes}; {new_notes}"
                            else:
                                check["notes"] = new_notes
                        
                        # Se abbiamo informazioni sufficienti, marca come completato
                        if self._is_check_complete(check, user_response):
                            check["state"] = "done"
                        
                        break
    
    def _extract_relevant_info(self,
                             user_response: str,
                             check_id: str,
                             personality_profile: PersonalityProfile) -> str:
        """Estrae informazioni rilevanti dalla risposta per un check specifico"""
        
        response_lower = user_response.lower()
        
        # Extraction rules per tipo di check
        extraction_rules = {
            "basic_demographics": self._extract_demographics,
            "health_goals": self._extract_goals,
            "current_eating_habits": self._extract_eating_habits,
            "activity_level": self._extract_activity_info,
            "dietary_preferences": self._extract_dietary_preferences,
            "lifestyle_factors": self._extract_lifestyle_info
        }
        
        extractor = extraction_rules.get(check_id)
        if extractor:
            return extractor(user_response)
        
        # Default: estrai informazioni generiche
        return user_response[:200]  # Prime 200 caratteri come fallback
    
    def _extract_demographics(self, response: str) -> str:
        """Estrae informazioni demografiche dalla risposta"""
        import re
        
        demographics = []
        
        # Cerca età
        age_patterns = [
            r'(\d+)\s*anni?',
            r'ho\s+(\d+)',
            r'sono\s+(\d+)',
            r'età[:\s]+(\d+)'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, response.lower())
            if match:
                demographics.append(f"Età: {match.group(1)} anni")
                break
        
        # Cerca genere
        if any(word in response.lower() for word in ['sono un uomo', 'maschio', 'sono uomo']):
            demographics.append("Genere: Maschile")
        elif any(word in response.lower() for word in ['sono una donna', 'femmina', 'sono donna']):
            demographics.append("Genere: Femminile")
        
        return "; ".join(demographics) if demographics else response[:100]
    
    def _extract_goals(self, response: str) -> str:
        """Estrae obiettivi dalla risposta"""
        goals = []
        response_lower = response.lower()
        
        # Pattern comuni per obiettivi
        goal_patterns = {
            "perdere peso": "Perdita di peso",
            "dimagrire": "Perdita di peso",
            "mettere massa": "Aumento massa muscolare",
            "muscoli": "Aumento massa muscolare",
            "tonificare": "Tonificazione",
            "salute": "Miglioramento salute generale",
            "energia": "Aumento energia",
            "forma fisica": "Miglioramento forma fisica"
        }
        
        for pattern, goal in goal_patterns.items():
            if pattern in response_lower:
                goals.append(goal)
        
        return "; ".join(goals) if goals else response[:150]
    
    def _extract_eating_habits(self, response: str) -> str:
        """Estrae abitudini alimentari dalla risposta"""
        habits = []
        response_lower = response.lower()
        
        # Pattern per abitudini
        habit_patterns = {
            "colazione": "Fa colazione",
            "non faccio colazione": "Non fa colazione",
            "salto": "Salta pasti",
            "fuori pasti": "Mangia fuori pasto",
            "sera": "Mangia la sera",
            "fast food": "Consuma fast food",
            "cucino": "Cucina a casa",
            "ordinare": "Ordina spesso"
        }
        
        for pattern, habit in habit_patterns.items():
            if pattern in response_lower:
                habits.append(habit)
        
        return "; ".join(habits) if habits else response[:150]
    
    def _extract_activity_info(self, response: str) -> str:
        """Estrae informazioni sull'attività fisica dalla risposta"""
        activity_info = []
        response_lower = response.lower()
        
        # Tipi di attività
        activities = {
            "palestra": "Palestra",
            "correre": "Corsa",
            "camminare": "Camminata",
            "nuoto": "Nuoto",
            "calcio": "Calcio",
            "tennis": "Tennis",
            "yoga": "Yoga",
            "sedentario": "Stile di vita sedentario"
        }
        
        for activity, label in activities.items():
            if activity in response_lower:
                activity_info.append(label)
        
        # Frequenza
        frequency_patterns = {
            "ogni giorno": "Frequenza: quotidiana",
            "tutti i giorni": "Frequenza: quotidiana", 
            "settimana": "Frequenza: settimanale",
            "raramente": "Frequenza: raramente",
            "mai": "Frequenza: mai"
        }
        
        for pattern, freq in frequency_patterns.items():
            if pattern in response_lower:
                activity_info.append(freq)
                break
        
        return "; ".join(activity_info) if activity_info else response[:150]
    
    def _extract_dietary_preferences(self, response: str) -> str:
        """Estrae preferenze dietetiche dalla risposta"""
        preferences = []
        response_lower = response.lower()
        
        # Diete speciali
        diet_patterns = {
            "vegetariano": "Vegetariano",
            "vegano": "Vegano", 
            "senza glutine": "Senza glutine",
            "keto": "Dieta chetogenica",
            "mediterranea": "Dieta mediterranea",
            "allergia": "Ha allergie alimentari"
        }
        
        for pattern, pref in diet_patterns.items():
            if pattern in response_lower:
                preferences.append(pref)
        
        return "; ".join(preferences) if preferences else response[:150]
    
    def _extract_lifestyle_info(self, response: str) -> str:
        """Estrae informazioni sullo stile di vita dalla risposta"""
        lifestyle_info = []
        response_lower = response.lower()
        
        # Pattern lifestyle
        lifestyle_patterns = {
            "stress": "Alto livello di stress",
            "lavoro": "Fattori lavorativi",
            "famiglia": "Responsabilità familiari",
            "tempo": "Limitazioni di tempo",
            "viaggiare": "Viaggia spesso",
            "turni": "Lavoro a turni"
        }
        
        for pattern, info in lifestyle_patterns.items():
            if pattern in response_lower:
                lifestyle_info.append(info)
        
        return "; ".join(lifestyle_info) if lifestyle_info else response[:150]
    
    def _is_check_complete(self, check: Dict[str, Any], user_response: str) -> bool:
        """Determina se un check può essere considerato completato"""
        
        # Criteri semplici per completamento
        notes = check.get("notes", "")
        
        # Se abbiamo note sufficienti e una risposta non vaga
        if len(notes) > 20 and len(user_response.split()) > 3:
            vague_responses = ["non so", "boh", "forse", "magari", "mah"]
            if not any(vague in user_response.lower() for vague in vague_responses):
                return True
        
        return False
    
    def _extract_context_insights(self, checklist_context: Dict[str, Any]) -> Dict[str, Any]:
        """Estrae insight dal contesto della checklist"""
        
        insights = {
            "completion_rate": 0.0,
            "critical_gaps": [],
            "completed_areas": [],
            "user_profile_emerging": {}
        }
        
        checklist = checklist_context.get("checklist", [])
        
        total_checks = 0
        completed_checks = 0
        
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    total_checks += 1
                    
                    if check.get("state") == "done":
                        completed_checks += 1
                        insights["completed_areas"].append(check.get("check_id", ""))
                    elif check.get("state") == "pending" and self._is_critical_check(check):
                        insights["critical_gaps"].append(check.get("check_id", ""))
        
        insights["completion_rate"] = completed_checks / total_checks if total_checks > 0 else 0.0
        
        return insights
    
    def _is_critical_check(self, check: Dict[str, Any]) -> bool:
        """Determina se un check è critico per il processo"""
        critical_checks = [
            "basic_demographics", "health_goals", "current_eating_habits", 
            "activity_level", "dietary_restrictions"
        ]
        return check.get("check_id", "") in critical_checks
    
    def _generate_recommendations(self,
                                conversation_state: ConversationState,
                                checklist_context: Dict[str, Any],
                                personality_profile: PersonalityProfile) -> List[str]:
        """Genera raccomandazioni per la conversazione"""
        
        recommendations = []
        
        # Raccomandazioni basate sulla fase
        if conversation_state.phase == ConversationPhase.WARMUP:
            recommendations.append("Focalizzarsi sulla costruzione del rapport")
            recommendations.append("Usare domande aperte e non invasive")
        elif conversation_state.phase == ConversationPhase.ASSESSMENT:
            recommendations.append("Raccogliere informazioni mancanti critiche")
            recommendations.append("Mantenere il flusso conversazionale naturale")
        
        # Raccomandazioni basate sull'engagement
        if conversation_state.user_engagement == "low":
            recommendations.append("Aumentare supporto emotivo e rassicurazione")
            recommendations.append("Considerare domande più semplici e meno invasive")
        
        # Raccomandazioni basate sulla completezza
        if conversation_state.information_completeness < 0.5:
            recommendations.append("Accelerare la raccolta di informazioni base")
        elif conversation_state.information_completeness > 0.8:
            recommendations.append("Iniziare a focalizzarsi sulla pianificazione")
        
        return recommendations
    
    # Metodi di supporto per le estrazioni specifiche
    
    def _extract_demographic_updates(self, response: str) -> List[Tuple[str, str, Any]]:
        """Estrae aggiornamenti demografici dalla risposta"""
        updates = []
        
        demographic_info = self._extract_demographics(response)
        if demographic_info:
            updates.append(("basic_demographics", "notes", demographic_info))
            updates.append(("basic_demographics", "state", "done"))
        
        return updates
    
    def _extract_goal_updates(self, response: str) -> List[Tuple[str, str, Any]]:
        """Estrae aggiornamenti degli obiettivi dalla risposta"""
        updates = []
        
        goals_info = self._extract_goals(response)
        if goals_info:
            updates.append(("health_goals", "notes", goals_info))
            updates.append(("health_goals", "state", "in_progress"))
        
        return updates
    
    def _extract_habit_updates(self, response: str) -> List[Tuple[str, str, Any]]:
        """Estrae aggiornamenti delle abitudini dalla risposta"""
        updates = []
        
        habits_info = self._extract_eating_habits(response)
        if habits_info:
            updates.append(("current_eating_habits", "notes", habits_info))
            updates.append(("current_eating_habits", "state", "in_progress"))
        
        return updates
    
    def _extract_activity_updates(self, response: str) -> List[Tuple[str, str, Any]]:
        """Estrae aggiornamenti dell'attività dalla risposta"""
        updates = []
        
        activity_info = self._extract_activity_info(response)
        if activity_info:
            updates.append(("activity_level", "notes", activity_info))
            updates.append(("activity_level", "state", "in_progress"))
        
        return updates
    
    def _extract_followup_updates(self, response: str, template_key: str) -> List[Tuple[str, str, Any]]:
        """Estrae aggiornamenti da domande di follow-up"""
        updates = []
        
        # Follow-up generici aggiungono dettagli alle note esistenti
        if template_key and len(response.split()) > 3:
            updates.append((template_key, "notes", f"Follow-up: {response[:200]}"))
        
        return updates
    
    def _analyze_checklist_progress(self, checklist_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza il progresso della checklist"""
        
        checklist = checklist_context.get("checklist", [])
        
        progress = {
            "total_checks": 0,
            "completed_checks": 0,
            "in_progress_checks": 0,
            "pending_checks": 0,
            "completion_percentage": 0.0,
            "phase_progress": {}
        }
        
        for phase in checklist:
            phase_name = phase.get("title", "Unknown")
            phase_stats = {"total": 0, "completed": 0, "in_progress": 0, "pending": 0}
            
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    progress["total_checks"] += 1
                    phase_stats["total"] += 1
                    
                    state = check.get("state", "pending")
                    progress[f"{state}_checks"] += 1
                    phase_stats[state] += 1
        
        progress["completion_percentage"] = (progress["completed_checks"] / 
                                           progress["total_checks"] * 100 
                                           if progress["total_checks"] > 0 else 0)
        
        return progress
    
    def _analyze_conversation_quality(self,
                                    conversation_history: List[Dict[str, str]],
                                    personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Analizza la qualità della conversazione"""
        
        quality = {
            "total_exchanges": len(conversation_history),
            "avg_user_response_length": 0,
            "engagement_indicators": [],
            "rapport_level": "building",
            "conversation_depth": "surface"
        }
        
        if not conversation_history:
            return quality
        
        # Calcola lunghezza media delle risposte
        user_responses = [msg.get("user", "") for msg in conversation_history]
        total_words = sum(len(response.split()) for response in user_responses)
        quality["avg_user_response_length"] = total_words / len(user_responses) if user_responses else 0
        
        # Analizza indicatori di engagement
        recent_responses = user_responses[-3:] if len(user_responses) >= 3 else user_responses
        
        for response in recent_responses:
            if len(response.split()) > 10:
                quality["engagement_indicators"].append("detailed_responses")
            if "?" in response:
                quality["engagement_indicators"].append("asks_questions")
            if any(word in response.lower() for word in ["grazie", "ottimo", "perfetto"]):
                quality["engagement_indicators"].append("positive_feedback")
        
        # Determina livello di rapport
        if len(quality["engagement_indicators"]) >= 4:
            quality["rapport_level"] = "strong"
        elif len(quality["engagement_indicators"]) >= 2:
            quality["rapport_level"] = "established"
        
        return quality
    
    def _identify_next_steps(self,
                           checklist_progress: Dict[str, Any],
                           conversation_quality: Dict[str, Any],
                           personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Identifica i prossimi passi raccomandati"""
        
        next_steps = {
            "immediate_priorities": [],
            "conversation_adjustments": [],
            "checklist_focus": [],
            "recommendations": []
        }
        
        # Priorità immediate basate sul progresso
        if checklist_progress["completion_percentage"] < 30:
            next_steps["immediate_priorities"].append("Accelerare raccolta informazioni base")
        elif checklist_progress["completion_percentage"] < 70:
            next_steps["immediate_priorities"].append("Completare assessment critico")
        else:
            next_steps["immediate_priorities"].append("Iniziare pianificazione")
        
        # Aggiustamenti conversazionali
        if conversation_quality["avg_user_response_length"] < 5:
            next_steps["conversation_adjustments"].append("Incoraggiare risposte più dettagliate")
        
        if conversation_quality["rapport_level"] == "building":
            next_steps["conversation_adjustments"].append("Investire più tempo nel rapport building")
        
        return next_steps
    
    def _extract_key_insights(self,
                            conversation_history: List[Dict[str, str]],
                            checklist_context: Dict[str, Any],
                            personality_profile: PersonalityProfile) -> List[str]:
        """Estrae insight chiave dalla conversazione"""
        
        insights = []
        
        # Insight dal profilo personalità
        insights.append(f"Profilo primario: {personality_profile.primary_type}")
        insights.append(f"Stile comunicativo preferito: {personality_profile.communication_preference}")
        
        # Insight dalla conversazione
        if conversation_history:
            total_user_words = sum(len(msg.get("user", "").split()) for msg in conversation_history)
            avg_words = total_user_words / len(conversation_history)
            
            if avg_words > 15:
                insights.append("Utente molto comunicativo e dettagliato")
            elif avg_words < 5:
                insights.append("Utente conciso, preferisce risposte brevi")
        
        # Insight dalla checklist
        completion_rate = self._calculate_completion_rate(checklist_context)
        if completion_rate > 0.7:
            insights.append("Ottime informazioni raccolte, pronto per pianificazione")
        elif completion_rate < 0.3:
            insights.append("Necessarie più informazioni per assessment completo")
        
        return insights
    
    def _calculate_completion_rate(self, checklist_context: Dict[str, Any]) -> float:
        """Calcola il tasso di completamento della checklist"""
        
        checklist = checklist_context.get("checklist", [])
        
        total = 0
        completed = 0
        
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    total += 1
                    if check.get("state") == "done":
                        completed += 1
        
        return completed / total if total > 0 else 0.0
    
    def _extract_response_insights(self,
                                 user_response: str,
                                 personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Estrae insight dalla risposta dell'utente"""
        
        insights = {}
        response_lower = user_response.lower()
        
        # Sentiment della risposta
        positive_indicators = ["bene", "ottimo", "sì", "perfetto", "grazie"]
        negative_indicators = ["male", "difficile", "problema", "non riesco", "stress"]
        
        positive_score = sum(1 for ind in positive_indicators if ind in response_lower)
        negative_score = sum(1 for ind in negative_indicators if ind in response_lower)
        
        if positive_score > negative_score:
            insights["response_sentiment"] = "positive"
        elif negative_score > positive_score:
            insights["response_sentiment"] = "negative"
        else:
            insights["response_sentiment"] = "neutral"
        
        # Livello di dettaglio
        word_count = len(user_response.split())
        if word_count > 20:
            insights["detail_level"] = "high"
        elif word_count > 8:
            insights["detail_level"] = "medium"
        else:
            insights["detail_level"] = "low"
        
        # Openness (quanto condivide)
        personal_indicators = ["io", "mi", "mio", "mia", "per me"]
        personal_count = sum(1 for ind in personal_indicators if ind in response_lower)
        
        insights["openness_level"] = "high" if personal_count > 3 else "medium" if personal_count > 1 else "low"
        
        return insights