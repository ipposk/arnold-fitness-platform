# ARNOLD AI NUTRITIONIST - Guida Completa

## 📋 INDICE
1. [Cos'è Arnold](#cosè-arnold)
2. [Architettura del Sistema](#architettura-del-sistema)
3. [Sistema Checklist-Driven](#sistema-checklist-driven)
4. [Componenti Tecnici](#componenti-tecnici)
5. [Come Usare Arnold](#come-usare-arnold)
6. [Flusso di Lavoro Dettagliato](#flusso-di-lavoro-dettagliato)
7. [Configurazione e Installazione](#configurazione-e-installazione)
8. [Esempi Pratici](#esempi-pratici)
9. [Troubleshooting](#troubleshooting)
10. [Sviluppo e Architettura Tecnica](#sviluppo-e-architettura-tecnica)

---

## Cos'è Arnold

**Arnold AI Nutritionist** è un sistema di coaching nutrizionale basato su intelligenza artificiale che segue un approccio professionale e sistematico. A differenza delle app tradizionali che danno consigli immediati, Arnold segue un processo rigoroso di assessment prima di fornire qualsiasi raccomandazione.

### 🎯 Filosofia
- **Approccio Professionale**: Come un vero nutrizionista, raccoglie tutti i dati necessari prima di dare consigli
- **Sistematico**: Segue checklist evidence-based per non perdere informazioni cruciali
- **Personalizzato**: Adatta lo stile comunicativo al profilo psicologico dell'utente
- **Sicuro**: Non bypassa mai l'assessment completo per garantire consigli appropriati

### 🏗️ Origine
Arnold deriva dall'architettura di **Penelope**, un sistema di penetration testing automatizzato. L'architettura modulare è stata adattata dal dominio cybersecurity al coaching nutrizionale, mantenendo la stessa logica rigorosa di workflow e checklist.

---

## Architettura del Sistema

### 🎪 Architettura ad Alto Livello

```
┌─────────────────────────────────────────────────────────────┐
│                    ARNOLD AI NUTRITIONIST                  │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface (arnold_cli_checklist_driven.py)            │
├─────────────────────────────────────────────────────────────┤
│  Checklist-Driven Orchestrator                             │
│  ├── Personality Profiler (stile comunicativo)             │
│  ├── Checklist Manager (binario obbligatorio)              │
│  ├── Troubleshooter (verifica completezza)                 │
│  └── Context Manager (JSON strutturato)                    │
├─────────────────────────────────────────────────────────────┤
│  Storage Layer                                              │
│  ├── Checklist JSON Files (data/checklists/)               │
│  ├── Context JSON (user profiles)                          │
│  └── Knowledge Base RAG (Qdrant - futuro)                  │
└─────────────────────────────────────────────────────────────┘
```

### 🧩 Componenti Principali

#### 1. **Orchestrator Checklist-Driven**
- **File**: `src/orchestrator/checklist_driven_orchestrator.py`
- **Funzione**: Cervello del sistema, coordina tutto il flusso
- **Responsabilità**: 
  - Determina quale checklist usare
  - Trova il check corrente
  - Verifica completezza con troubleshooter
  - Aggiorna context JSON
  - Personalizza stile comunicativo

#### 2. **Sistema Checklist**
- **Directory**: `data/checklists/`
- **Tipi di Checklist**:
  - `onboarding_checklist.json` - Primo utilizzo (8 check)
  - `daily_checkin_checklist.json` - Check-in regolari
  - `reconnection_checklist.json` - Dopo assenza >30 giorni
- **Funzione**: Binario obbligatorio per raccolta dati sistematica

#### 3. **Visualizzazione Progress**
- **File**: `src/checklist_manager/checklist_progress_display.py`
- **Funzione**: Mostra visivamente lo stato delle checklist
- **Elementi**:
  - ✅ Check completati
  - 🔄 Check in corso
  - ⏸️ Check in attesa
  - 👉 Check corrente
  - Barra di progresso percentuale

#### 4. **Context Manager**
- **Funzione**: Mantiene stato utente in JSON strutturato
- **Schema**: Segue `context_path` delle checklist
- **Esempio**:
```json
{
  "user_profile": {
    "personal_info": {
      "name": {"first_name": "Francesco"},
      "age": {"age": 29}
    }
  },
  "fitness_profile": {
    "anthropometric_data": {
      "height": {"height_cm": 173},
      "current_weight": {"weight_kg": 96}
    }
  }
}
```

---

## Sistema Checklist-Driven

### 🎯 Principi Fondamentali

#### 1. **Checklist come Binario Obbligatorio**
- Mai bypassare i check
- Sequenza obbligatoria: pending → in_progress → completed
- Dipendenze tra task rispettate
- Troubleshooter verifica completezza prima di avanzare

#### 2. **Personalizzazione del COME, non del COSA**
- **COSA chiedere**: Determinato dalla checklist (fisso)
- **COME chiedere**: Personalizzato in base al profilo utente
- Esempio:
  - Check: "Raccolta peso corporeo"
  - Analitico: "Per completare l'assessment, quanto pesi attualmente?"
  - Emotivo: "Mi aiuteresti a conoscerti meglio? Quanto pesi?"
  - Pratico: "Perfetto! Adesso quanto pesi?"

#### 3. **Context JSON Always Updated**
- Ogni check completed aggiorna il context
- Segue il `context_path` specificato nella checklist
- Single source of truth per tutti i dati utente

### 📋 Tipi di Checklist

#### Onboarding Checklist (Primo Utilizzo)
```
📁 Informazioni di Base (ONB-basics)
├── ONB-001: Nome ✅
├── ONB-002: Età e data di nascita 🔄
└── ONB-003: Genere ⏸️

📁 Dati Fisici Iniziali (ONB-anthropometric)  
├── ONB-004: Altezza attuale ⏸️
├── ONB-005: Peso attuale ⏸️
└── ONB-006: Obiettivo principale ⏸️

📁 Stile di Vita e Preferenze (ONB-lifestyle)
├── ONB-007: Livello di attività fisica ⏸️
└── ONB-008: Preferenze alimentari ⏸️
```

#### Daily Check-in Checklist
- Progress tracking (peso, aderenza)
- Livelli energia e benessere
- Necessità di aggiustamenti

#### Reconnection Checklist  
- Aggiornamento dopo assenza
- Revisione obiettivi
- Rivalutazione del piano

### 🔄 Flusso Checklist

```
1. DETERMINA CHECKLIST
   ├── sessions_count == 0 → onboarding
   ├── days_since_last > 30 → reconnection  
   └── else → daily_checkin

2. TROVA CHECK CORRENTE
   ├── Primo in_progress
   └── Altrimenti primo pending (con dipendenze soddisfatte)

3. PROCESSA INPUT UTENTE
   ├── Estrae dati dall'input
   ├── Verifica completezza con troubleshooter
   └── Se completo: mark completed + avanza
   └── Se incompleto: richiede dati mancanti

4. AGGIORNA CONTEXT
   ├── Segue context_path del check
   └── JSON sempre sincronizzato

5. GENERA RISPOSTA PERSONALIZZATA
   ├── Stile basato su profilo utente
   └── Contenuto sempre checklist-driven
```

---

## Componenti Tecnici

### 🧠 Personality Profiler
- **Directory**: `src/personality_profiler/`
- **Componenti**:
  - `StyleAnalyzer`: Analizza verbosità, tono emotivo, energia
  - `PersonalityMapper`: Mappa a profili (analytical, emotional, practical, social)
  - `EmpathyAdapter`: Adatta linguaggio al profilo
- **Uso**: Solo per personalizzazione stile comunicativo

### 🎯 Adaptive Prompting
- **Directory**: `src/adaptive_prompting/`
- **Componenti**:
  - `QuestionGenerator`: Genera domande personalizzate
  - `PromptPersonalizer`: Personalizza prompt LLM
  - `ToneAdjuster`: Regola tono delle risposte

### 🔄 Conversation Director
- **Directory**: `src/conversation_director/`
- **Componenti**:
  - `FlowManager`: Gestisce fasi conversazionali
  - `QuestionSelector`: Seleziona domande appropriate
  - `ContextBridge`: Collega checklist a flusso conversazionale

### 📊 Checklist Manager
- **Directory**: `src/checklist_manager/`
- **Componenti**:
  - `ChecklistProgressDisplay`: Visualizzazione progress nel CLI

---

## Come Usare Arnold

### 🚀 Avvio Rapido

```bash
# 1. Vai nella directory backend
cd arnold-fitness/arnold-fitness-backend

# 2. Avvia il CLI checklist-driven
python3 arnold_cli_checklist_driven.py
```

### 🖥️ Interfaccia CLI

#### Schermata di Benvenuto
```
====================================================================
   ARNOLD AI NUTRITIONIST - Sistema Checklist-Driven
====================================================================

🎯 APPROCCIO PROFESSIONALE GUIDATO

Arnold segue un approccio sistematico basato su checklist professionali.
Ogni domanda ha uno scopo preciso per costruire il tuo profilo completo.

✅ COSA ASPETTARTI:
• Domande strutturate e sequenziali
• Progress visibile per ogni step  
• Assessment completo prima dei consigli
• Personalizzazione basata sul tuo stile di comunicazione
```

#### Visualizzazione Progress
```
📊 AVANZAMENTO: 3/8 completati (37.5%)
██████████░░░░░░░░░░░░ 37.5%

📁 Informazioni di Base
  ✅ ONB-001: Nome
  ✅ ONB-002: Età  
  👉 ONB-003: Genere (IN CORSO)

📁 Dati Fisici Iniziali  
  ⏸️ ONB-004: Altezza
  ⏸️ ONB-005: Peso
```

#### Finestra di Contesto
```
← PRECEDENTE    | ● IN CORSO      | PROSSIMO →
ONB-002         | ONB-003        | ONB-004
Età             | Genere         | Altezza  
✅ Completato   | 👉 Raccogliendo| ⏸️ In attesa
```

### 🎮 Comandi Disponibili

- `/progress` - Mostra progress completo checklist
- `/checklist` - Visualizza intera checklist con stati
- `/context` - Mostra context JSON corrente  
- `/clear` - Pulisce schermo
- `/help` - Mostra aiuto comandi
- `/exit` - Esci dalla sessione

---

## Flusso di Lavoro Dettagliato

### 📝 Esempio di Conversazione Completa

#### Turno 1: Nome
```
👤 Input: "Francesco"
🧠 Sistema: 
   ├── Analizza personalità → practical
   ├── Check corrente → ONB-001 (Nome)  
   ├── Estrae dati → {"first_name": "Francesco"}
   ├── Verifica completezza → ✅ completo
   ├── Marca completed → ONB-001 ✅
   ├── Avanza → ONB-002 (Età) 👉
   └── Aggiorna context → user_profile.personal_info.name

🤖 Arnold: "Perfetto! Quanti anni hai?"
📊 Progress: 12.5% (1/8)
```

#### Turno 2: Età
```  
👤 Input: "29 anni"
🧠 Sistema:
   ├── Check corrente → ONB-002 (Età)
   ├── Estrae dati → {"age": 29}  
   ├── Verifica completezza → ✅ completo
   ├── Marca completed → ONB-002 ✅
   ├── Avanza → ONB-003 (Genere) 👉
   └── Aggiorna context → user_profile.personal_info.age

🤖 Arnold: "Ottimo! Sei maschio o femmina?"
📊 Progress: 25.0% (2/8)
```

### 🔍 Estrazione Dati Intelligente

Arnold riconosce diversi pattern di input:

#### Nomi
- ✅ "Francesco" → `first_name: "Francesco"`
- ✅ "Mi chiamo Marco" → `first_name: "Marco"`
- ✅ "Sono Giulia" → `first_name: "Giulia"`

#### Età
- ✅ "29 anni" → `age: 29`
- ✅ "29" → `age: 29`
- ✅ "Ho 35 anni" → `age: 35`

#### Misure Fisiche
- ✅ "173 cm" → `height_cm: 173`
- ✅ "1.73 m" → `height_cm: 173`
- ✅ "96 kg" → `weight_kg: 96`

### 🛡️ Troubleshooter in Azione

Se l'input è incompleto:

```
👤 Input: "Alto"  (per check Altezza)
🧠 Sistema:
   ├── Estrae dati → {} (vuoto, manca numero)
   ├── Verifica completezza → ❌ incompleto  
   ├── Missing data → ["height_cm"]
   └── Non avanza, richiede completamento

🤖 Arnold: "Mi servirebbe il numero preciso. Quanto sei alto in centimetri?"
```

---

## Configurazione e Installazione

### 📦 Dipendenze

#### Python Requirements
```bash
pip install -r requirements.txt
```

Principali dipendenze:
- `colorama` - Colori terminale
- `python-dotenv` - Gestione environment variables
- `pathlib` - Manipolazione percorsi

#### Environment Variables (Opzionali)
```bash
# File .env (per funzionalità avanzate future)
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=arnold_fitness_chunks
```

### 🗂️ Struttura Directory

```
arnold-fitness-backend/
├── arnold_cli_checklist_driven.py     # CLI principale
├── data/
│   └── checklists/                    # Checklist JSON
│       ├── onboarding_checklist.json
│       ├── daily_checkin_checklist.json
│       └── reconnection_checklist.json
├── src/
│   ├── orchestrator/
│   │   └── checklist_driven_orchestrator.py
│   ├── checklist_manager/
│   │   ├── __init__.py
│   │   └── checklist_progress_display.py
│   ├── personality_profiler/
│   ├── adaptive_prompting/
│   └── conversation_director/
└── test_checklist_system.py          # Test completo
```

### 🧪 Testing del Sistema

```bash
# Test completo del sistema
python3 test_checklist_system.py

# Debug specifico
python3 debug_orchestrator.py
python3 debug_process_input.py
```

---

## Esempi Pratici

### 📋 Esempio Checklist JSON

```json
{
  "phase_id": "ONB",
  "title": "Onboarding - Primo Utilizzo",
  "description": "Checklist completa per nuovi utenti",
  "trigger_condition": "user.sessions_count == 0",
  "tasks": [
    {
      "task_id": "ONB-basics",
      "title": "Informazioni di Base",
      "checks": [
        {
          "check_id": "ONB-001",
          "description": "Nome",
          "context_path": "user_profile.personal_info.name",
          "required_data": ["first_name"],
          "state": "pending",
          "priority": "critical",
          "example_questions": [
            "Come ti chiami?",
            "Qual è il tuo nome?"
          ]
        }
      ]
    }
  ]
}
```

### 🧠 Esempio Context JSON Risultante

```json
{
  "sessions_count": 0,
  "days_since_last_session": 0,
  "user_profile": {
    "personal_info": {
      "name": {
        "first_name": "Francesco"
      },
      "age": {
        "age": 29
      },
      "gender": {
        "gender": "male"
      }
    }
  },
  "fitness_profile": {
    "anthropometric_data": {
      "height": {
        "height_cm": 173
      },
      "current_weight": {
        "weight_kg": 96,
        "measurement_date": "2025-08-22T18:07:07.969518"
      }
    },
    "goals": {
      "primary_goal": {
        "goal_type": "weight_loss",
        "target_weight": 85,
        "timeline": "6_months"
      }
    }
  }
}
```

### 💬 Esempio Personalizzazione Stile

#### Utente Analitico
```
Input: "Vorrei dati precisi su macro e micronutrienti"
Profilo: analytical
Risposta: "Per completare l'assessment sistematico, quanto pesi attualmente? Questo dato è essenziale per calcolare il tuo fabbisogno calorico."
```

#### Utente Emotivo  
```
Input: "Mi sento frustrato per il mio peso"
Profilo: emotional  
Risposta: "Capisco la tua frustrazione, è normale sentirsi così. Mi aiuteresti a conoscerti meglio condividendo quanto pesi attualmente?"
```

#### Utente Pratico
```
Input: "Dimmi cosa devo fare"
Profilo: practical
Risposta: "Perfetto! Andiamo dritti al punto. Quanto pesi attualmente?"
```

---

## Troubleshooting

### 🐛 Problemi Comuni

#### Errore: "OSError: Operation not supported on socket"
```bash
# Problema: Terminal size non rilevabile in ambienti non interattivi
# Soluzione: Il sistema ha fallback automatico a 80 caratteri
```

#### Estrazione Dati Non Funziona
```python
# Debug: Testa l'estrazione manualmente
from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
orch = ChecklistDrivenOrchestrator('TEST', {'sessions_count': 0})
result = orch._extract_data_from_input("Francesco", ["first_name"])
print(result)  # Dovrebbe essere {'first_name': 'Francesco'}
```

#### Checklist Non Si Carica
```bash
# Verifica che i file esistano
ls -la data/checklists/
# Dovrebbe mostrare onboarding_checklist.json, etc.
```

#### Progress Non Si Aggiorna
- Il sistema marca i check come completed solo quando TUTTI i required_data sono estratti
- Usa `/context` per vedere cosa è stato salvato
- Usa `/progress` per vedere lo stato completo

### 🔧 Debug Tools

#### Test Sistema Completo
```bash
python3 test_checklist_system.py
# Output atteso: 🎉 TUTTI I TEST SUPERATI!
```

#### Debug Step-by-Step
```bash  
python3 debug_process_input.py
# Mostra ogni step dell'elaborazione input
```

#### Visualizzazione Checklist
```bash
# Nel CLI usa:
/checklist  # Mostra checklist completa
/progress   # Mostra progress dettagliato
/context    # Mostra JSON context
```

---

## Sviluppo e Architettura Tecnica

### 🏗️ Design Patterns Utilizzati

#### 1. **Orchestrator Pattern**
- Singolo punto di coordinamento
- Gestisce flusso tra componenti
- Mantiene stato centralizzato

#### 2. **Chain of Responsibility**
- Check delle dipendenze tra task
- Pipeline di elaborazione input
- Fallback gerarchici

#### 3. **State Machine**
- Stati check: pending → in_progress → completed
- Transizioni controllate dal troubleshooter
- Context JSON come stato persistente

#### 4. **Template Method**
- Flusso fisso per elaborazione input
- Personalizzazione nei dettagli (stile comunicativo)
- Hook points per estensione

### 🧩 Estensibilità

#### Aggiungere Nuove Checklist
```json
// Crea nuovo file in data/checklists/
{
  "phase_id": "NEW",
  "title": "Nuova Checklist",
  "trigger_condition": "custom_condition",
  "tasks": [...]
}
```

#### Aggiungere Nuovi Pattern Estrazione
```python
# In _extract_data_from_input():
if 'new_field' in required_fields:
    # Aggiungi logica di estrazione
    new_match = re.search(r'pattern', lower_input)
    if new_match:
        extracted['new_field'] = new_match.group(1)
```

#### Personalizzare Stili Comunicativi  
```python
# In _personalize_question_style():
if personality_type == 'new_type':
    return f"Nuovo stile: {base_question}"
```

### 🎯 Principi di Design

#### 1. **Checklist-First**
- Checklist determinano sempre il flusso
- Mai bypassare l'assessment
- Context JSON sempre sincronizzato

#### 2. **Graceful Degradation**
- Fallback automatici per componenti mancanti
- Personalizzazione opzionale (default neutro)
- Robustezza anche senza API keys

#### 3. **Separation of Concerns**
- COSA chiedere: Checklist JSON
- COME chiedere: Personalizzazione
- DOVE salvare: Context paths
- QUANDO avanzare: Troubleshooter

#### 4. **User Experience First**
- Progress visibile sempre
- Feedback immediato per completamenti
- Comandi di debug accessibili

---

## 📚 Conclusione

**Arnold AI Nutritionist** rappresenta un approccio innovativo al coaching nutrizionale digitale, combinando:

- 🧠 **Intelligenza Artificiale** per personalizzazione
- 📋 **Rigore Scientifico** delle checklist evidence-based  
- 🎯 **User Experience** moderna e coinvolgente
- 🛡️ **Sicurezza** nell'assessment completo prima dei consigli

Il sistema è progettato per essere:
- **Professionale**: Come un vero nutrizionista
- **Sistematico**: Nessun dato importante viene perso
- **Personalizzato**: Si adatta al tuo stile comunicativo
- **Estensibile**: Facilmente ampliabile con nuove funzionalità

Arnold non è solo un'app di fitness, è un **sistema professionale di coaching nutrizionale** che mantiene gli standard qualitativi di un consulente umano esperto, potenziato dall'intelligenza artificiale.

---

*Ultimo aggiornamento: 22 Agosto 2025*  
*Versione: 1.0.0 - Sistema Checklist-Driven Completo*