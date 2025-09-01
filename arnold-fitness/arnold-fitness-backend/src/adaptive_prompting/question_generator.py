"""
Question Generator - Genera domande naturali e personalizzate
"""

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..personality_profiler import PersonalityProfile, WritingStyle
from ..conversation_director import ConversationState, ConversationPhase


@dataclass
class QuestionTemplate:
    """Template per una domanda personalizzata"""
    base_question: str
    analytical_variant: str
    emotional_variant: str
    practical_variant: str
    social_variant: str
    context_requirements: List[str] = None
    sensitivity_level: str = "medium"  # "low", "medium", "high"
    

class QuestionGenerator:
    """Genera domande conversazionali personalizzate basate su profilo e contesto"""
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        self.warmup_questions = self._load_warmup_questions()
        self.followup_generators = self._load_followup_generators()
        self.transition_phrases = self._load_transition_phrases()
    
    def generate_question(self,
                         question_context: Dict[str, Any],
                         personality_profile: PersonalityProfile,
                         writing_style: WritingStyle,
                         conversation_state: ConversationState) -> str:
        """Genera una domanda personalizzata basata sul contesto"""
        
        # Seleziona il template appropriato
        template = self._select_template(
            question_context, personality_profile, conversation_state
        )
        
        if not template:
            return self._generate_fallback_question(personality_profile)
        
        # Personalizza la domanda per il profilo
        personalized_question = self._personalize_question(
            template, personality_profile, writing_style
        )
        
        # Aggiungi transizioni naturali se necessario
        final_question = self._add_transition_if_needed(
            personalized_question, conversation_state, question_context
        )
        
        # Aggiungi tocchi finali basati sul writing style
        return self._finalize_question(final_question, writing_style, personality_profile)
    
    def generate_warmup_question(self,
                               personality_profile: PersonalityProfile,
                               writing_style: WritingStyle,
                               turn_number: int = 1) -> str:
        """Genera una domanda di warmup per iniziare la conversazione"""
        
        if turn_number == 1:
            return self._generate_opening_question(personality_profile)
        else:
            return self._generate_followup_warmup(personality_profile, turn_number)
    
    def generate_followup_question(self,
                                 last_response: str,
                                 topic: str,
                                 personality_profile: PersonalityProfile,
                                 writing_style: WritingStyle) -> str:
        """Genera una domanda di follow-up basata sulla risposta precedente"""
        
        # Analizza la risposta per determinare il tipo di follow-up
        followup_type = self._determine_followup_type(last_response, writing_style)
        
        # Genera follow-up appropriato
        return self._generate_specific_followup(
            followup_type, last_response, topic, personality_profile
        )
    
    def _select_template(self,
                        question_context: Dict[str, Any],
                        personality_profile: PersonalityProfile,
                        conversation_state: ConversationState) -> Optional[QuestionTemplate]:
        """Seleziona il template più appropriato per il contesto"""
        
        template_key = question_context.get("template_key", "")
        question_type = question_context.get("question_type", "")
        
        # Prima cerca per template_key specifico
        if template_key and template_key in self.question_templates:
            return self.question_templates[template_key]
        
        # Poi cerca per question_type
        type_mapping = {
            "demographic_info": "demographics",
            "goal_exploration": "goals",
            "habit_assessment": "eating_habits",
            "activity_assessment": "activity",
            "warmup": f"{personality_profile.primary_type}_warmup",
            "followup": "generic_followup"
        }
        
        mapped_key = type_mapping.get(question_type)
        if mapped_key and mapped_key in self.question_templates:
            return self.question_templates[mapped_key]
        
        # Fallback su template generici
        return self.question_templates.get("generic_assessment")
    
    def _personalize_question(self,
                            template: QuestionTemplate,
                            personality_profile: PersonalityProfile,
                            writing_style: WritingStyle) -> str:
        """Personalizza una domanda per il profilo specifico"""
        
        # Seleziona la variante appropriata per il tipo di personalità
        variant_map = {
            "analytical": template.analytical_variant,
            "emotional": template.emotional_variant,
            "practical": template.practical_variant,
            "social": template.social_variant
        }
        
        question = variant_map.get(
            personality_profile.primary_type, 
            template.base_question
        )
        
        # Aggiusta per writing style
        if writing_style.verbosity == "brief":
            question = self._make_more_concise(question)
        elif writing_style.verbosity == "verbose":
            question = self._add_context_detail(question)
        
        return question
    
    def _add_transition_if_needed(self,
                                question: str,
                                conversation_state: ConversationState,
                                question_context: Dict[str, Any]) -> str:
        """Aggiunge transizioni naturali alla domanda se necessario"""
        
        # Se cambiamo topic, aggiungi transizione
        current_topic = question_context.get("topic", "")
        last_topic = conversation_state.last_topic
        
        if (current_topic and last_topic and 
            current_topic != last_topic and 
            conversation_state.turn_count > 2):
            
            transition = self._get_topic_transition(last_topic, current_topic)
            return f"{transition} {question}"
        
        # Se è l'inizio di una nuova fase
        if conversation_state.turn_count > 1:
            phase_transitions = {
                ConversationPhase.ASSESSMENT: [
                    "Ora vorrei conoscerti meglio.",
                    "Passiamo a parlare di te.",
                    "Adesso vorrei capire la tua situazione."
                ],
                ConversationPhase.PLANNING: [
                    "Bene, ora che ci conosciamo meglio...",
                    "Basandoci su quello che mi hai detto...",
                    "Ora possiamo iniziare a pensare insieme..."
                ]
            }
            
            transitions = phase_transitions.get(conversation_state.phase, [])
            if transitions:
                transition = random.choice(transitions)
                return f"{transition} {question}"
        
        return question
    
    def _finalize_question(self,
                          question: str,
                          writing_style: WritingStyle,
                          personality_profile: PersonalityProfile) -> str:
        """Applica tocchi finali alla domanda"""
        
        # Aggiusta energia
        if writing_style.energy_level == "high" and not question.endswith("!"):
            # Aggiungi occasionalmente un punto esclamativo
            if random.random() > 0.7:
                question = question.rstrip(".") + "!"
        
        # Aggiungi supporto se necessario
        if (writing_style.concern_level == "high" or 
            personality_profile.support_needs == "high"):
            supportive_endings = [
                " Prenditi il tempo che ti serve per rispondere.",
                " Non c'è fretta, condividi quello che ti senti di dire.",
                " Ricorda che non ci sono risposte giuste o sbagliate."
            ]
            
            if random.random() > 0.8:  # 20% chance
                question += random.choice(supportive_endings)
        
        return question
    
    def _generate_opening_question(self, personality_profile: PersonalityProfile) -> str:
        """Genera la prima domanda della conversazione"""
        
        opening_questions = {
            "analytical": [
                "Ciao! Sono Arnold, il tuo consulente nutrizionale AI. Per offrirti consigli mirati e basati su evidenze, mi piacerebbe iniziare conoscendo i tuoi obiettivi specifici per la salute.",
                "Benvenuto! Sono Arnold. Utilizzo un approccio sistematico per il benessere nutrizionale. Potresti iniziarmi raccontandomi qual è la tua situazione attuale e cosa vorresti migliorare?"
            ],
            "emotional": [
                "Ciao! Sono Arnold, e sono qui per ascoltarti e supportarti nel tuo percorso di benessere. Mi piacerebbe iniziare sentendo come ti senti riguardo alla tua salute e alimentazione in questo momento.",
                "Benvenuto! Sono Arnold. Prima di tutto, voglio che tu sappia che questo è uno spazio sicuro dove puoi condividere liberamente. Come ti senti riguardo al tuo rapporto con il cibo ultimamente?"
            ],
            "practical": [
                "Ciao! Sono Arnold, il tuo consulente nutrizionale. Andiamo dritti al punto: quali sono le sfide principali che stai affrontando con la tua alimentazione o forma fisica?",
                "Benvenuto! Sono Arnold. Mi piace lavorare su soluzioni concrete. Dimmi: cosa vorresti cambiare nella tua routine alimentare o di fitness?"
            ],
            "social": [
                "Ciao! Sono Arnold, e sono entusiasta di iniziare questo percorso insieme a te! Mi piacerebbe conoscere un po' la tua storia - come va la tua vita dal punto di vista della salute e benessere?",
                "Benvenuto nella nostra conversazione! Sono Arnold. Adoro conoscere le persone e le loro storie uniche. Raccontami un po' di te e di come vivi la tua relazione con il cibo e la salute."
            ]
        }
        
        questions = opening_questions.get(
            personality_profile.primary_type,
            opening_questions["practical"]  # Fallback
        )
        
        return random.choice(questions)
    
    def _generate_followup_warmup(self, personality_profile: PersonalityProfile, turn_number: int) -> str:
        """Genera domande di warmup per i turni successivi al primo"""
        
        followup_warmups = {
            "analytical": [
                "Interessante! Potresti essere più specifico su questo aspetto?",
                "Questo mi dà un buon quadro di partenza. Quali dati ritieni più importanti per valutare i tuoi progressi?"
            ],
            "emotional": [
                "Capisco quello che provi. È normale sentirsi così. Puoi dirmi di più su come queste sensazioni influenzano la tua giornata?",
                "Ti ringrazio per aver condiviso questo con me. Come ti senti quando pensi ai tuoi obiettivi di benessere?"
            ],
            "practical": [
                "Perfetto, questo mi aiuta a capire la situazione. Quali sono gli ostacoli più concreti che incontri quotidianamente?",
                "Bene, stiamo delineando il quadro. Qual è la cosa più urgente su cui vorresti lavorare?"
            ],
            "social": [
                "Mi piace il tuo approccio! Come reagiscono le persone intorno a te ai tuoi obiettivi di salute?",
                "Fantastico! E la tua famiglia o i tuoi amici come vivono questi cambiamenti che vuoi fare?"
            ]
        }
        
        questions = followup_warmups.get(
            personality_profile.primary_type,
            followup_warmups["practical"]
        )
        
        return random.choice(questions)
    
    def _determine_followup_type(self, last_response: str, writing_style: WritingStyle) -> str:
        """Determina che tipo di follow-up è necessario"""
        
        response_lower = last_response.lower()
        
        # Risposta vaga -> chiedi chiarimenti
        vague_indicators = ["non so", "mah", "boh", "forse", "magari", "dipende"]
        if any(indicator in response_lower for indicator in vague_indicators):
            return "clarification"
        
        # Risposta emotiva -> offri supporto
        emotional_indicators = ["difficile", "stress", "problemi", "paura", "ansia"]
        if any(indicator in response_lower for indicator in emotional_indicators):
            return "emotional_support"
        
        # Risposta dettagliata -> approfondisci
        if len(last_response.split()) > 15:
            return "deep_dive"
        
        # Risposta breve ma specifica -> esplora
        return "exploration"
    
    def _generate_specific_followup(self,
                                  followup_type: str,
                                  last_response: str,
                                  topic: str,
                                  personality_profile: PersonalityProfile) -> str:
        """Genera un follow-up specifico basato sul tipo identificato"""
        
        followup_generators = {
            "clarification": self._generate_clarification_followup,
            "emotional_support": self._generate_supportive_followup,
            "deep_dive": self._generate_deepdive_followup,
            "exploration": self._generate_exploration_followup
        }
        
        generator = followup_generators.get(followup_type, self._generate_exploration_followup)
        return generator(last_response, topic, personality_profile)
    
    def _generate_clarification_followup(self,
                                       last_response: str,
                                       topic: str,
                                       personality_profile: PersonalityProfile) -> str:
        """Genera follow-up per chiarire risposte vaghe"""
        
        clarification_questions = {
            "analytical": [
                "Capisco che ci sono molte variabili. Potresti darmi un esempio specifico?",
                "Per aiutarti meglio, mi servirebbe qualche dettaglio in più su questo punto."
            ],
            "emotional": [
                "Non c'è fretta, ma quando ti senti pronto/a potresti condividere qualche dettaglio in più?",
                "È normale non avere tutto chiaro subito. Cosa ti viene in mente se pensi a questo argomento?"
            ],
            "practical": [
                "Okay, prendiamola da un altro angolo. Qual è la prima cosa che noti quando...",
                "Facciamo un esempio concreto: ieri, come è andata con..."
            ],
            "social": [
                "Immagino che sia complesso! Molte persone si trovano nella tua situazione. Cosa noti di più quando..."
            ]
        }
        
        questions = clarification_questions.get(
            personality_profile.primary_type,
            clarification_questions["practical"]
        )
        
        return random.choice(questions)
    
    def _generate_supportive_followup(self,
                                    last_response: str,
                                    topic: str,
                                    personality_profile: PersonalityProfile) -> str:
        """Genera follow-up di supporto emotivo"""
        
        supportive_questions = [
            "Quello che provi è comprensibile e più comune di quanto pensi. Come posso supportarti al meglio in questo?",
            "Ti ringrazio per aver condiviso questo con me. È importante che io capisca anche l'aspetto emotivo. Cosa ti aiuterebbe di più?",
            "Sento che c'è molto dietro a quello che mi hai detto. Vuoi parlarmi di come influisce sulla tua quotidianità?",
            "Non sei solo/a in questo. Come pensi che potremmo affrontare insieme questa difficoltà?"
        ]
        
        return random.choice(supportive_questions)
    
    def _generate_deepdive_followup(self,
                                  last_response: str,
                                  topic: str,
                                  personality_profile: PersonalityProfile) -> str:
        """Genera follow-up per approfondire risposte dettagliate"""
        
        # Estrai keyword interessanti dalla risposta
        keywords = self._extract_keywords(last_response)
        
        if keywords:
            keyword = random.choice(keywords)
            deepdive_questions = [
                f"Hai menzionato '{keyword}' - è un aspetto importante per te?",
                f"Mi colpisce quello che dici su '{keyword}'. Puoi dirmi di più?",
                f"'{keyword}' sembra centrale nella tua esperienza. Come influisce sul resto?"
            ]
            return random.choice(deepdive_questions)
        
        # Fallback generico
        return "Quello che mi racconti è molto interessante. C'è un aspetto in particolare su cui ti piacerebbe che ci soffermassimo?"
    
    def _generate_exploration_followup(self,
                                     last_response: str,
                                     topic: str,
                                     personality_profile: PersonalityProfile) -> str:
        """Genera follow-up per esplorare ulteriormente"""
        
        exploration_questions = {
            "analytical": [
                "Interessante. Quanto spesso si verifica questa situazione?",
                "Questo mi dà informazioni utili. Hai notato dei pattern o delle correlazioni?"
            ],
            "emotional": [
                "Capisco. Come ti fa sentire questa situazione?",
                "Mi sembra importante per te. Cosa rappresenta emotivamente?"
            ],
            "practical": [
                "Bene. Cosa fai di solito in questi casi?",
                "Ok. Qual è l'approccio che hai trovato più efficace finora?"
            ],
            "social": [
                "Interessante! E le persone intorno a te come reagiscono?",
                "E nel tuo ambiente sociale, come viene vissuta questa cosa?"
            ]
        }
        
        questions = exploration_questions.get(
            personality_profile.primary_type,
            exploration_questions["practical"]
        )
        
        return random.choice(questions)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Estrae parole chiave interessanti dal testo"""
        
        # Parole di stop da ignorare
        stop_words = {
            "io", "tu", "lui", "lei", "noi", "voi", "loro",
            "il", "la", "i", "le", "un", "una", "uno",
            "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
            "che", "chi", "come", "quando", "dove", "perché", "quanto",
            "e", "o", "ma", "se", "anche", "ancora", "già", "più", "molto",
            "essere", "avere", "fare", "dire", "andare", "stare", "dare"
        }
        
        words = text.lower().split()
        
        # Filtra parole interessanti (lunghe e non stop words)
        keywords = [
            word.strip(".,!?;:") 
            for word in words 
            if len(word) > 4 and word.lower() not in stop_words
        ]
        
        return keywords[:3]  # Massimo 3 keyword
    
    def _make_more_concise(self, question: str) -> str:
        """Rende una domanda più concisa"""
        
        # Rimuovi frasi di cortesia
        concise_replacements = {
            "Mi piacerebbe sapere ": "",
            "Potresti dirmi ": "",
            "Vorrei chiederti ": "",
            "Ti andrebbe di ": "",
            ", se ti va": "",
            ", quando hai tempo": ""
        }
        
        for verbose, concise in concise_replacements.items():
            question = question.replace(verbose, concise)
        
        return question.strip()
    
    def _add_context_detail(self, question: str) -> str:
        """Aggiunge dettagli contestuali per persone più verbose"""
        
        detail_additions = [
            " Questo mi aiuterà a personalizzare i miei consigli per te.",
            " Sto raccogliendo queste informazioni per capire meglio la tua situazione unica.",
            " Ogni dettaglio che condividi mi permette di supportarti più efficacemente."
        ]
        
        if random.random() > 0.6:  # 40% chance
            question += random.choice(detail_additions)
        
        return question
    
    def _get_topic_transition(self, last_topic: str, current_topic: str) -> str:
        """Genera una transizione naturale tra topic"""
        
        transitions = [
            "Ora cambiamo argomento.",
            "Passiamo a parlare di qualcos'altro.",
            "Vorrei esplorare un altro aspetto.",
            "Ora mi piacerebbe sapere qualcosa su...",
            "Cambiando tema,",
            "A proposito di un'altra cosa,"
        ]
        
        return random.choice(transitions)
    
    def _generate_fallback_question(self, personality_profile: PersonalityProfile) -> str:
        """Genera una domanda di fallback quando non trova template appropriati"""
        
        fallback_questions = {
            "analytical": "Puoi darmi più dettagli su questo aspetto specifico?",
            "emotional": "Come ti senti riguardo a quello di cui stiamo parlando?",
            "practical": "Cosa succede di solito nella tua routine quotidiana?",
            "social": "Com'è la situazione quando sei con altre persone?"
        }
        
        return fallback_questions.get(
            personality_profile.primary_type,
            "Dimmi di più su questo argomento."
        )
    
    def _load_question_templates(self) -> Dict[str, QuestionTemplate]:
        """Carica i template delle domande"""
        
        return {
            "demographics": QuestionTemplate(
                base_question="Potresti dirmi qualcosa su di te, come l'età e la situazione generale?",
                analytical_variant="Per personalizzare i miei consigli con precisione, mi servono alcuni dati demografici di base. Potresti condividere la tua età e genere?",
                emotional_variant="Per conoscerti meglio come persona e offrirti il supporto più adatto, mi piacerebbe sapere qualcosa in più su di te. Ti va di condividere la tua età e come preferisci essere considerato/a?",
                practical_variant="Per darti consigli pratici e mirati, dimmi: quanti anni hai e qual è la tua situazione di vita attuale?",
                social_variant="Iniziamo a conoscerci! Mi piacerebbe sapere qualcosa in più su di te - età, come ti piace definirti, la tua situazione...",
                sensitivity_level="low"
            ),
            
            "goals": QuestionTemplate(
                base_question="Quali sono i tuoi obiettivi per la salute e l'alimentazione?",
                analytical_variant="Quali sono i tuoi obiettivi specifici e misurabili per la salute e l'alimentazione? Preferisci target numerici o miglioramenti qualitativi?",
                emotional_variant="Cosa speri di raggiungere in questo percorso? Come ti piacerebbe sentirti? Quali sogni hai per il tuo benessere?",
                practical_variant="Quale risultato concreto vorresti ottenere nei prossimi 3-6 mesi? Su cosa vuoi concentrarti principalmente?",
                social_variant="Condividiamo gli obiettivi! Cosa ti piacerebbe migliorare nella tua vita? Anche in relazione a come ti senti con gli altri?",
                sensitivity_level="medium"
            ),
            
            "eating_habits": QuestionTemplate(
                base_question="Com'è attualmente la tua alimentazione quotidiana?",
                analytical_variant="Descrivimi il pattern tipico della tua alimentazione: orari, frequenza dei pasti, porzioni approssimative, e eventuali regolarità che hai notato.",
                emotional_variant="Raccontami del tuo rapporto con il cibo. Come ti senti durante i pasti? Ci sono momenti della giornata in cui mangi diversamente?",
                practical_variant="Descrivimi una giornata tipo dal punto di vista alimentare: cosa mangi, quando, e come organizzi i tuoi pasti?",
                social_variant="Come sono i tuoi pasti? Mangi spesso con altre persone? Come influisce il contesto sociale sulla tua alimentazione?",
                sensitivity_level="medium"
            ),
            
            "activity": QuestionTemplate(
                base_question="Che tipo di attività fisica fai di solito?",
                analytical_variant="Potresti quantificare il tuo livello di attività fisica? Frequenza settimanale, durata, intensità, e tipi di esercizio che pratichi?",
                emotional_variant="Come vivi l'attività fisica? Ti piace muoverti? Ci sono attività che ti fanno sentire bene o che invece eviti?",
                practical_variant="Che sport o attività fisiche fai durante la settimana? Quanto tempo riesci a dedicarci con i tuoi impegni?",
                social_variant="Fai attività fisica? Ti piace allenarti da solo/a o preferisci la compagnia? Pratichi sport di gruppo?",
                sensitivity_level="low"
            ),
            
            "analytical_warmup": QuestionTemplate(
                base_question="Dimmi qualcosa della tua situazione attuale.",
                analytical_variant="Mi piace lavorare con dati concreti. Potresti descrivermi oggettivamente la tua situazione attuale dal punto di vista nutrizionale e di forma fisica?",
                emotional_variant="Prima di entrare nei dettagli, mi piacerebbe capire come ti senti oggi riguardo alla tua salute e benessere.",
                practical_variant="Iniziamo dal concreto: quali sono le sfide principali che stai affrontando nella tua routine di salute?",
                social_variant="Raccontami un po' di te e di come vivi il tema della salute nel tuo ambiente sociale e familiare.",
                sensitivity_level="low"
            ),
            
            "generic_assessment": QuestionTemplate(
                base_question="Dimmi di più su questo aspetto.",
                analytical_variant="Potresti fornirmi dettagli più specifici e misurabili su questo punto?",
                emotional_variant="Come ti senti riguardo a quello che stiamo discutendo? Che significato ha per te?",
                practical_variant="Come si traduce questo nella tua vita di tutti i giorni?",
                social_variant="Come influisce questo sulle tue relazioni e sulla tua vita sociale?",
                sensitivity_level="medium"
            )
        }
    
    def _load_warmup_questions(self) -> Dict[str, List[str]]:
        """Carica domande di warmup per fase iniziale"""
        
        return {
            "first_contact": {
                "analytical": [
                    "Benvenuto! Sono Arnold. Uso un approccio basato su evidenze per il benessere. Quali sono i tuoi obiettivi principali?",
                    "Ciao! Sono Arnold, il tuo consulente nutrizionale AI. Per iniziare con il metodo giusto, dimmi: cosa vorresti ottenere?"
                ],
                "emotional": [
                    "Ciao! Sono Arnold, sono qui per ascoltarti. Come ti senti oggi riguardo alla tua salute?",
                    "Benvenuto! Sono Arnold. Questo è un posto sicuro dove puoi condividere. Come va il tuo rapporto con il benessere?"
                ],
                "practical": [
                    "Ciao! Sono Arnold. Andiamo al dunque: qual è la tua sfida principale con alimentazione o fitness?",
                    "Benvenuto! Sono Arnold. Mi piacciono le soluzioni concrete. Su cosa vuoi lavorare?"
                ],
                "social": [
                    "Ciao! Sono Arnold! Sono entusiasta di conoscerti. Raccontami la tua storia con la salute!",
                    "Benvenuto! Sono Arnold. Adoro le conversazioni! Come va la tua vita dal punto di vista del benessere?"
                ]
            }
        }
    
    def _load_followup_generators(self) -> Dict[str, Any]:
        """Carica generatori per follow-up specifici"""
        
        return {
            "vague_response": {
                "gentle_probe": "Non c'è fretta. Quando ti senti pronto/a, mi piacerebbe sapere qualche dettaglio in più.",
                "specific_example": "Facciamo un esempio: ieri come è andata?",
                "alternative_angle": "Proviamo da un altro punto di vista: cosa noti di solito quando..."
            },
            "detailed_response": {
                "acknowledge_depth": "Vedo che c'è molto da esplorare in quello che mi dici.",
                "pick_thread": "Mi colpisce particolarmente quando menzioni...",
                "go_deeper": "C'è un aspetto che ti sembra più importante degli altri?"
            }
        }
    
    def _load_transition_phrases(self) -> Dict[str, List[str]]:
        """Carica frasi di transizione per cambi di argomento"""
        
        return {
            "topic_change": [
                "Ora vorrei parlare di qualcos'altro.",
                "Cambiando argomento,",
                "Passiamo a un altro aspetto:",
                "Mi piacerebbe esplorare anche...",
                "Un'altra cosa che mi interessa sapere è..."
            ],
            "phase_transition": {
                "warmup_to_assessment": [
                    "Perfetto, ora che ci conosciamo un po' meglio...",
                    "Bene! Ora possiamo entrare più nel dettaglio.",
                    "Ottimo inizio! Ora vorrei capire meglio..."
                ],
                "assessment_to_planning": [
                    "Basandoci su quello che mi hai raccontato...",
                    "Ora che ho un quadro della situazione...",
                    "Con queste informazioni, possiamo iniziare a pensare..."
                ]
            }
        }