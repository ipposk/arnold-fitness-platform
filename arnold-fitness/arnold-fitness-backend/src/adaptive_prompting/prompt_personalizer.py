"""
Prompt Personalizer - Personalizza i prompt per gli LLM basandosi sul profilo utente
"""

from typing import Dict, List, Any, Optional
from ..personality_profiler import PersonalityProfile, WritingStyle
from ..conversation_director import ConversationState


class PromptPersonalizer:
    """Personalizza i prompt per gli LLM basandosi sul profilo dell'utente"""
    
    def __init__(self):
        self.base_prompts = self._load_base_prompts()
        self.personality_modifiers = self._load_personality_modifiers()
        self.context_enhancers = self._load_context_enhancers()
    
    def personalize_guidance_prompt(self,
                                  base_prompt: str,
                                  user_input: str,
                                  personality_profile: PersonalityProfile,
                                  writing_style: WritingStyle,
                                  conversation_state: ConversationState,
                                  checklist_context: Dict[str, Any]) -> str:
        """Personalizza il prompt per generare guidance basata sul profilo utente"""
        
        # Costruisci il contesto del profilo
        profile_context = self._build_profile_context(personality_profile, writing_style)
        
        # Costruisci il contesto conversazionale
        conversation_context = self._build_conversation_context(conversation_state)
        
        # Costruisci le istruzioni di personalizzazione
        personalization_instructions = self._build_personalization_instructions(
            personality_profile, writing_style, conversation_state
        )
        
        # Combina tutto nel prompt personalizzato
        personalized_prompt = f"""
{base_prompt}

=== PROFILO UTENTE ===
{profile_context}

=== CONTESTO CONVERSAZIONALE ===
{conversation_context}

=== ISTRUZIONI DI PERSONALIZZAZIONE ===
{personalization_instructions}

=== INPUT UTENTE ===
{user_input}

Genera una risposta che sia:
1. Completamente allineata al profilo psicologico dell'utente
2. Appropriata per la fase conversazionale attuale
3. Scritta nel linguaggio e tono che risuona con questa persona
4. Orientata ai suoi bisogni specifici di supporto e informazione

IMPORTANTE: La risposta deve sembrare naturale e umana, MAI robotica o generica.
"""
        
        return personalized_prompt
    
    def personalize_query_generation_prompt(self,
                                          base_prompt: str,
                                          user_input: str,
                                          personality_profile: PersonalityProfile,
                                          context: Dict[str, Any]) -> str:
        """Personalizza il prompt per la generazione di query di ricerca"""
        
        query_focus = self._determine_query_focus(personality_profile, user_input)
        
        personalized_prompt = f"""
{base_prompt}

=== STILE DI RICERCA PERSONALIZZATO ===
Per questo utente ({personality_profile.primary_type}), focalizzati su:
{query_focus}

=== INPUT UTENTE ===
{user_input}

Genera query che catturino le informazioni più rilevanti per il profilo di questo utente.
"""
        
        return personalized_prompt
    
    def personalize_context_update_prompt(self,
                                        base_prompt: str,
                                        user_input: str,
                                        personality_profile: PersonalityProfile,
                                        writing_style: WritingStyle,
                                        current_context: Dict[str, Any]) -> str:
        """Personalizza il prompt per l'aggiornamento del contesto"""
        
        interpretation_style = self._get_interpretation_style(personality_profile, writing_style)
        
        personalized_prompt = f"""
{base_prompt}

=== STILE DI INTERPRETAZIONE ===
{interpretation_style}

=== PROFILO COMUNICATIVO ===
- Tipo personalità: {personality_profile.primary_type}
- Verbosità: {writing_style.verbosity}
- Tono emotivo: {writing_style.emotional_tone}
- Livello di apertura: {writing_style.openness}
- Livello di preoccupazione: {writing_style.concern_level}

=== INPUT UTENTE ===
{user_input}

Interpreta questo input considerando il profilo dell'utente e aggiorna il contesto di conseguenza.
"""
        
        return personalized_prompt
    
    def _build_profile_context(self,
                             personality_profile: PersonalityProfile,
                             writing_style: WritingStyle) -> str:
        """Costruisce il contesto del profilo utente per il prompt"""
        
        profile_context = f"""
PROFILO PSICOLOGICO:
- Tipo primario: {personality_profile.primary_type}
- Preferenza comunicativa: {personality_profile.communication_preference}
- Stile motivazionale: {personality_profile.motivation_style}
- Bisogni di supporto: {personality_profile.support_needs}
- Processamento informazioni: {personality_profile.information_processing}

STILE DI SCRITTURA:
- Verbosità: {writing_style.verbosity}
- Tono emotivo: {writing_style.emotional_tone}
- Formalità: {writing_style.formality}
- Livello tecnico: {writing_style.technical_level}
- Apertura: {writing_style.openness}
- Energia: {writing_style.energy_level}
- Preoccupazione: {writing_style.concern_level}
"""
        
        return profile_context
    
    def _build_conversation_context(self, conversation_state: ConversationState) -> str:
        """Costruisce il contesto conversazionale per il prompt"""
        
        return f"""
STATO CONVERSAZIONE:
- Fase attuale: {conversation_state.phase.value}
- Numero turno: {conversation_state.turn_count}
- Engagement utente: {conversation_state.user_engagement}
- Completezza informazioni: {conversation_state.information_completeness:.1%}
- Forza relazione: {conversation_state.relationship_strength}
- Ultimo topic: {conversation_state.last_topic}
- Follow-up pendenti: {', '.join(conversation_state.pending_followups) if conversation_state.pending_followups else 'Nessuno'}
"""
    
    def _build_personalization_instructions(self,
                                          personality_profile: PersonalityProfile,
                                          writing_style: WritingStyle,
                                          conversation_state: ConversationState) -> str:
        """Costruisce le istruzioni specifiche di personalizzazione"""
        
        instructions = []
        
        # Istruzioni per tipo di personalità
        personality_instructions = {
            "analytical": [
                "Usa linguaggio preciso e basato su evidenze",
                "Fornisci spiegazioni logiche e strutturate",
                "Includi dati o riferimenti quando possibile",
                "Evita linguaggio eccessivamente emotivo"
            ],
            "emotional": [
                "Usa linguaggio empatico e comprensivo",
                "Valida sempre le emozioni dell'utente",
                "Includi supporto emotivo nelle risposte",
                "Connettiti ai sentimenti più che ai fatti"
            ],
            "practical": [
                "Fornisci consigli concreti e actionable",
                "Vai dritto al punto senza troppe premesse",
                "Includi passaggi specifici e pratici",
                "Focalizzati su soluzioni implementabili"
            ],
            "social": [
                "Usa linguaggio caloroso e coinvolgente",
                "Includi riferimenti a esperienze condivise",
                "Mostra entusiasmo e energia positiva",
                "Connetti l'esperienza individuale a quella sociale"
            ]
        }
        
        instructions.extend(personality_instructions.get(personality_profile.primary_type, []))
        
        # Istruzioni per stile di comunicazione
        communication_instructions = {
            "direct": ["Sii conciso e diretto", "Evita preamboli lunghi"],
            "gentle": ["Usa tono rassicurante", "Offri supporto emotivo extra"],
            "detailed": ["Fornisci spiegazioni complete", "Includi contesto e background"],
            "encouraging": ["Mantieni tono positivo", "Celebra i progressi"]
        }
        
        instructions.extend(communication_instructions.get(personality_profile.communication_preference, []))
        
        # Istruzioni per writing style
        if writing_style.verbosity == "brief":
            instructions.append("Mantieni le risposte concise e al punto")
        elif writing_style.verbosity == "verbose":
            instructions.append("Puoi essere più dettagliato e espansivo")
        
        if writing_style.energy_level == "low":
            instructions.append("Usa tono calmo e rilassato")
        elif writing_style.energy_level == "high":
            instructions.append("Mantieni energia e entusiasmo")
        
        if writing_style.concern_level == "high":
            instructions.append("Offri rassicurazione extra e supporto")
        
        # Istruzioni per fase conversazionale
        phase_instructions = {
            "warmup": ["Focalizzati sul building rapport", "Mantieni tono accogliente"],
            "assessment": ["Bilancia raccolta info con empathy", "Non fare troppe domande insieme"],
            "planning": ["Coinvolgi l'utente nelle decisioni", "Fai sentire ownership del piano"]
        }
        
        phase_key = conversation_state.phase.value
        instructions.extend(phase_instructions.get(phase_key, []))
        
        return "• " + "\n• ".join(instructions)
    
    def _determine_query_focus(self, personality_profile: PersonalityProfile, user_input: str) -> str:
        """Determina su cosa focalizzare le query di ricerca"""
        
        focus_by_type = {
            "analytical": "ricerca basata su evidenze, studi scientifici, dati quantificabili",
            "emotional": "aspetti psicologici, benessere emotivo, strategie di coping",
            "practical": "soluzioni concrete, guide step-by-step, tips implementabili",
            "social": "aspetti sociali dell'alimentazione, supporto di gruppo, esperienze condivise"
        }
        
        return focus_by_type.get(personality_profile.primary_type, focus_by_type["practical"])
    
    def _get_interpretation_style(self,
                                personality_profile: PersonalityProfile,
                                writing_style: WritingStyle) -> str:
        """Determina lo stile di interpretazione per l'input dell'utente"""
        
        style_elements = []
        
        # Base sul tipo di personalità
        if personality_profile.primary_type == "analytical":
            style_elements.append("Cerca pattern logici e informazioni concrete")
        elif personality_profile.primary_type == "emotional":
            style_elements.append("Presta particolare attenzione al contenuto emotivo")
        elif personality_profile.primary_type == "practical":
            style_elements.append("Focalizzati su azioni e behavior descritti")
        elif personality_profile.primary_type == "social":
            style_elements.append("Nota riferimenti sociali e interpersonali")
        
        # Base sullo stile di scrittura
        if writing_style.openness == "very_open":
            style_elements.append("L'utente condivide liberamente - estrai dettagli ricchi")
        elif writing_style.openness == "reserved":
            style_elements.append("L'utente è riservato - leggi tra le righe")
        
        if writing_style.concern_level == "high":
            style_elements.append("Identifica preoccupazioni e ansie per offrire supporto")
        
        return ". ".join(style_elements)
    
    def _load_base_prompts(self) -> Dict[str, str]:
        """Carica i prompt base per diversi tipi di operazione"""
        
        return {
            "task_guidance": """
Sei Arnold, un consulente nutrizionale AI empatico e professionale. 
Il tuo compito è fornire guidance personalizzata basata sull'input dell'utente e sul suo profilo.

Genera una risposta che:
- Sia professionale ma calda e accessibile
- Mostri comprensione della situazione dell'utente  
- Fornisca guidance pratica e actionable
- Incoraggi il progresso senza essere pressante
- Mantenga il focus sul benessere olistico
""",
            "context_interpretation": """
Analizza l'input dell'utente e aggiorna il contesto di conseguenza.
Estrai informazioni rilevanti per:
- Obiettivi e motivazioni
- Abitudini e comportamenti attuali
- Sfide e ostacoli
- Preferenze e vincoli
- Stato emotivo e mentale
""",
            "query_generation": """
Basandoti sull'input dell'utente, genera query di ricerca per recuperare 
informazioni rilevanti dalla knowledge base.
Le query dovrebbero catturare:
- Concetti chiave espressi dall'utente
- Problemi o sfide menzionate
- Aree di interesse per approfondimenti
- Informazioni correlate che potrebbero essere utili
"""
        }
    
    def _load_personality_modifiers(self) -> Dict[str, Dict[str, str]]:
        """Carica modificatori specifici per tipo di personalità"""
        
        return {
            "analytical": {
                "tone": "professionale e basato su evidenze",
                "language": "preciso e tecnico quando appropriato",
                "approach": "logico e strutturato",
                "evidence": "includi riferimenti a studi o dati quando possibile"
            },
            "emotional": {
                "tone": "empatico e comprensivo",
                "language": "caloroso e validante",
                "approach": "supportivo e paziente",
                "evidence": "connetti alle esperienze emotive"
            },
            "practical": {
                "tone": "diretto e orientato all'azione",
                "language": "concreto e chiaro",
                "approach": "focalizzato su soluzioni implementabili",
                "evidence": "esempi pratici e step actionable"
            },
            "social": {
                "tone": "coinvolgente e collaborativo",
                "language": "inclusivo e connettivo",
                "approach": "orientato alla community e condivisione",
                "evidence": "esempi sociali e esperienze condivise"
            }
        }
    
    def _load_context_enhancers(self) -> Dict[str, List[str]]:
        """Carica enhancer per migliorare il contesto basato sulla situazione"""
        
        return {
            "low_engagement": [
                "L'utente sembra meno coinvolto - usa approccio più gentle",
                "Potrebbe aver bisogno di più supporto emotivo",
                "Considera domande più semplici e meno invasive"
            ],
            "high_concern": [
                "L'utente mostra preoccupazione - offri rassicurazione",
                "Enfatizza sicurezza e benefici per la salute",
                "Usa linguaggio che riduce l'ansia"
            ],
            "early_conversation": [
                "Siamo nelle fasi iniziali - focalizzati su rapport building",
                "Non essere troppo tecnico o dettagliato ancora",
                "Mantieni atmosfera accogliente e non giudicante"
            ]
        }