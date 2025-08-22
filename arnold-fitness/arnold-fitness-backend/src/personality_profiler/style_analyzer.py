"""
Style Analyzer - Analizza lo stile di scrittura dell'utente
"""

import re
import json
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class WritingStyle:
    """Rappresenta lo stile di scrittura di un utente"""
    verbosity: str  # "brief", "moderate", "verbose"
    emotional_tone: str  # "analytical", "emotional", "neutral", "anxious"
    formality: str  # "informal", "semi_formal", "formal"
    technical_level: str  # "basic", "intermediate", "advanced"
    openness: str  # "reserved", "moderate", "very_open"
    energy_level: str  # "low", "moderate", "high"
    concern_level: str  # "low", "moderate", "high"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "verbosity": self.verbosity,
            "emotional_tone": self.emotional_tone,
            "formality": self.formality,
            "technical_level": self.technical_level,
            "openness": self.openness,
            "energy_level": self.energy_level,
            "concern_level": self.concern_level
        }


class StyleAnalyzer:
    """Analizza lo stile di scrittura dell'utente per personalizzare le risposte"""
    
    def __init__(self):
        self.emotional_keywords = {
            "anxious": ["preoccupato", "ansia", "stress", "nervoso", "paura", "timido", "insicuro"],
            "frustrated": ["frustrato", "arrabbiato", "stufo", "difficile", "impossibile", "non riesco"],
            "hopeful": ["speranza", "voglio", "desidero", "obiettivo", "migliorare", "cambiare"],
            "analytical": ["dati", "numeri", "specifico", "preciso", "esatto", "calcolare", "misurare"],
            "emotional": ["sento", "provo", "emozioni", "cuore", "anima", "felice", "triste"]
        }
        
        self.formality_indicators = {
            "informal": ["ciao", "ok", "tipo", "roba", "boh", "mah", "diciamo"],
            "formal": ["salve", "cortesemente", "ringrazio", "distinti saluti", "la prego"]
        }
        
        self.technical_indicators = {
            "basic": ["mangiare", "cibo", "peso", "dieta", "sport"],
            "intermediate": ["calorie", "proteine", "carboidrati", "metabolismo", "allenamento"],
            "advanced": ["macronutrienti", "TDEE", "deficit calorico", "composizione corporea", "periodizzazione"]
        }

    def analyze_text(self, text: str) -> WritingStyle:
        """Analizza un testo e restituisce il profilo stilistico"""
        if not text or not text.strip():
            return self._get_default_style()
            
        text_lower = text.lower()
        
        return WritingStyle(
            verbosity=self._analyze_verbosity(text),
            emotional_tone=self._analyze_emotional_tone(text_lower),
            formality=self._analyze_formality(text_lower),
            technical_level=self._analyze_technical_level(text_lower),
            openness=self._analyze_openness(text),
            energy_level=self._analyze_energy_level(text),
            concern_level=self._analyze_concern_level(text_lower)
        )
    
    def analyze_conversation_history(self, messages: List[str]) -> WritingStyle:
        """Analizza una serie di messaggi per un profilo più accurato"""
        if not messages:
            return self._get_default_style()
            
        # Combina tutti i messaggi
        combined_text = " ".join(messages)
        base_style = self.analyze_text(combined_text)
        
        # Affina l'analisi basandosi su pattern nella conversazione
        return self._refine_analysis(base_style, messages)
    
    def _analyze_verbosity(self, text: str) -> str:
        """Analizza la verbosità del testo"""
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        
        if word_count < 10:
            return "brief"
        elif word_count < 30:
            return "moderate"
        else:
            return "verbose"
    
    def _analyze_emotional_tone(self, text_lower: str) -> str:
        """Analizza il tono emotivo del testo"""
        emotion_scores = {}
        
        for emotion, keywords in self.emotional_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if not emotion_scores:
            return "neutral"
            
        return max(emotion_scores, key=emotion_scores.get)
    
    def _analyze_formality(self, text_lower: str) -> str:
        """Analizza il livello di formalità"""
        informal_score = sum(1 for word in self.formality_indicators["informal"] 
                           if word in text_lower)
        formal_score = sum(1 for word in self.formality_indicators["formal"] 
                         if word in text_lower)
        
        if formal_score > informal_score:
            return "formal"
        elif informal_score > 0:
            return "informal"
        else:
            return "semi_formal"
    
    def _analyze_technical_level(self, text_lower: str) -> str:
        """Analizza il livello di competenza tecnica"""
        tech_scores = {}
        
        for level, keywords in self.technical_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            tech_scores[level] = score
        
        max_level = max(tech_scores, key=tech_scores.get)
        if tech_scores[max_level] == 0:
            return "basic"
        return max_level
    
    def _analyze_openness(self, text: str) -> str:
        """Analizza il livello di apertura/condivisione"""
        personal_indicators = ["io", "mi", "mio", "mia", "sono", "ho", "mi sento"]
        details_indicators = ["perché", "infatti", "cioè", "ad esempio", "specificamente"]
        
        personal_score = sum(1 for indicator in personal_indicators 
                           if indicator in text.lower())
        details_score = sum(1 for indicator in details_indicators 
                          if indicator in text.lower())
        
        total_score = personal_score + details_score
        
        if total_score >= 5:
            return "very_open"
        elif total_score >= 2:
            return "moderate"
        else:
            return "reserved"
    
    def _analyze_energy_level(self, text: str) -> str:
        """Analizza il livello di energia nel testo"""
        high_energy_indicators = ["!", "?", "davvero", "fantastico", "ottimo", "perfetto"]
        low_energy_indicators = ["...", "mah", "boh", "non so", "forse", "magari"]
        
        high_score = sum(1 for indicator in high_energy_indicators 
                        if indicator in text.lower())
        low_score = sum(1 for indicator in low_energy_indicators 
                       if indicator in text.lower())
        
        # Conta anche la punteggiatura
        high_score += text.count('!') + text.count('?')
        low_score += text.count('...')
        
        if high_score > low_score and high_score > 0:
            return "high"
        elif low_score > 0:
            return "low"
        else:
            return "moderate"
    
    def _analyze_concern_level(self, text_lower: str) -> str:
        """Analizza il livello di preoccupazione"""
        high_concern = ["problema", "difficoltà", "preoccupato", "ansia", "stress", 
                       "non riesco", "fallimento", "sbagliato", "paura"]
        
        concern_score = sum(1 for word in high_concern if word in text_lower)
        
        if concern_score >= 2:
            return "high"
        elif concern_score >= 1:
            return "moderate"
        else:
            return "low"
    
    def _refine_analysis(self, base_style: WritingStyle, messages: List[str]) -> WritingStyle:
        """Affina l'analisi basandosi su pattern nella conversazione"""
        # Se l'utente diventa più aperto nel corso della conversazione
        if len(messages) > 2:
            recent_openness = self._analyze_openness(" ".join(messages[-2:]))
            if recent_openness == "very_open" and base_style.openness == "moderate":
                base_style.openness = "very_open"
        
        return base_style
    
    def _get_default_style(self) -> WritingStyle:
        """Restituisce uno stile di default per input vuoti"""
        return WritingStyle(
            verbosity="moderate",
            emotional_tone="neutral",
            formality="semi_formal",
            technical_level="basic",
            openness="moderate",
            energy_level="moderate",
            concern_level="moderate"
        )