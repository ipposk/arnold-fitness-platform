"""
Tone Adjuster - Regola il tono e stile delle risposte di Arnold
"""

import re
import random
from typing import Dict, List, Any, Optional
from ..personality_profiler import PersonalityProfile, WritingStyle
from ..conversation_director import ConversationState


class ToneAdjuster:
    """Regola finemente il tono delle risposte di Arnold per adattarlo al profilo utente"""
    
    def __init__(self):
        self.tone_patterns = self._load_tone_patterns()
        self.personality_vocabulary = self._load_personality_vocabulary()
        self.emotional_markers = self._load_emotional_markers()
        self.formality_adjusters = self._load_formality_adjusters()
    
    def adjust_response_tone(self,
                           response: str,
                           personality_profile: PersonalityProfile,
                           writing_style: WritingStyle,
                           conversation_state: ConversationState,
                           context: Dict[str, Any] = None) -> str:
        """Aggiusta il tono di una risposta per allinearla al profilo utente"""
        
        adjusted_response = response
        
        # Step 1: Aggiusta per tipo di personalità
        adjusted_response = self._adjust_for_personality_type(
            adjusted_response, personality_profile
        )
        
        # Step 2: Aggiusta per stile di scrittura
        adjusted_response = self._adjust_for_writing_style(
            adjusted_response, writing_style
        )
        
        # Step 3: Aggiusta per stato conversazionale
        adjusted_response = self._adjust_for_conversation_state(
            adjusted_response, conversation_state
        )
        
        # Step 4: Aggiusta per contesto specifico
        if context:
            adjusted_response = self._adjust_for_context(
                adjusted_response, context, personality_profile
            )
        
        # Step 5: Validazione finale e polish
        adjusted_response = self._final_polish(
            adjusted_response, personality_profile, writing_style
        )
        
        return adjusted_response
    
    def adjust_question_tone(self,
                           question: str,
                           personality_profile: PersonalityProfile,
                           writing_style: WritingStyle,
                           sensitivity_level: str = "medium") -> str:
        """Aggiusta il tono di una domanda per renderla appropriata al profilo"""
        
        adjusted_question = question
        
        # Aggiusta sensibilità basata sul profilo
        if sensitivity_level == "high" or writing_style.concern_level == "high":
            adjusted_question = self._make_question_gentler(adjusted_question)
        
        # Aggiusta per comunicazione preferita
        if personality_profile.communication_preference == "direct":
            adjusted_question = self._make_question_direct(adjusted_question)
        elif personality_profile.communication_preference == "gentle":
            adjusted_question = self._make_question_supportive(adjusted_question)
        elif personality_profile.communication_preference == "detailed":
            adjusted_question = self._make_question_contextual(adjusted_question)
        
        # Aggiusta per energia
        if writing_style.energy_level == "high":
            adjusted_question = self._add_energy_to_question(adjusted_question)
        elif writing_style.energy_level == "low":
            adjusted_question = self._make_question_calm(adjusted_question)
        
        return adjusted_question
    
    def _adjust_for_personality_type(self,
                                   response: str,
                                   personality_profile: PersonalityProfile) -> str:
        """Aggiusta la risposta per il tipo di personalità primario"""
        
        personality_type = personality_profile.primary_type
        
        if personality_type == "analytical":
            response = self._make_more_analytical(response)
        elif personality_type == "emotional":
            response = self._make_more_emotional(response)
        elif personality_type == "practical":
            response = self._make_more_practical(response)
        elif personality_type == "social":
            response = self._make_more_social(response)
        
        return response
    
    def _adjust_for_writing_style(self,
                                response: str,
                                writing_style: WritingStyle) -> str:
        """Aggiusta la risposta per lo stile di scrittura dell'utente"""
        
        # Aggiusta verbosità
        if writing_style.verbosity == "brief":
            response = self._make_more_concise(response)
        elif writing_style.verbosity == "verbose":
            response = self._add_more_detail(response)
        
        # Aggiusta formalità
        if writing_style.formality == "informal":
            response = self._make_more_casual(response)
        elif writing_style.formality == "formal":
            response = self._make_more_formal(response)
        
        # Aggiusta per livello tecnico
        if writing_style.technical_level == "basic":
            response = self._simplify_technical_language(response)
        elif writing_style.technical_level == "advanced":
            response = self._enhance_technical_language(response)
        
        return response
    
    def _adjust_for_conversation_state(self,
                                     response: str,
                                     conversation_state: ConversationState) -> str:
        """Aggiusta la risposta per lo stato conversazionale"""
        
        # Aggiusta per fase
        if conversation_state.phase.value == "warmup":
            response = self._make_more_welcoming(response)
        elif conversation_state.phase.value == "assessment":
            response = self._balance_professional_empathy(response)
        elif conversation_state.phase.value == "planning":
            response = self._make_more_collaborative(response)
        
        # Aggiusta per engagement
        if conversation_state.user_engagement == "low":
            response = self._add_encouragement(response)
        elif conversation_state.user_engagement == "high":
            response = self._match_enthusiasm(response)
        
        # Aggiusta per forza relazione
        if conversation_state.relationship_strength == "building":
            response = self._add_trust_building_elements(response)
        elif conversation_state.relationship_strength == "strong":
            response = self._allow_more_directness(response)
        
        return response
    
    def _adjust_for_context(self,
                          response: str,
                          context: Dict[str, Any],
                          personality_profile: PersonalityProfile) -> str:
        """Aggiusta per contesto specifico della conversazione"""
        
        # Se l'utente ha mostrato stress o ansia
        if context.get("user_stress_level", "medium") == "high":
            response = self._add_calming_elements(response)
        
        # Se stiamo discutendo un topic sensibile
        if context.get("sensitive_topic", False):
            response = self._increase_sensitivity(response)
        
        # Se l'utente ha mostrato resistenza
        if context.get("user_resistance", False):
            response = self._reduce_pressure(response)
        
        return response
    
    def _make_more_analytical(self, response: str) -> str:
        """Rende la risposta più analitica"""
        
        # Aggiungi parole che indicano precisione
        precision_words = {
            "può": "può specificamente",
            "aiuta": "contribuisce in modo misurabile a",
            "migliora": "ottimizza quantitativamente",
            "buono": "efficace",
            "importante": "fondamentale per"
        }
        
        for old, new in precision_words.items():
            response = response.replace(old, new)
        
        # Aggiungi occasionalmente riferimenti a evidenze
        if "perché" in response and random.random() > 0.7:
            response = response.replace("perché", "perché la ricerca dimostra che")
        
        return response
    
    def _make_more_emotional(self, response: str) -> str:
        """Rende la risposta più emotiva ed empatica"""
        
        # Aggiungi validazione emotiva
        emotional_enhancers = [
            ("Capisco", "Capisco profondamente"),
            ("È normale", "È completamente comprensibile"),
            ("Va bene", "Va più che bene"),
            ("Puoi", "Hai la forza di")
        ]
        
        for old, new in emotional_enhancers:
            if old in response:
                response = response.replace(old, new, 1)  # Solo la prima occorrenza
        
        # Aggiungi occasionalmente validazione emotiva
        validation_phrases = [
            "I tuoi sentimenti sono validi. ",
            "È normale sentirsi così. ",
            "Stai facendo del tuo meglio. "
        ]
        
        if random.random() > 0.8:  # 20% chance
            response = random.choice(validation_phrases) + response
        
        return response
    
    def _make_more_practical(self, response: str) -> str:
        """Rende la risposta più pratica e orientata all'azione"""
        
        # Trasforma consigli generici in step specifici
        if "dovresti" in response:
            response = response.replace("dovresti", "il prossimo passo concreto è")
        
        # Aggiungi elementi actionable
        practical_enhancers = {
            "considera": "prova concretamente a",
            "potrebbe essere utile": "ti suggerisco di",
            "è importante": "il primo passo è",
            "ricorda": "applica questo"
        }
        
        for old, new in practical_enhancers.items():
            response = response.replace(old, new)
        
        return response
    
    def _make_more_social(self, response: str) -> str:
        """Rende la risposta più sociale e coinvolgente"""
        
        # Aggiungi elementi di condivisione
        social_enhancers = {
            "tu": "noi",
            "la tua esperienza": "la nostra esperienza condivisa",
            "il tuo percorso": "il percorso che stiamo facendo insieme"
        }
        
        for old, new in social_enhancers.items():
            if old in response and random.random() > 0.6:
                response = response.replace(old, new, 1)
        
        # Aggiungi riferimenti sociali
        social_additions = [
            "Molte persone si trovano nella tua situazione. ",
            "Non sei da solo/a in questo. ",
            "È un'esperienza molto comune. "
        ]
        
        if random.random() > 0.8:
            response = random.choice(social_additions) + response
        
        return response
    
    def _make_more_concise(self, response: str) -> str:
        """Rende la risposta più concisa"""
        
        # Rimuovi ridondanze comuni
        redundant_phrases = [
            "come sai, ", "ovviamente, ", "naturalmente, ",
            "di solito, ", "in generale, ", "tipicamente, ",
            "fondamentalmente, ", "essenzialmente, "
        ]
        
        for phrase in redundant_phrases:
            response = response.replace(phrase, "")
        
        # Accorcia frasi lunghe
        if len(response.split('.')) > 3:
            sentences = response.split('.')
            # Mantieni solo le prime 2-3 frasi più importanti
            response = '. '.join(sentences[:3]).rstrip() + '.'
        
        return response
    
    def _add_more_detail(self, response: str) -> str:
        """Aggiunge più dettagli alla risposta"""
        
        # Espandi concetti con spiegazioni
        expansions = {
            "questo aiuta": "questo aiuta perché crea un meccanismo che",
            "è importante": "è particolarmente importante perché influisce direttamente su",
            "dovresti": "dovresti considerare di, specialmente perché"
        }
        
        for old, new in expansions.items():
            if old in response:
                response = response.replace(old, new, 1)
        
        return response
    
    def _make_more_casual(self, response: str) -> str:
        """Rende la risposta più casual"""
        
        casual_replacements = {
            "Salve": "Ciao",
            "La ringrazio": "Grazie",
            "cortesemente": "",
            "le consiglio": "ti consiglio",
            "potrebbe": "potresti",
            "dovrebbe": "dovresti"
        }
        
        for formal, casual in casual_replacements.items():
            response = response.replace(formal, casual)
        
        return response
    
    def _make_more_formal(self, response: str) -> str:
        """Rende la risposta più formale"""
        
        formal_replacements = {
            "ciao": "salve",
            "ok": "d'accordo",
            "tipo": "ad esempio",
            "roba": "elementi",
            "figata": "ottimo"
        }
        
        for casual, formal in formal_replacements.items():
            response = response.replace(casual, formal)
        
        return response
    
    def _simplify_technical_language(self, response: str) -> str:
        """Semplifica il linguaggio tecnico"""
        
        simplifications = {
            "macronutrienti": "nutrienti principali (proteine, carboidrati, grassi)",
            "deficit calorico": "mangiare meno calorie di quelle che bruci",
            "metabolismo basale": "energia che il corpo usa a riposo",
            "indice glicemico": "velocità con cui un cibo alza la glicemia",
            "composizione corporea": "rapporto tra muscoli e grasso"
        }
        
        for technical, simple in simplifications.items():
            response = response.replace(technical, simple)
        
        return response
    
    def _enhance_technical_language(self, response: str) -> str:
        """Arricchisce il linguaggio tecnico"""
        
        technical_enhancements = {
            "proteine": "proteine (macronutrienti essenziali)",
            "calorie": "calorie (unità di energia)",
            "esercizio": "esercizio fisico (stimolo adattivo)",
            "peso": "peso corporeo (massa totale)",
            "dieta": "regime alimentare"
        }
        
        for simple, technical in technical_enhancements.items():
            if simple in response and random.random() > 0.7:
                response = response.replace(simple, technical, 1)
        
        return response
    
    def _make_more_welcoming(self, response: str) -> str:
        """Rende la risposta più accogliente"""
        
        if not response.startswith(("Ciao", "Benvenuto", "Salve")):
            welcoming_starts = [
                "Ciao! ", "Benvenuto/a! ", "È un piacere conoscerti! "
            ]
            response = random.choice(welcoming_starts) + response
        
        return response
    
    def _balance_professional_empathy(self, response: str) -> str:
        """Bilancia professionalità ed empatia"""
        
        # Aggiungi elementi professionali con calore
        if "ti consiglio" in response:
            response = response.replace("ti consiglio", "dal punto di vista professionale, ti consiglio con calore")
        
        return response
    
    def _make_more_collaborative(self, response: str) -> str:
        """Rende la risposta più collaborativa"""
        
        collaborative_replacements = {
            "dovresti": "potremmo insieme",
            "ti consiglio": "lavoriamo insieme su",
            "la soluzione è": "insieme possiamo trovare",
            "devi": "possiamo"
        }
        
        for directive, collaborative in collaborative_replacements.items():
            response = response.replace(directive, collaborative)
        
        return response
    
    def _add_encouragement(self, response: str) -> str:
        """Aggiunge incoraggiamento alla risposta"""
        
        encouraging_additions = [
            "Stai facendo un ottimo lavoro condividendo questo con me. ",
            "Apprezzo la tua apertura. ",
            "È già un grande passo quello che stai facendo. ",
            "La tua consapevolezza è il primo passo verso il cambiamento. "
        ]
        
        if random.random() > 0.7:
            response = random.choice(encouraging_additions) + response
        
        return response
    
    def _match_enthusiasm(self, response: str) -> str:
        """Fa corrispondere l'entusiasmo dell'utente"""
        
        if not response.endswith("!"):
            enthusiasm_markers = ["fantastico", "ottimo", "perfetto", "eccellente"]
            if any(marker in response.lower() for marker in enthusiasm_markers):
                response = response.rstrip(".") + "!"
        
        return response
    
    def _add_trust_building_elements(self, response: str) -> str:
        """Aggiunge elementi per costruire fiducia"""
        
        trust_elements = [
            "Sono qui per supportarti. ",
            "Puoi fidarti che troveremo insieme la strada giusta. ",
            "Non c'è giudizio qui, solo supporto. "
        ]
        
        if random.random() > 0.8:
            response = random.choice(trust_elements) + response
        
        return response
    
    def _allow_more_directness(self, response: str) -> str:
        """Permette maggiore dirrettezza quando la relazione è forte"""
        
        # Rimuovi eccessiva cortesia quando la relazione è consolidata
        excessive_politeness = [
            "se ti va, ", "quando ti senti comodo/a, ",
            "solo se ti va di condividere, ", "non c'è fretta, ma "
        ]
        
        for politeness in excessive_politeness:
            response = response.replace(politeness, "")
        
        return response
    
    def _add_calming_elements(self, response: str) -> str:
        """Aggiunge elementi calmanti per ridurre stress"""
        
        calming_additions = [
            "Respira profondamente. ",
            "Tutto a suo tempo. ",
            "Non c'è fretta. ",
            "Andiamo con calma. "
        ]
        
        response = random.choice(calming_additions) + response
        
        return response
    
    def _increase_sensitivity(self, response: str) -> str:
        """Aumenta la sensibilità per topic delicati"""
        
        # Aggiungi disclaimer sensibili
        sensitive_additions = [
            "So che può essere difficile parlarne. ",
            "Prendi tutto il tempo che ti serve. ",
            "Condividi solo quello di cui ti senti a tuo agio. "
        ]
        
        response = random.choice(sensitive_additions) + response
        
        return response
    
    def _reduce_pressure(self, response: str) -> str:
        """Riduce la pressione quando l'utente mostra resistenza"""
        
        # Rimuovi linguaggio pressante
        pressure_words = ["devi", "dovresti assolutamente", "è fondamentale che"]
        
        for pressure in pressure_words:
            response = response.replace(pressure, "potresti considerare di")
        
        # Aggiungi opzionalità
        response = response + " Ma ricorda, sei tu a decidere il ritmo che ti è più comodo."
        
        return response
    
    def _final_polish(self,
                     response: str,
                     personality_profile: PersonalityProfile,
                     writing_style: WritingStyle) -> str:
        """Ultimo polish generale della risposta"""
        
        # Rimuovi spazi extra e doppi punti
        response = re.sub(r'\s+', ' ', response)
        response = re.sub(r'\.+', '.', response)
        response = response.strip()
        
        # Assicurati che finisca con punteggiatura appropriata
        if not response.endswith(('.', '!', '?')):
            response += '.'
        
        # Capitalizzazione iniziale
        if response:
            response = response[0].upper() + response[1:]
        
        return response
    
    # Metodi specifici per le domande
    
    def _make_question_gentler(self, question: str) -> str:
        """Rende una domanda più gentile"""
        
        gentle_prefixes = [
            "Solo se ti va di condividerlo, ",
            "Quando ti senti pronto/a, ",
            "Se ti senti a tuo agio, "
        ]
        
        if not any(prefix in question for prefix in gentle_prefixes):
            question = random.choice(gentle_prefixes) + question.lower()
            question = question[0].upper() + question[1:]
        
        return question
    
    def _make_question_direct(self, question: str) -> str:
        """Rende una domanda più diretta"""
        
        # Rimuovi preamboli
        direct_starters = ["Dimmi", "Quale", "Come", "Quando", "Dove"]
        
        for starter in direct_starters:
            if question.startswith("Potresti dirmi"):
                question = question.replace("Potresti dirmi", "Dimmi")
            elif question.startswith("Mi piacerebbe sapere"):
                question = question.replace("Mi piacerebbe sapere", "Dimmi")
        
        return question
    
    def _make_question_supportive(self, question: str) -> str:
        """Rende una domanda più supportiva"""
        
        supportive_endings = [
            " Non c'è fretta per rispondere.",
            " Condividi quello che ti senti di dire.",
            " Sono qui per ascoltarti senza giudizio."
        ]
        
        if random.random() > 0.7:
            question += random.choice(supportive_endings)
        
        return question
    
    def _make_question_contextual(self, question: str) -> str:
        """Aggiunge contesto a una domanda"""
        
        contextual_additions = [
            " Questo mi aiuterà a capirti meglio.",
            " Queste informazioni sono importanti per personalizzare i miei consigli.",
            " Conoscere questo aspetto mi permetterà di supportarti al meglio."
        ]
        
        question += random.choice(contextual_additions)
        
        return question
    
    def _add_energy_to_question(self, question: str) -> str:
        """Aggiunge energia a una domanda"""
        
        if not question.endswith("!"):
            energetic_words = ["fantastico", "interessante", "ottimo", "perfetto"]
            if any(word in question.lower() for word in energetic_words):
                question = question.rstrip(".?") + "!"
        
        return question
    
    def _make_question_calm(self, question: str) -> str:
        """Rende una domanda più calma"""
        
        # Rimuovi punti esclamativi
        question = question.replace("!", ".")
        
        # Aggiungi elementi calmanti
        if random.random() > 0.8:
            question = "Con calma, " + question.lower()
            question = question[0].upper() + question[1:]
        
        return question
    
    def _load_tone_patterns(self) -> Dict[str, Any]:
        """Carica pattern per aggiustamenti del tono"""
        return {
            "analytical": {
                "markers": ["evidenza", "dati", "ricerca", "studi", "specificamente"],
                "avoid": ["senti", "provi", "emotivamente"]
            },
            "emotional": {
                "markers": ["comprendo", "senti", "emozioni", "cuore", "validazione"],
                "avoid": ["oggettivamente", "analiticamente", "tecnicamente"]
            }
        }
    
    def _load_personality_vocabulary(self) -> Dict[str, Dict[str, List[str]]]:
        """Carica vocabolario specifico per personalità"""
        return {
            "analytical": {
                "preferred": ["preciso", "misurabile", "evidenza", "dati", "sistematico"],
                "avoid": ["sento che", "mi sembra", "probabilmente"]
            },
            "emotional": {
                "preferred": ["comprendo", "sento", "validazione", "supporto", "empatia"],
                "avoid": ["oggettivamente", "precisamente", "sistematicamente"]
            }
        }
    
    def _load_emotional_markers(self) -> Dict[str, List[str]]:
        """Carica marcatori emotionali"""
        return {
            "supportive": ["ti capisco", "è normale", "vai bene", "sei forte"],
            "encouraging": ["ottimo lavoro", "stai migliorando", "continua così", "bravo"],
            "calming": ["con calma", "respira", "tutto a posto", "passo dopo passo"]
        }
    
    def _load_formality_adjusters(self) -> Dict[str, Dict[str, str]]:
        """Carica aggiustatori di formalità"""
        return {
            "make_casual": {
                "La ringrazio": "Grazie",
                "potrebbe": "potresti", 
                "dovrebbe": "dovresti",
                "cortesemente": ""
            },
            "make_formal": {
                "ciao": "salve",
                "ok": "d'accordo",
                "roba": "elementi",
                "figata": "eccellente"
            }
        }