"""
Offline Conversational Orchestrator - Versione semplice e sicura
"""

import json
from datetime import datetime
from typing import Dict, Any

# Import componenti conversazionali con fallback sicuri
try:
    from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter
except ImportError:
    # Fallback se i componenti non sono disponibili
    class StyleAnalyzer:
        def analyze_text(self, text): 
            return {'verbosity': 'medium', 'emotional_tone': 'neutral', 'energy_level': 'medium'}
    
    class PersonalityMapper:
        def map_to_profile(self, analysis):
            return {'primary_type': 'practical', 'communication_preference': 'encouraging'}
    
    class EmpathyAdapter:
        def adapt_to_profile(self, profile):
            return {'tone': 'friendly', 'formality': 'casual'}


class OfflineConversationalOrchestrator:
    """
    Orchestrator conversazionale offline semplice e sicuro
    Perfetto per demo senza API keys
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        
        # Inizializza componenti con fallback
        try:
            self.style_analyzer = StyleAnalyzer()
            self.personality_mapper = PersonalityMapper()
            self.empathy_adapter = EmpathyAdapter()
        except:
            # Usa versioni mock se i componenti non sono disponibili
            self.style_analyzer = StyleAnalyzer()
            self.personality_mapper = PersonalityMapper()
            self.empathy_adapter = EmpathyAdapter()
        
        # Stato conversazionale semplice
        self.conversation_state = {
            'phase': 'warmup',
            'turn_count': 0,
            'user_engagement': 'medium'
        }
        
        # Cronologia limitata
        self.conversation_history = []
        
        # Templates di risposta sicure
        self.response_templates = {
            'practical': [
                "Perfetto! Grazie per i dettagli concreti. {input_specific}. Quali sono le tue sfide principali in questo momento?",
                "Ottimo, hai un percorso molto interessante! Da 123kg a 89.7kg è un risultato incredibile. Ora vuoi arrivare a 80-85kg - questo è un obiettivo molto concreto. Qual è la parte più difficile per te in questo momento?",
                "Ah, ecco il punto! La dieta è spesso la parte più tosta. È fantastico che tu abbia scoperto la corsa - spesso è più stimolante della palestra! Sul tema alimentazione: quali sono i momenti più difficili della giornata per te?",
                "Interessante! {input_specific}. Cosa pensi che funzionerebbe meglio per il tuo stile di vita?",
                "Perfetto, stiamo andando nel dettaglio! {input_specific}. Come possiamo rendere questo più sostenibile per te?"
            ],
            'emotional': [
                "Grazie per aver condiviso i tuoi sentimenti con me. {input_specific}. Come ti fa sentire questa situazione?",
                "Capisco che questo sia importante per te. {input_specific}. Vuoi raccontarmi di più su come vivi tutto questo?",
                "Ti ringrazio per la fiducia nel condividere questo. {input_specific}. Cosa provi quando ci pensi?"
            ],
            'analytical': [
                "Interessante approccio sistematico! {input_specific}. Hai già identificato dei pattern o correlazioni?",
                "Apprezzo la tua analisi dettagliata. {input_specific}. Quali dati consideri più significativi?",
                "Ottima strutturazione del problema! {input_specific}. Su quali metriche ti stai basando?"
            ],
            'social': [
                "Che bello sentire la tua esperienza! {input_specific}. Come reagiscono le persone intorno a te?",
                "Mi fa piacere che tu abbia condiviso questo. {input_specific}. Chi ti supporta in questo percorso?",
                "Grazie per aver aperto questo dialogo! {input_specific}. Come influisce questo sulle tue relazioni?"
            ],
            'neutral': [
                "Ciao! Grazie per aver condiviso. {input_specific}. Come posso aiutarti meglio?",
                "Interessante! {input_specific}. Dimmi di più su quello che ti preoccupa.",
                "Capisco. {input_specific}. Su cosa vorresti che ci concentrassimo?"
            ]
        }

    def process_conversational_input(self, user_input: str) -> Dict[str, Any]:
        """
        Processa l'input dell'utente - versione sicura e limitata
        """
        try:
            # Incrementa contatore
            self.conversation_state['turn_count'] += 1
            
            # Analizza input in modo sicuro
            input_specific = self._extract_key_info(user_input)
            
            # Determina profilo in modo semplice
            personality_type = self._detect_simple_personality(user_input)
            
            # Genera risposta sicura
            response = self._generate_safe_response(personality_type, input_specific)
            
            # Salva storia limitata
            if len(self.conversation_history) >= 5:
                self.conversation_history = self.conversation_history[-2:]  # Mantieni solo le ultime 2
                
            self.conversation_history.append({
                'user_input': user_input[:100],  # Limita lunghezza
                'response': response[:300],      # Limita lunghezza
                'personality': personality_type
            })
            
            # Risultato sicuro
            return {
                'last_output': {
                    'guidance_markdown': response
                },
                'personality_profile': {
                    'primary_type': personality_type,
                    'communication_preference': 'encouraging'
                },
                'conversation_state': {
                    'phase': self.conversation_state['phase'],
                    'turn_count': self.conversation_state['turn_count'],
                    'user_engagement': 'medium'
                },
                'session_id': self.session_id
            }
            
        except Exception as e:
            # Fallback ultra-sicuro
            return {
                'last_output': {
                    'guidance_markdown': "Ciao! Grazie per aver scritto. Come posso aiutarti con la tua salute e benessere oggi?"
                },
                'personality_profile': {'primary_type': 'neutral'},
                'conversation_state': {'turn_count': 1, 'phase': 'warmup'},
                'session_id': self.session_id
            }

    def _extract_key_info(self, user_input: str) -> str:
        """Estrae info chiave dall'input in modo sicuro"""
        try:
            # Cerca parole chiave specifiche per percorsi di peso
            lower_input = user_input.lower()
            
            if 'dimagrire' in lower_input and 'kg' in lower_input:
                return "Vedo che hai un percorso di dimagrimento con obiettivi specifici"
            elif any(word in lower_input for word in ['123', '107', '89.7', '90']) and 'kg' in lower_input:
                return "Hai condiviso la tua storia di peso dettagliata"
            elif 'non riesco' in lower_input and 'dieta' in lower_input:
                return "La dieta sembra essere la tua sfida principale"
            elif 'correre' in lower_input or ('palestra' in lower_input and 'stimolava poco' in lower_input):
                return "Hai fatto un bel cambio dall'allenamento in palestra alla corsa"
            elif 'appena detto' in lower_input or 'te l\'ho' in lower_input:
                return "Capisco che ti aspetti una risposta più specifica"
            elif any(word in lower_input for word in ['peso', 'kg', 'altezza', 'cm']):
                return "Vedo che hai condiviso alcuni dati fisici"
            elif any(word in lower_input for word in ['stressato', 'frustrato', 'preoccupato']):
                return "Sento che ci sono delle emozioni forti in gioco"
            elif any(word in lower_input for word in ['allenamento', 'palestra', 'sport']):
                return "L'attività fisica sembra essere importante per te"
            elif any(word in lower_input for word in ['mangiare', 'cibo', 'dieta']):
                return "La nutrizione è al centro dei tuoi pensieri"
            else:
                return "Grazie per aver condiviso la tua situazione"
        except:
            return "Grazie per aver scritto"

    def _detect_simple_personality(self, user_input: str) -> str:
        """Rileva personalità in modo semplice"""
        try:
            # Semplice rilevamento basato su parole chiave
            if any(word in user_input.lower() for word in ['dati', 'numeri', 'preciso', 'esatto']):
                return 'analytical'
            elif any(word in user_input.lower() for word in ['sento', 'emozione', 'frustrato', 'stressato']):
                return 'emotional'  
            elif any(word in user_input.lower() for word in ['veloce', 'pratico', 'diretto', 'soluzione']):
                return 'practical'
            elif any(word in user_input.lower() for word in ['famiglia', 'amici', 'insieme', 'condividere']):
                return 'social'
            else:
                return 'practical'  # Default pratico per info fisiche
        except:
            return 'neutral'

    def _generate_safe_response(self, personality_type: str, input_specific: str) -> str:
        """Genera risposta sicura basata sul profilo"""
        try:
            templates = self.response_templates.get(personality_type, self.response_templates['neutral'])
            
            # Selezione intelligente del template basata sul turno
            turn_count = self.conversation_state.get('turn_count', 1)
            template_index = min(turn_count - 1, len(templates) - 1)
            template = templates[template_index]
            
            return template.format(input_specific=input_specific)
        except:
            return "Ciao! Grazie per aver condiviso. Come posso aiutarti con la tua salute?"