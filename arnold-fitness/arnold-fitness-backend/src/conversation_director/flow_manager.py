"""
Flow Manager - Gestisce il flusso naturale della conversazione
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..personality_profiler import PersonalityProfile, WritingStyle


class ConversationPhase(Enum):
    """Fasi della conversazione"""
    WARMUP = "warmup"
    PROFILING = "profiling" 
    ASSESSMENT = "assessment"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    MONITORING = "monitoring"


@dataclass
class ConversationState:
    """Stato attuale della conversazione"""
    phase: ConversationPhase
    turn_count: int
    user_engagement: str  # "low", "medium", "high"
    information_completeness: float  # 0.0 to 1.0
    relationship_strength: str  # "building", "established", "strong"
    last_topic: str
    pending_followups: List[str]


class FlowManager:
    """Gestisce il flusso e le transizioni della conversazione"""
    
    def __init__(self):
        self.phase_rules = self._load_phase_rules()
        self.transition_conditions = self._load_transition_conditions()
        self.engagement_indicators = self._load_engagement_indicators()
    
    def assess_conversation_state(self,
                                conversation_history: List[Dict[str, str]],
                                checklist_context: Dict[str, Any],
                                personality_profile: PersonalityProfile) -> ConversationState:
        """Valuta lo stato attuale della conversazione"""
        
        turn_count = len(conversation_history)
        
        # Determina la fase attuale
        current_phase = self._determine_current_phase(
            turn_count, checklist_context, conversation_history
        )
        
        # Valuta l'engagement dell'utente
        user_engagement = self._assess_user_engagement(
            conversation_history, personality_profile
        )
        
        # Calcola la completezza delle informazioni
        information_completeness = self._calculate_information_completeness(
            checklist_context
        )
        
        # Valuta la forza della relazione
        relationship_strength = self._assess_relationship_strength(
            conversation_history, user_engagement, turn_count
        )
        
        # Identifica l'ultimo topic discusso
        last_topic = self._identify_last_topic(conversation_history)
        
        # Identifica follow-up pendenti
        pending_followups = self._identify_pending_followups(
            conversation_history, checklist_context
        )
        
        return ConversationState(
            phase=current_phase,
            turn_count=turn_count,
            user_engagement=user_engagement,
            information_completeness=information_completeness,
            relationship_strength=relationship_strength,
            last_topic=last_topic,
            pending_followups=pending_followups
        )
    
    def should_transition_phase(self,
                              current_state: ConversationState,
                              checklist_context: Dict[str, Any]) -> Optional[ConversationPhase]:
        """Determina se è il momento di transitare a una nuova fase"""
        
        current_phase = current_state.phase
        
        # Regole per transizioni di fase
        transition_rules = {
            ConversationPhase.WARMUP: self._should_exit_warmup,
            ConversationPhase.PROFILING: self._should_exit_profiling,
            ConversationPhase.ASSESSMENT: self._should_exit_assessment,
            ConversationPhase.PLANNING: self._should_exit_planning,
            ConversationPhase.IMPLEMENTATION: self._should_exit_implementation
        }
        
        rule_func = transition_rules.get(current_phase)
        if rule_func and rule_func(current_state, checklist_context):
            return self._get_next_phase(current_phase)
        
        return None
    
    def get_phase_guidance(self,
                          phase: ConversationPhase,
                          personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Restituisce guidance per la fase corrente"""
        
        phase_guidance = {
            ConversationPhase.WARMUP: {
                "objective": "Costruire rapport e mettere a proprio agio l'utente",
                "approach": "Domande aperte e accoglienti",
                "duration_turns": 2-3,
                "success_indicators": ["utente condivide spontaneamente", "tono rilassato"]
            },
            ConversationPhase.PROFILING: {
                "objective": "Comprendere stile di comunicazione e personalità",
                "approach": "Osservare pattern di risposta e adattarsi",
                "duration_turns": 3-5,
                "success_indicators": ["stile comunicativo chiaro", "adattamento avvenuto"]
            },
            ConversationPhase.ASSESSMENT: {
                "objective": "Raccogliere informazioni critiche per la valutazione",
                "approach": "Domande strutturate ma naturali",
                "duration_turns": 8-12,
                "success_indicators": ["informazioni chiave raccolte", "checklist 70%+ completa"]
            },
            ConversationPhase.PLANNING: {
                "objective": "Co-creare un piano personalizzato",
                "approach": "Collaborativo e orientato alle soluzioni",
                "duration_turns": 5-8,
                "success_indicators": ["piano condiviso", "commitment dell'utente"]
            },
            ConversationPhase.IMPLEMENTATION: {
                "objective": "Supportare l'implementazione del piano",
                "approach": "Coaching e problem-solving",
                "duration_turns": "ongoing",
                "success_indicators": ["azioni intraprese", "feedback su progressi"]
            }
        }
        
        base_guidance = phase_guidance.get(phase, {})
        
        # Personalizza per il profilo dell'utente
        if personality_profile:
            base_guidance = self._personalize_phase_guidance(
                base_guidance, personality_profile
            )
        
        return base_guidance
    
    def recommend_interaction_style(self,
                                  current_state: ConversationState,
                                  personality_profile: PersonalityProfile) -> Dict[str, str]:
        """Raccomanda lo stile di interazione per lo stato corrente"""
        
        style_recommendations = {}
        
        # Basato sulla fase
        phase_styles = {
            ConversationPhase.WARMUP: {
                "tone": "accogliente e rilassato",
                "question_style": "aperte e non invasive",
                "pace": "lento e naturale"
            },
            ConversationPhase.PROFILING: {
                "tone": "curioso e osservativo", 
                "question_style": "esploratore ma rispettoso",
                "pace": "moderato con pause per osservazione"
            },
            ConversationPhase.ASSESSMENT: {
                "tone": "professionale ma empatico",
                "question_style": "specifiche ma conversazionali",
                "pace": "efficiente ma non affrettato"
            }
        }
        
        style_recommendations.update(
            phase_styles.get(current_state.phase, {})
        )
        
        # Aggiustamenti basati su engagement
        if current_state.user_engagement == "low":
            style_recommendations.update({
                "tone": "più supportivo e rassicurante",
                "question_style": "più soft e opzionali",
                "pace": "più lento con più validazione"
            })
        elif current_state.user_engagement == "high":
            style_recommendations.update({
                "pace": "può essere più efficiente",
                "question_style": "può essere più dirette"
            })
        
        # Aggiustamenti basati sulla forza della relazione
        if current_state.relationship_strength == "building":
            style_recommendations["priority"] = "costruire fiducia"
        elif current_state.relationship_strength == "strong":
            style_recommendations["priority"] = "massimizzare efficacia"
        
        return style_recommendations
    
    def _determine_current_phase(self,
                               turn_count: int,
                               checklist_context: Dict[str, Any],
                               conversation_history: List[Dict[str, str]]) -> ConversationPhase:
        """Determina la fase corrente basandosi sul contesto"""
        
        # Regole semplici per determinare la fase
        if turn_count <= 3:
            return ConversationPhase.WARMUP
        elif turn_count <= 8:
            return ConversationPhase.PROFILING
        
        # Guarda la completezza della checklist per le fasi successive
        completeness = self._calculate_information_completeness(checklist_context)
        
        if completeness < 0.7:
            return ConversationPhase.ASSESSMENT
        elif completeness < 0.9:
            return ConversationPhase.PLANNING
        else:
            return ConversationPhase.IMPLEMENTATION
    
    def _assess_user_engagement(self,
                              conversation_history: List[Dict[str, str]],
                              personality_profile: PersonalityProfile) -> str:
        """Valuta il livello di engagement dell'utente"""
        
        if not conversation_history:
            return "medium"
        
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
        
        engagement_score = 0
        total_possible = len(recent_messages) * 3
        
        for msg in recent_messages:
            user_text = msg.get("user", "")
            
            # Indicatori positivi di engagement
            if len(user_text.split()) > 10:  # Risposte elaborate
                engagement_score += 2
            elif len(user_text.split()) > 3:  # Risposte moderate
                engagement_score += 1
            
            # Domande dall'utente indicano interesse
            if "?" in user_text:
                engagement_score += 1
            
            # Condivisione di dettagli personali
            personal_indicators = ["io", "mi", "mio", "mia", "per me", "nella mia situazione"]
            if any(indicator in user_text.lower() for indicator in personal_indicators):
                engagement_score += 1
        
        engagement_ratio = engagement_score / total_possible if total_possible > 0 else 0
        
        if engagement_ratio > 0.7:
            return "high"
        elif engagement_ratio > 0.4:
            return "medium"
        else:
            return "low"
    
    def _calculate_information_completeness(self, checklist_context: Dict[str, Any]) -> float:
        """Calcola la percentuale di completezza delle informazioni"""
        
        checklist = checklist_context.get("checklist", [])
        
        total_checks = 0
        completed_checks = 0
        
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    total_checks += 1
                    if check.get("state") == "done":
                        completed_checks += 1
        
        return completed_checks / total_checks if total_checks > 0 else 0.0
    
    def _assess_relationship_strength(self,
                                    conversation_history: List[Dict[str, str]],
                                    user_engagement: str,
                                    turn_count: int) -> str:
        """Valuta la forza della relazione con l'utente"""
        
        # Fattori che indicano una relazione forte
        strength_score = 0
        
        # Durata della conversazione
        if turn_count > 10:
            strength_score += 2
        elif turn_count > 5:
            strength_score += 1
        
        # Livello di engagement
        engagement_scores = {"high": 3, "medium": 1, "low": 0}
        strength_score += engagement_scores.get(user_engagement, 0)
        
        # Indicatori qualitativi dalle conversazioni
        if conversation_history:
            recent_text = " ".join([msg.get("user", "") for msg in conversation_history[-5:]])
            
            # Indicatori di fiducia
            trust_indicators = ["grazie", "hai ragione", "mi aiuti", "capisco", "ottimo"]
            strength_score += sum(1 for indicator in trust_indicators if indicator in recent_text.lower())
            
            # Condivisione di informazioni sensibili
            sensitive_topics = ["peso", "salute", "problemi", "difficoltà", "paura"]
            if any(topic in recent_text.lower() for topic in sensitive_topics):
                strength_score += 2
        
        if strength_score >= 6:
            return "strong"
        elif strength_score >= 3:
            return "established"
        else:
            return "building"
    
    def _identify_last_topic(self, conversation_history: List[Dict[str, str]]) -> str:
        """Identifica l'ultimo topic discusso"""
        
        if not conversation_history:
            return "introduction"
        
        last_exchange = conversation_history[-1]
        arnold_text = last_exchange.get("arnold", "") or ""
        arnold_text = arnold_text.lower()
        
        # Topic keywords mapping
        topic_keywords = {
            "goals": ["obiettivo", "target", "risultato", "raggiungere"],
            "eating_habits": ["mangiare", "alimentazione", "cibo", "pasti"],
            "activity": ["attività", "esercizio", "sport", "movimento"],
            "lifestyle": ["stile di vita", "routine", "giornata", "lavoro"],
            "health": ["salute", "benessere", "condizione", "medico"],
            "preferences": ["preferisci", "piace", "gradisci", "scelta"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in arnold_text for keyword in keywords):
                return topic
        
        return "general"
    
    def _identify_pending_followups(self,
                                  conversation_history: List[Dict[str, str]],
                                  checklist_context: Dict[str, Any]) -> List[str]:
        """Identifica follow-up che potrebbero essere necessari"""
        
        followups = []
        
        if not conversation_history:
            return followups
        
        last_exchange = conversation_history[-1]
        user_text = last_exchange.get("user", "").lower()
        
        # Risposte incomplete che richiedono follow-up
        incomplete_indicators = [
            "non so", "forse", "magari", "dipende", "vediamo", "mah", "boh"
        ]
        
        if any(indicator in user_text for indicator in incomplete_indicators):
            followups.append("clarify_previous_response")
        
        # Accenni a temi che meritano approfondimento
        deep_topics = {
            "stress": ["stress", "ansia", "preoccupato", "nervoso"],
            "health_issues": ["problema", "malattia", "medico", "dottore"],
            "emotional_eating": ["emozioni", "triste", "arrabbiato", "mangio quando"]
        }
        
        for topic, keywords in deep_topics.items():
            if any(keyword in user_text for keyword in keywords):
                followups.append(f"explore_{topic}")
        
        return followups
    
    def _should_exit_warmup(self, state: ConversationState, checklist_context: Dict[str, Any]) -> bool:
        """Determina se è ora di uscire dalla fase warmup"""
        return (state.turn_count >= 3 or 
                state.user_engagement in ["medium", "high"] or
                state.relationship_strength != "building")
    
    def _should_exit_profiling(self, state: ConversationState, checklist_context: Dict[str, Any]) -> bool:
        """Determina se è ora di uscire dalla fase profiling"""
        return state.turn_count >= 8 or state.user_engagement == "high"
    
    def _should_exit_assessment(self, state: ConversationState, checklist_context: Dict[str, Any]) -> bool:
        """Determina se è ora di uscire dalla fase assessment"""
        return state.information_completeness >= 0.7
    
    def _should_exit_planning(self, state: ConversationState, checklist_context: Dict[str, Any]) -> bool:
        """Determina se è ora di uscire dalla fase planning"""
        return state.information_completeness >= 0.9
    
    def _should_exit_implementation(self, state: ConversationState, checklist_context: Dict[str, Any]) -> bool:
        """Determina se è ora di uscire dalla fase implementation"""
        # Implementation è ongoing, quindi return False per ora
        return False
    
    def _get_next_phase(self, current_phase: ConversationPhase) -> ConversationPhase:
        """Restituisce la prossima fase logica"""
        phase_sequence = [
            ConversationPhase.WARMUP,
            ConversationPhase.PROFILING,
            ConversationPhase.ASSESSMENT,
            ConversationPhase.PLANNING,
            ConversationPhase.IMPLEMENTATION,
            ConversationPhase.MONITORING
        ]
        
        try:
            current_index = phase_sequence.index(current_phase)
            if current_index < len(phase_sequence) - 1:
                return phase_sequence[current_index + 1]
        except ValueError:
            pass
        
        return ConversationPhase.ASSESSMENT  # Fallback
    
    def _personalize_phase_guidance(self,
                                  base_guidance: Dict[str, Any],
                                  personality_profile: PersonalityProfile) -> Dict[str, Any]:
        """Personalizza la guidance per il profilo dell'utente"""
        
        personalized = base_guidance.copy()
        
        # Aggiustamenti per tipo di personalità
        if personality_profile.primary_type == "analytical":
            personalized["approach"] += " con focus su dati e logica"
            personalized["communication_style"] = "strutturato e basato su evidenze"
        elif personality_profile.primary_type == "emotional":
            personalized["approach"] += " con particolare attenzione all'aspetto emotivo"
            personalized["communication_style"] = "empatico e validante"
        elif personality_profile.primary_type == "practical":
            personalized["approach"] += " con focus su soluzioni concrete"
            personalized["communication_style"] = "diretto e orientato all'azione"
        elif personality_profile.primary_type == "social":
            personalized["approach"] += " con elementi di condivisione sociale"
            personalized["communication_style"] = "coinvolgente e collaborativo"
        
        return personalized
    
    def _load_phase_rules(self) -> Dict[str, Any]:
        """Carica le regole per le diverse fasi"""
        return {
            "warmup": {
                "min_turns": 2,
                "max_turns": 4,
                "success_metrics": ["user_comfort", "basic_rapport"]
            },
            "assessment": {
                "min_completeness": 0.7,
                "critical_checks": ["health_goals", "current_habits", "constraints"]
            }
        }
    
    def _load_transition_conditions(self) -> Dict[str, Any]:
        """Carica le condizioni per le transizioni di fase"""
        return {
            "warmup_to_profiling": {
                "user_engagement": "medium+",
                "turn_count": "3+"
            },
            "assessment_to_planning": {
                "information_completeness": "0.7+",
                "critical_gaps": "none"
            }
        }
    
    def _load_engagement_indicators(self) -> Dict[str, List[str]]:
        """Carica gli indicatori di engagement"""
        return {
            "high": [
                "detailed responses", "asks questions", "shares personal info",
                "expresses enthusiasm", "provides examples"
            ],
            "medium": [
                "adequate responses", "some detail", "basic cooperation"
            ],
            "low": [
                "short responses", "vague answers", "reluctant sharing",
                "frequent 'i don't know'"
            ]
        }