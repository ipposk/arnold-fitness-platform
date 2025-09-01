"""
Question Selector - Seleziona la prossima domanda basandosi sul progresso checklist e profilo utente
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from ..personality_profiler import PersonalityProfile, WritingStyle


@dataclass
class QuestionContext:
    """Contesto per la selezione delle domande"""
    current_phase: str
    completed_checks: List[str]
    in_progress_checks: List[str] 
    pending_checks: List[str]
    conversation_turn: int
    user_comfort_level: str  # "low", "medium", "high"
    critical_gaps: List[str]  # Informazioni critiche mancanti


class QuestionSelector:
    """Seleziona la prossima domanda più appropriata basandosi su checklist e profilo utente"""
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        self.priority_mapping = self._load_priority_mapping()
        self.flow_rules = self._load_flow_rules()
    
    def select_next_question(self, 
                           checklist_context: Dict[str, Any],
                           personality_profile: PersonalityProfile,
                           writing_style: WritingStyle,
                           conversation_history: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Seleziona la prossima domanda più appropriata"""
        
        # Analizza il contesto attuale
        question_context = self._analyze_context(checklist_context, conversation_history)
        
        # Trova candidati per la prossima domanda
        candidates = self._find_question_candidates(
            question_context, 
            checklist_context,
            personality_profile
        )
        
        if not candidates:
            return None
        
        # Seleziona la migliore tra i candidati
        selected = self._select_best_candidate(
            candidates,
            personality_profile,
            writing_style,
            question_context
        )
        
        return selected
    
    def _analyze_context(self, checklist_context: Dict[str, Any], 
                        conversation_history: List[Dict[str, str]]) -> QuestionContext:
        """Analizza il contesto attuale per la selezione della domanda"""
        
        # Estrai informazioni dalla checklist
        completed_checks = []
        in_progress_checks = []
        pending_checks = []
        current_phase = "assessment"  # Default
        
        checklist = checklist_context.get("checklist", [])
        
        for phase in checklist:
            phase_title = phase.get("title", "").lower()
            if "assessment" in phase_title:
                current_phase = "assessment"
            elif "planning" in phase_title:
                current_phase = "planning"
            elif "implementation" in phase_title:
                current_phase = "implementation"
            
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    check_id = check.get("check_id", "")
                    state = check.get("state", "pending")
                    
                    if state == "done":
                        completed_checks.append(check_id)
                    elif state == "in_progress":
                        in_progress_checks.append(check_id)
                    else:
                        pending_checks.append(check_id)
        
        # Determina il livello di comfort basandosi sulla storia
        comfort_level = self._assess_comfort_level(conversation_history)
        
        # Identifica gap critici
        critical_gaps = self._identify_critical_gaps(completed_checks, current_phase)
        
        return QuestionContext(
            current_phase=current_phase,
            completed_checks=completed_checks,
            in_progress_checks=in_progress_checks,
            pending_checks=pending_checks,
            conversation_turn=len(conversation_history),
            user_comfort_level=comfort_level,
            critical_gaps=critical_gaps
        )
    
    def _find_question_candidates(self, 
                                question_context: QuestionContext,
                                checklist_context: Dict[str, Any],
                                personality_profile: PersonalityProfile) -> List[Dict[str, Any]]:
        """Trova le domande candidate per il prossimo turno"""
        
        candidates = []
        
        # 1. Gap critici hanno priorità massima
        if question_context.critical_gaps:
            for gap in question_context.critical_gaps:
                candidate = self._create_candidate_from_gap(gap, personality_profile)
                if candidate:
                    candidate["priority"] = "critical"
                    candidates.append(candidate)
        
        # 2. Check in progress da completare
        if question_context.in_progress_checks:
            for check_id in question_context.in_progress_checks:
                candidate = self._create_candidate_from_check(
                    check_id, checklist_context, personality_profile
                )
                if candidate:
                    candidate["priority"] = "high"
                    candidates.append(candidate)
        
        # 3. Prossimi check logici nella sequenza
        logical_next = self._find_logical_next_checks(
            question_context, checklist_context, personality_profile
        )
        for check_info in logical_next:
            check_info["priority"] = "medium"
            candidates.append(check_info)
        
        # 4. Follow-up basati su risposte precedenti
        followups = self._generate_followup_questions(
            question_context, personality_profile
        )
        for followup in followups:
            followup["priority"] = "low"
            candidates.append(followup)
        
        return candidates
    
    def _select_best_candidate(self, 
                             candidates: List[Dict[str, Any]],
                             personality_profile: PersonalityProfile,
                             writing_style: WritingStyle,
                             question_context: QuestionContext) -> Dict[str, Any]:
        """Seleziona il miglior candidato tra le domande disponibili"""
        
        # Ordina per priorità
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        candidates.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 1), reverse=True)
        
        # Filtra in base al livello di comfort
        suitable_candidates = self._filter_by_comfort_level(candidates, question_context)
        
        if not suitable_candidates:
            suitable_candidates = candidates  # Fallback
        
        # Seleziona basandosi sul profilo di personalità
        best_candidate = self._choose_by_personality_fit(
            suitable_candidates, personality_profile, writing_style
        )
        
        return best_candidate
    
    def _assess_comfort_level(self, conversation_history: List[Dict[str, str]]) -> str:
        """Valuta il livello di comfort dell'utente nella conversazione"""
        
        if len(conversation_history) < 2:
            return "low"
        
        # Analizza gli ultimi messaggi per indicatori di comfort
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
        
        comfort_indicators = {
            "high": ["sì esatto", "perfetto", "assolutamente", "hai ragione", "mi piace", "fantastico"],
            "low": ["non so", "forse", "magari", "boh", "mah", "difficile", "complicato"]
        }
        
        high_score = 0
        low_score = 0
        
        for msg in recent_messages:
            user_text = msg.get("user", "").lower()
            
            for indicator in comfort_indicators["high"]:
                if indicator in user_text:
                    high_score += 1
            
            for indicator in comfort_indicators["low"]:
                if indicator in user_text:
                    low_score += 1
        
        if high_score > low_score:
            return "high"
        elif low_score > high_score:
            return "low"
        else:
            return "medium"
    
    def _identify_critical_gaps(self, completed_checks: List[str], current_phase: str) -> List[str]:
        """Identifica gap critici nelle informazioni raccolte"""
        
        critical_by_phase = {
            "assessment": [
                "basic_demographics",
                "health_goals", 
                "current_eating_habits",
                "activity_level"
            ],
            "planning": [
                "dietary_preferences",
                "schedule_constraints",
                "cooking_skills"
            ],
            "implementation": [
                "meal_prep_capacity",
                "support_system",
                "tracking_preferences"
            ]
        }
        
        required_for_phase = critical_by_phase.get(current_phase, [])
        return [gap for gap in required_for_phase if gap not in completed_checks]
    
    def _create_candidate_from_gap(self, gap: str, personality_profile: PersonalityProfile) -> Optional[Dict[str, Any]]:
        """Crea una domanda candidata da un gap critico"""
        
        gap_questions = {
            "basic_demographics": {
                "check_id": "basic_demographics",
                "question_type": "demographic_info",
                "template_key": "demographics",
                "topic": "informazioni di base"
            },
            "health_goals": {
                "check_id": "health_goals",
                "question_type": "goal_exploration", 
                "template_key": "goals",
                "topic": "obiettivi di salute"
            },
            "current_eating_habits": {
                "check_id": "current_eating_habits",
                "question_type": "habit_assessment",
                "template_key": "eating_habits",
                "topic": "abitudini alimentari attuali"
            },
            "activity_level": {
                "check_id": "activity_level", 
                "question_type": "activity_assessment",
                "template_key": "activity",
                "topic": "livello di attività fisica"
            }
        }
        
        return gap_questions.get(gap)
    
    def _create_candidate_from_check(self, 
                                   check_id: str,
                                   checklist_context: Dict[str, Any],
                                   personality_profile: PersonalityProfile) -> Optional[Dict[str, Any]]:
        """Crea una domanda candidata da un check in progress"""
        
        # Trova il check nella checklist
        checklist = checklist_context.get("checklist", [])
        
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    if check.get("check_id") == check_id:
                        return {
                            "check_id": check_id,
                            "question_type": "followup",
                            "template_key": check_id,
                            "topic": check.get("description", "informazioni aggiuntive"),
                            "check_data": check
                        }
        
        return None
    
    def _find_logical_next_checks(self,
                                question_context: QuestionContext,
                                checklist_context: Dict[str, Any],
                                personality_profile: PersonalityProfile) -> List[Dict[str, Any]]:
        """Trova i prossimi check logici nella sequenza"""
        
        candidates = []
        checklist = checklist_context.get("checklist", [])
        
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    check_id = check.get("check_id", "")
                    
                    # Skip completed or in-progress checks
                    if (check_id in question_context.completed_checks or
                        check_id in question_context.in_progress_checks):
                        continue
                    
                    # Check if dependencies are met
                    if self._check_dependencies_met(check, question_context.completed_checks):
                        candidate = {
                            "check_id": check_id,
                            "question_type": "assessment",
                            "template_key": check_id,
                            "topic": check.get("description", ""),
                            "check_data": check,
                            "phase": phase.get("title", "")
                        }
                        candidates.append(candidate)
        
        # Limita a 3 candidati per non sovraccaricare
        return candidates[:3]
    
    def _generate_followup_questions(self,
                                   question_context: QuestionContext,
                                   personality_profile: PersonalityProfile) -> List[Dict[str, Any]]:
        """Genera domande di follow-up basate sul contesto"""
        
        followups = []
        
        # Se siamo all'inizio, genera domande di warm-up
        if question_context.conversation_turn < 3:
            followups.extend(self._get_warmup_questions(personality_profile))
        
        # Se l'utente sembra a disagio, genera domande più soft
        if question_context.user_comfort_level == "low":
            followups.extend(self._get_comfort_building_questions(personality_profile))
        
        return followups
    
    def _get_warmup_questions(self, personality_profile: PersonalityProfile) -> List[Dict[str, Any]]:
        """Genera domande di riscaldamento per l'inizio della conversazione"""
        
        warmup_by_type = {
            "analytical": [
                {
                    "question_type": "warmup",
                    "template_key": "analytical_warmup",
                    "topic": "approccio metodico alla salute",
                    "priority": "medium"
                }
            ],
            "emotional": [
                {
                    "question_type": "warmup", 
                    "template_key": "emotional_warmup",
                    "topic": "sentimenti riguardo alla salute",
                    "priority": "medium"
                }
            ],
            "practical": [
                {
                    "question_type": "warmup",
                    "template_key": "practical_warmup", 
                    "topic": "sfide pratiche attuali",
                    "priority": "medium"
                }
            ],
            "social": [
                {
                    "question_type": "warmup",
                    "template_key": "social_warmup",
                    "topic": "contesto sociale dell'alimentazione",
                    "priority": "medium"
                }
            ]
        }
        
        return warmup_by_type.get(personality_profile.primary_type, [])
    
    def _get_comfort_building_questions(self, personality_profile: PersonalityProfile) -> List[Dict[str, Any]]:
        """Genera domande per aumentare il comfort dell'utente"""
        
        return [
            {
                "question_type": "comfort_building",
                "template_key": "reassurance",
                "topic": "rassicurazione e supporto",
                "priority": "high"
            }
        ]
    
    def _filter_by_comfort_level(self, candidates: List[Dict[str, Any]], 
                                question_context: QuestionContext) -> List[Dict[str, Any]]:
        """Filtra i candidati in base al livello di comfort dell'utente"""
        
        if question_context.user_comfort_level == "low":
            # Evita domande troppo personali o complesse
            sensitive_topics = ["weight_history", "body_image", "eating_disorders", "medical_history"]
            return [c for c in candidates if c.get("check_id", "") not in sensitive_topics]
        
        return candidates
    
    def _choose_by_personality_fit(self,
                                 candidates: List[Dict[str, Any]],
                                 personality_profile: PersonalityProfile,
                                 writing_style: WritingStyle) -> Dict[str, Any]:
        """Sceglie il candidato che meglio si adatta alla personalità"""
        
        # Se c'è solo un candidato, restituiscilo
        if len(candidates) == 1:
            return candidates[0]
        
        # Scoring basato su personality fit
        scored_candidates = []
        
        for candidate in candidates:
            score = 0
            
            # Bonus per tipo di personalità
            if personality_profile.primary_type == "analytical" and "assessment" in candidate.get("question_type", ""):
                score += 3
            elif personality_profile.primary_type == "emotional" and "warmup" in candidate.get("question_type", ""):
                score += 3
            elif personality_profile.primary_type == "practical" and "habit" in candidate.get("template_key", ""):
                score += 3
            elif personality_profile.primary_type == "social" and "social" in candidate.get("template_key", ""):
                score += 3
            
            # Bonus per stile di comunicazione
            if writing_style.verbosity == "brief" and candidate.get("priority") == "critical":
                score += 2
            elif writing_style.verbosity == "verbose" and "assessment" in candidate.get("question_type", ""):
                score += 2
            
            scored_candidates.append((candidate, score))
        
        # Restituisci il candidato con score più alto
        best_candidate = max(scored_candidates, key=lambda x: x[1])
        return best_candidate[0]
    
    def _check_dependencies_met(self, check: Dict[str, Any], completed_checks: List[str]) -> bool:
        """Verifica se le dipendenze di un check sono soddisfatte"""
        
        # Per ora, implementazione semplice
        # In futuro, si può aggiungere logica più complessa per le dipendenze
        
        dependencies = check.get("dependencies", [])
        return all(dep in completed_checks for dep in dependencies)
    
    def _load_question_templates(self) -> Dict[str, Any]:
        """Carica i template delle domande"""
        
        # Questi template saranno usati dall'Adaptive Prompting System
        return {
            "demographics": {
                "analytical": "Per personalizzare al meglio i miei consigli, ho bisogno di alcuni dati specifici. Potresti dirmi la tua età e genere?",
                "emotional": "Per conoscerti meglio e offrirti il supporto più adatto, mi piacerebbe sapere qualcosa in più su di te. Ti va di condividere la tua età?",
                "practical": "Per darti consigli pratici e mirati, dimmi: quanti anni hai e qual è la tua situazione attuale?",
                "social": "Iniziamo a conoscerci! Mi piacerebbe sapere qualcosa in più su di te - età, situazione di vita..."
            },
            "goals": {
                "analytical": "Quali sono i tuoi obiettivi specifici e misurabili per la salute e l'alimentazione?",
                "emotional": "Cosa speri di raggiungere in questo percorso? Come ti piacerebbe sentirti?",
                "practical": "Quale risultato concreto vorresti ottenere nei prossimi mesi?",
                "social": "Condividiamo gli obiettivi! Cosa ti piacerebbe migliorare nella tua vita?"
            }
        }
    
    def _load_priority_mapping(self) -> Dict[str, int]:
        """Carica la mappatura delle priorità dei check"""
        
        return {
            "basic_demographics": 10,
            "health_goals": 9,
            "current_eating_habits": 8,
            "activity_level": 7,
            "dietary_preferences": 6,
            "schedule_constraints": 5
        }
    
    def _load_flow_rules(self) -> Dict[str, Any]:
        """Carica le regole per il flusso conversazionale"""
        
        return {
            "max_questions_per_turn": 1,
            "warmup_turns": 2,
            "comfort_building_priority": "high",
            "critical_gap_threshold": 3
        }