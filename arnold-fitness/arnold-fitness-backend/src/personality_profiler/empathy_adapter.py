"""
Empathy Adapter - Adatta il tono e lo stile di Arnold al profilo dell'utente
"""

from typing import Dict, List, Any
from .personality_mapper import PersonalityProfile
from .style_analyzer import WritingStyle


class EmpathyAdapter:
    """Adatta il linguaggio e l'approccio di Arnold al profilo psicologico dell'utente"""
    
    def __init__(self):
        self.tone_templates = self._load_tone_templates()
        self.response_modifiers = self._load_response_modifiers()
    
    def adapt_tone(self, base_message: str, personality_profile: PersonalityProfile, 
                   writing_style: WritingStyle, context: Dict[str, Any] = None) -> str:
        """Adatta il tono di un messaggio al profilo dell'utente"""
        
        # Applica modificatori basati sul profilo
        adapted_message = self._apply_personality_modifiers(
            base_message, personality_profile
        )
        
        # Applica modificatori basati sullo stile di scrittura
        adapted_message = self._apply_style_modifiers(
            adapted_message, writing_style
        )
        
        # Applica modificatori contestuali
        if context:
            adapted_message = self._apply_context_modifiers(
                adapted_message, context
            )
        
        return adapted_message
    
    def get_greeting_style(self, personality_profile: PersonalityProfile) -> str:
        """Restituisce uno stile di saluto personalizzato"""
        greetings = {
            "analytical": "Ciao! Sono Arnold. Mi concentro su approcci basati su evidenze per il benessere nutrizionale.",
            "emotional": "Ciao! Sono Arnold, il tuo supporto nel percorso di benessere. Sono qui per ascoltarti e comprenderti.",
            "practical": "Ciao! Sono Arnold. Lavoriamo insieme per trovare soluzioni pratiche per la tua alimentazione.",
            "social": "Ciao! Sono Arnold! Sono entusiasta di iniziare questo percorso insieme a te."
        }
        
        return greetings.get(personality_profile.primary_type, 
                           "Ciao! Sono Arnold, il tuo consulente nutrizionale AI.")
    
    def get_question_style(self, base_question: str, personality_profile: PersonalityProfile) -> str:
        """Adatta lo stile di una domanda al profilo"""
        
        if personality_profile.communication_preference == "direct":
            return self._make_direct(base_question)
        elif personality_profile.communication_preference == "gentle":
            return self._make_gentle(base_question)
        elif personality_profile.communication_preference == "detailed":
            return self._make_detailed(base_question)
        else:  # encouraging
            return self._make_encouraging(base_question)
    
    def get_feedback_style(self, base_feedback: str, personality_profile: PersonalityProfile,
                          writing_style: WritingStyle) -> str:
        """Adatta lo stile del feedback al profilo"""
        
        feedback = base_feedback
        
        # Adatta in base al tipo primario
        if personality_profile.primary_type == "analytical":
            feedback = self._add_analytical_elements(feedback)
        elif personality_profile.primary_type == "emotional":
            feedback = self._add_emotional_support(feedback)
        elif personality_profile.primary_type == "social":
            feedback = self._add_social_elements(feedback)
        
        # Adatta in base al livello di supporto richiesto
        if personality_profile.support_needs == "high":
            feedback = self._add_extra_support(feedback)
        
        return feedback
    
    def _apply_personality_modifiers(self, message: str, profile: PersonalityProfile) -> str:
        """Applica modificatori basati sul profilo di personalità"""
        
        # Modificatori per tipo primario
        if profile.primary_type == "analytical":
            message = self._add_precision_language(message)
        elif profile.primary_type == "emotional":
            message = self._add_empathy_language(message)
        elif profile.primary_type == "practical":
            message = self._add_action_language(message)
        elif profile.primary_type == "social":
            message = self._add_social_language(message)
        
        return message
    
    def _apply_style_modifiers(self, message: str, style: WritingStyle) -> str:
        """Applica modificatori basati sullo stile di scrittura"""
        
        # Adatta alla verbosità
        if style.verbosity == "brief":
            message = self._make_concise(message)
        elif style.verbosity == "verbose":
            message = self._make_detailed(message)
        
        # Adatta al livello di energia
        if style.energy_level == "high":
            message = self._increase_energy(message)
        elif style.energy_level == "low":
            message = self._decrease_energy(message)
        
        # Adatta al livello di preoccupazione
        if style.concern_level == "high":
            message = self._add_reassurance(message)
        
        return message
    
    def _apply_context_modifiers(self, message: str, context: Dict[str, Any]) -> str:
        """Applica modificatori contestuali"""
        
        # Se è l'inizio della conversazione
        if context.get("is_first_interaction", False):
            message = self._add_welcome_tone(message)
        
        # Se l'utente sembra frustrato dai messaggi precedenti
        if context.get("user_frustration_level", 0) > 0:
            message = self._add_understanding_tone(message)
        
        # Se si sta discutendo un topic sensibile
        if context.get("sensitive_topic", False):
            message = self._add_sensitivity(message)
        
        return message
    
    # Modificatori di stile specifici
    
    def _make_direct(self, text: str) -> str:
        """Rende il testo più diretto"""
        # Rimuove preamboli non necessari
        direct_starters = ["Parlami di", "Dimmi", "Quale è"]
        for starter in direct_starters:
            if text.startswith("Potresti dirmi"):
                text = text.replace("Potresti dirmi", "Dimmi")
            if text.startswith("Mi piacerebbe sapere"):
                text = text.replace("Mi piacerebbe sapere", "Dimmi")
        return text
    
    def _make_gentle(self, text: str) -> str:
        """Rende il testo più gentile e rassicurante"""
        gentle_prefixes = [
            "Non c'è fretta, ma mi piacerebbe sapere",
            "Quando ti senti comodo/a di condividere",
            "Solo se ti va di parlarmene"
        ]
        
        # Aggiungi un prefixo gentile se il testo è troppo diretto
        if text.startswith(("Dimmi", "Quale", "Come")):
            return f"{gentle_prefixes[0]}: {text.lower()}"
        
        return text
    
    def _make_detailed(self, text: str) -> str:
        """Rende il testo più dettagliato e strutturato"""
        if "?" in text:
            # Aggiungi contesto alla domanda
            return f"Per comprenderti meglio, {text.lower()} Questo mi aiuterà a personalizzare i miei consigli per te."
        return text
    
    def _make_encouraging(self, text: str) -> str:
        """Rende il testo più incoraggiante"""
        encouraging_additions = [
            "Stai facendo un ottimo lavoro nel prenderti cura di te!",
            "Ogni passo che fai verso il benessere conta!",
            "È fantastico che tu stia investendo nella tua salute!"
        ]
        
        # Aggiungi incoraggiamento occasionale
        import random
        if random.random() > 0.7:  # 30% chance
            return f"{text} {random.choice(encouraging_additions)}"
        
        return text
    
    def _add_precision_language(self, text: str) -> str:
        """Aggiunge linguaggio preciso per personalità analitiche"""
        replacements = {
            "alcuni": "specifici",
            "cosa": "quali dati",
            "come": "in che modo specifico",
            "quanto": "quale quantità esatta"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _add_empathy_language(self, text: str) -> str:
        """Aggiunge linguaggio empatico per personalità emotive"""
        empathy_additions = [
            "Capisco che possa essere difficile",
            "I tuoi sentimenti sono completamente validi",
            "Non sei solo/a in questo percorso"
        ]
        
        # Aggiungi validazione emotiva occasionale
        import random
        if random.random() > 0.8:  # 20% chance
            return f"{random.choice(empathy_additions)}. {text}"
        
        return text
    
    def _add_action_language(self, text: str) -> str:
        """Aggiunge linguaggio orientato all'azione per personalità pratiche"""
        action_words = {
            "capire": "identificare e agire su",
            "sapere": "determinare per poi applicare",
            "conoscere": "scoprire per utilizzare"
        }
        
        for old, new in action_words.items():
            text = text.replace(old, new)
        
        return text
    
    def _add_social_language(self, text: str) -> str:
        """Aggiunge linguaggio sociale per personalità sociali"""
        social_elements = [
            "insieme",
            "condividiamo",
            "il nostro percorso",
            "la nostra conversazione"
        ]
        
        # Sostituisci linguaggio individuale con linguaggio sociale
        text = text.replace("il tuo", "il nostro")
        text = text.replace("tu", "noi")
        
        return text
    
    def _make_concise(self, text: str) -> str:
        """Rende il testo più conciso"""
        # Rimuovi frasi ridondanti
        redundant_phrases = [
            "come sai, ",
            "ovviamente, ",
            "naturalmente, ",
            "di solito, "
        ]
        
        for phrase in redundant_phrases:
            text = text.replace(phrase, "")
        
        return text
    
    def _increase_energy(self, text: str) -> str:
        """Aumenta l'energia del testo"""
        if not text.endswith("!") and ("?" not in text):
            text = text.rstrip(".") + "!"
        
        energetic_words = {
            "bene": "fantastico",
            "buono": "ottimo",
            "ok": "perfetto"
        }
        
        for old, new in energetic_words.items():
            text = text.replace(old, new)
        
        return text
    
    def _decrease_energy(self, text: str) -> str:
        """Diminuisce l'energia del testo"""
        # Rimuovi punti esclamativi multipli
        text = text.replace("!!", ".")
        text = text.replace("!", ".")
        
        return text
    
    def _add_reassurance(self, text: str) -> str:
        """Aggiunge rassicurazione per utenti preoccupati"""
        reassuring_additions = [
            "Non c'è niente di sbagliato in quello che senti.",
            "È normale avere queste preoccupazioni.",
            "Prenderemo tutto con calma, un passo alla volta."
        ]
        
        import random
        reassurance = random.choice(reassuring_additions)
        return f"{reassurance} {text}"
    
    def _load_tone_templates(self) -> Dict[str, List[str]]:
        """Carica template di tono per diversi profili"""
        return {
            "analytical": [
                "Basandoci sui dati che mi hai fornito...",
                "L'evidenza suggerisce che...",
                "Analizzando la situazione..."
            ],
            "emotional": [
                "Sento che stai attraversando...",
                "È comprensibile che tu ti senta...",
                "I tuoi sentimenti sono importanti..."
            ],
            "practical": [
                "La prossima azione concreta che potresti fare...",
                "Un approccio pratico sarebbe...",
                "Focalizziamoci su quello che puoi controllare..."
            ],
            "social": [
                "Molte persone nella tua situazione...",
                "Non sei da solo/a in questo...",
                "Insieme possiamo..."
            ]
        }
    
    def _load_response_modifiers(self) -> Dict[str, Any]:
        """Carica modificatori per le risposte"""
        return {
            "high_support": {
                "add_validation": True,
                "increase_reassurance": True,
                "slower_pace": True
            },
            "low_support": {
                "be_concise": True,
                "focus_on_facts": True,
                "respect_autonomy": True
            }
        }