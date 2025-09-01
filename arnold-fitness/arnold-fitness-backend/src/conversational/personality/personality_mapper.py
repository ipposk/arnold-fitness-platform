"""
Personality Mapper - Mappa lo stile di scrittura a profili psicologici
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from .style_analyzer import WritingStyle


@dataclass
class PersonalityProfile:
    """Profilo psicologico dell'utente"""
    primary_type: str  # "analytical", "emotional", "practical", "social"
    communication_preference: str  # "direct", "gentle", "detailed", "encouraging"
    motivation_style: str  # "achievement", "security", "autonomy", "social"
    support_needs: str  # "high", "moderate", "low"
    information_processing: str  # "step_by_step", "big_picture", "example_based"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "primary_type": self.primary_type,
            "communication_preference": self.communication_preference,
            "motivation_style": self.motivation_style,
            "support_needs": self.support_needs,
            "information_processing": self.information_processing
        }


class PersonalityMapper:
    """Mappa gli stili di scrittura a profili psicologici per personalizzare l'approccio"""
    
    def __init__(self):
        self.personality_rules = self._load_personality_rules()
    
    def map_style_to_personality(self, writing_style: WritingStyle) -> PersonalityProfile:
        """Mappa uno stile di scrittura a un profilo psicologico"""
        
        # Determina il tipo primario
        primary_type = self._determine_primary_type(writing_style)
        
        # Determina le preferenze di comunicazione
        communication_preference = self._determine_communication_preference(writing_style)
        
        # Determina lo stile motivazionale
        motivation_style = self._determine_motivation_style(writing_style)
        
        # Determina i bisogni di supporto
        support_needs = self._determine_support_needs(writing_style)
        
        # Determina come processa le informazioni
        information_processing = self._determine_information_processing(writing_style)
        
        return PersonalityProfile(
            primary_type=primary_type,
            communication_preference=communication_preference,
            motivation_style=motivation_style,
            support_needs=support_needs,
            information_processing=information_processing
        )
    
    def _determine_primary_type(self, style: WritingStyle) -> str:
        """Determina il tipo di personalità primario"""
        
        # Analitico: tono analitico, livello tecnico alto, approccio formale
        if (style.emotional_tone == "analytical" or 
            style.technical_level == "advanced" or
            (style.formality == "formal" and style.verbosity == "verbose")):
            return "analytical"
        
        # Emotivo: tono emotivo, alto livello di apertura, energia variabile
        if (style.emotional_tone in ["emotional", "anxious", "frustrated"] or
            (style.openness == "very_open" and style.concern_level == "high")):
            return "emotional"
        
        # Sociale: alta apertura, energia alta, stile informale
        if (style.openness == "very_open" and 
            style.energy_level == "high" and 
            style.formality == "informal"):
            return "social"
        
        # Default: pratico
        return "practical"
    
    def _determine_communication_preference(self, style: WritingStyle) -> str:
        """Determina come l'utente preferisce essere comunicato"""
        
        # Diretto: breve, bassa apertura, tono neutro
        if (style.verbosity == "brief" and 
            style.openness == "reserved" and 
            style.emotional_tone == "neutral"):
            return "direct"
        
        # Gentile: alta preoccupazione, tono ansioso, energia bassa
        if (style.concern_level == "high" or 
            style.emotional_tone == "anxious" or
            style.energy_level == "low"):
            return "gentle"
        
        # Dettagliato: verboso, analitico, formale
        if (style.verbosity == "verbose" and 
            (style.emotional_tone == "analytical" or style.formality == "formal")):
            return "detailed"
        
        # Default: incoraggiante
        return "encouraging"
    
    def _determine_motivation_style(self, style: WritingStyle) -> str:
        """Determina cosa motiva l'utente"""
        
        # Achievement: tono speranzoso, energia alta, apertura moderata
        if (style.emotional_tone == "hopeful" and style.energy_level == "high"):
            return "achievement"
        
        # Security: alta preoccupazione, tono ansioso
        if (style.concern_level == "high" or style.emotional_tone == "anxious"):
            return "security"
        
        # Social: alta apertura, stile informale, energia alta
        if (style.openness == "very_open" and 
            style.formality == "informal" and 
            style.energy_level == "high"):
            return "social"
        
        # Default: autonomia
        return "autonomy"
    
    def _determine_support_needs(self, style: WritingStyle) -> str:
        """Determina quanto supporto emotivo serve"""
        
        # Alto supporto: alta preoccupazione, tono emotivo/ansioso
        if (style.concern_level == "high" or 
            style.emotional_tone in ["anxious", "frustrated", "emotional"]):
            return "high"
        
        # Basso supporto: tono analitico, bassa apertura, approccio diretto
        if (style.emotional_tone == "analytical" and 
            style.openness == "reserved" and
            style.verbosity == "brief"):
            return "low"
        
        # Default: moderato
        return "moderate"
    
    def _determine_information_processing(self, style: WritingStyle) -> str:
        """Determina come l'utente processa meglio le informazioni"""
        
        # Step by step: alta preoccupazione, tono ansioso, supporto alto
        if (style.concern_level == "high" or style.emotional_tone == "anxious"):
            return "step_by_step"
        
        # Big picture: analitico, verboso, livello tecnico alto
        if (style.emotional_tone == "analytical" and 
            style.verbosity == "verbose" and
            style.technical_level in ["intermediate", "advanced"]):
            return "big_picture"
        
        # Example based: alta apertura, tono emotivo, energia alta
        if (style.openness == "very_open" and 
            style.emotional_tone in ["emotional", "hopeful"]):
            return "example_based"
        
        # Default: step by step (più sicuro)
        return "step_by_step"
    
    def _load_personality_rules(self) -> Dict[str, Any]:
        """Carica le regole per la mappatura personalità (future espansioni)"""
        return {
            "analytical": {
                "preferred_language": "tecnico e preciso",
                "question_style": "strutturate e logiche",
                "feedback_style": "basato su dati e evidenze"
            },
            "emotional": {
                "preferred_language": "empatico e comprensivo",
                "question_style": "aperte e validanti",
                "feedback_style": "supportivo e incoraggiante"
            },
            "practical": {
                "preferred_language": "diretto e concreto",
                "question_style": "specifiche e orientate all'azione",
                "feedback_style": "pratico e applicabile"
            },
            "social": {
                "preferred_language": "caloroso e coinvolgente",
                "question_style": "conversazionali e condivisive",
                "feedback_style": "collaborativo e sociale"
            }
        }
    
    def get_personality_insights(self, profile: PersonalityProfile) -> Dict[str, str]:
        """Restituisce insights su come approcciarsi a questo profilo"""
        base_insights = self.personality_rules.get(profile.primary_type, {})
        
        return {
            **base_insights,
            "communication_tip": self._get_communication_tip(profile),
            "motivation_approach": self._get_motivation_approach(profile),
            "support_strategy": self._get_support_strategy(profile)
        }
    
    def _get_communication_tip(self, profile: PersonalityProfile) -> str:
        """Suggerimenti per comunicare con questo profilo"""
        tips = {
            "direct": "Essere concisi e andare dritti al punto",
            "gentle": "Usare linguaggio rassicurante e validante",
            "detailed": "Fornire spiegazioni complete e strutturate", 
            "encouraging": "Mantenere un tono positivo e motivante"
        }
        return tips.get(profile.communication_preference, "Adattarsi al suo stile")
    
    def _get_motivation_approach(self, profile: PersonalityProfile) -> str:
        """Approccio motivazionale per questo profilo"""
        approaches = {
            "achievement": "Focalizzarsi su obiettivi e risultati misurabili",
            "security": "Enfatizzare sicurezza e benefici per la salute",
            "autonomy": "Rispettare l'indipendenza e offrire scelte",
            "social": "Collegare ai benefici sociali e relazionali"
        }
        return approaches.get(profile.motivation_style, "Approccio equilibrato")
    
    def _get_support_strategy(self, profile: PersonalityProfile) -> str:
        """Strategia di supporto per questo profilo"""
        strategies = {
            "high": "Fornire frequente rassicurazione e validazione emotiva",
            "moderate": "Bilanciare supporto emotivo e informazioni pratiche",
            "low": "Concentrarsi su fatti e lasciare spazio all'autonomia"
        }
        return strategies.get(profile.support_needs, "Supporto bilanciato")