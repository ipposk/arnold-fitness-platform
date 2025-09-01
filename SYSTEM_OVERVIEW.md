# Arnold AI Nutritionist - Workflow Sistema Completo

## Panoramica del Sistema Derivato

**Arnold** deriva direttamente da **Penelope**, un sistema di penetration testing automatizzato. L'architettura modulare è stata adattata dal dominio cybersecurity al coaching nutrizionale, mantenendo la stessa logica di workflow e checklist.

---

## Workflow Dettagliato - Mappatura File Repository

### **CICLO 1: Prima Interazione**

**Input Utente:** `"Ciao, sono Francesco e vorrei dimagrire"`

#### Step 1: User Input Analysis
- **File**: `src/llm_interfaces/user_input_interpreter_llm/user_input_interpreter_llm.py`
- **Prompt**: `src/llm_interfaces/user_input_interpreter_llm/prompt_templates/update_context_with_observation.txt`
- **Funzione**: Analizza il messaggio e aggiorna il context JSON
- **Output**: Scrive nel `db_context_schema.json` → nome=Francesco, goal=weight_loss

#### Step 2: Checklist Status Check
- **File**: `data/checklists/initial_assessment_checklist.json`
- **Logica**: Sistema verifica che siamo all'inizio → ASS-001 (status: pending)
- **Context**: `context + checklist_id` → Francesco vuole dimagrire + siamo in fase ASS-001

#### Step 3: RAG Query Generation
- **File**: `src/llm_interfaces/query_generator_llm/query_generator_llm.py`
- **Prompt**: `src/llm_interfaces/query_generator_llm/prompt_templates/query_generator.txt`
- **Input**: Context (Francesco + weight_loss) + checklist position (ASS-001)
- **Output**: Query per Qdrant → "assessment antropometrico peso altezza BMI"

#### Step 4: Knowledge Retrieval
- **File**: `src/db_fitness_interface/mock_fitness_retriever.py` (dev) / `FitnessRetriever` (prod)
- **Database**: Qdrant collection `arnold_fitness_chunks`
- **Content**: `data/fitness_knowledge/assessment/` → protocolli BMI, antropometria
- **Output**: Steps evidence-based per fare assessment iniziale

#### Step 5: Task Guidance Generation
- **File**: `src/llm_interfaces/task_guidance_llm/task_guidance_llm.py`
- **Prompt**: `src/llm_interfaces/task_guidance_llm/prompt_templates/task_guidance.txt`
- **Input**: Content retrievato + context Francesco + ASS-001
- **Output**: "Ciao Francesco! Per iniziare, mi dici quanto sei alto?"

---

### **CICLO 2+: Interazioni Successive con Troubleshooter**

**Input Utente:** `"Sono alto 1.75m"`

#### Pre-Step: Error Classification
- **File**: `src/llm_interfaces/error_classifier_llm/error_classifier_llm.py`
- **Prompt**: `src/llm_interfaces/error_classifier_llm/prompt_templates/classify_error_detection.txt`
- **Logica**: Confronta input utente con `last_output` salvato nel context
- **Decision**: L'utente ha risposto alla domanda? → routing verso troubleshooter o workflow normale

#### Troubleshooter Mode (se necessario)
- **File**: `src/llm_interfaces/troubleshooting_llm/troubleshooting_llm.py`
- **Prompt**: `src/llm_interfaces/troubleshooting_llm/prompt_templates/troubleshoot_command_issue.txt`
- **Workflow**: 
  1. **Confronta** `last_output` (domanda altezza) con user input (1.75m)
  2. **Valuta** se risposta è completa per ASS-001
  3. **Se SÌ**: Segna ASS-001 come completato, passa ad ASS-002
  4. **Se NO**: Aiuta utente a completare ASS-001

#### Orchestrator Logic
- **File**: `src/orchestrator/orchestrator.py`
- **Funzione**: `process_single_input()` coordina tutto il workflow
- **Logic Tree**:
  ```python
  if error_classifier.is_error(user_input, last_output):
      result = troubleshooter.resolve(user_input, last_output)
      if result.issue_resolved:
          return process_single_input(final_user_input)  # Ricorsione
      else:
          return troubleshooter_guidance  # Chiedi chiarimenti
  else:
      # Workflow normale Step 1-5
  ```

---

## **Mapping Checklist → Standard Nutrizionali**

### Checklist Nutrizionali (sostituti OWASP)
- **File**: `data/checklists/initial_assessment_checklist.json`
  - `ASS-001`: Raccolta peso corporeo (→ anthropometric_data.current_weight)
  - `ASS-002`: Misurazione altezza e BMI (→ anthropometric_data.height)
  - `ASS-003`: Circonferenze corporee (→ anthropometric_data.circumferences)

- **File**: `data/checklists/weight_loss_checklist.json`
  - `WL-001`: Calcolo BMR/TDEE (→ nutrition_plan.daily_calories)
  - `WL-002`: Definizione deficit calorico (→ nutrition_plan.deficit_calories)

### Knowledge Base Nutrizionale (sostituta MITRE ATT&CK)
- **Folder**: `data/fitness_knowledge/`
  - `assessment/`: Protocolli antropometrici professionali
  - `nutrition/`: Calcoli metabolici, macronutrienti
  - `training/`: Metodologie allenamento evidence-based
  - `troubleshooting/`: Gestione plateaus, motivazione

---

## **Context Management & Personalizzazione**

### Schema Context Fitness
- **File**: `src/context_validator/schemas/db_context_schema.json`
- **Sezioni**:
  ```json
  {
    "fitness_profile": {
      "anthropometric_data": { /* peso, altezza, BMI */ },
      "medical_history": { /* patologie, farmaci */ },
      "lifestyle_assessment": { /* attività, sonno, stress */ },
      "goals": { /* obiettivi, timeline */ }
    },
    "nutrition_plan": { /* calorie, macro, pasti */ },
    "progress_tracking": { /* misurazioni, aderenza */ }
  }
  ```

### Personalizzazione Multi-Sessione
- **Storage**: DynamoDB tables (`ArnoldSessions`, `ArnoldMessages`)
- **Logic**: Context accumula personalità, preferenze, trigger emotivi
- **Result**: Ogni sessione Arnold "ricorda" Francesco e adatta stile comunicativo

---

## **Entry Points e Testing**

### CLI Development
- **File**: `arnold_cli_clean.py` (nuovo, refactored)
- **Features**: 
  - Workflow 5-step visualization: `[1→2→3→4→5]`
  - Live prompt editing: `/edit task_guidance`
  - Rerun con modifiche: `/rerun`

### Backend Integration
- **File**: `backend/lambda_handlers.py`
- **Endpoint**: `process_chat_message_handler()` → orchestrator.process_single_input()
- **Deployment**: `serverless.yml` → AWS Lambda functions

### Local Testing
- **File**: `local_testing/components.py`
- **Mock Services**: DynamoDB, S3, Qdrant via `MockFitnessRetriever`
- **Same Logic**: Esatti stessi components di AWS Lambda

---

## **Miglioramenti Strategici Suggeriti**

### 1. **Checklist Enforcement Rigoroso**
- Arnold deve SEMPRE seguire checklist sequenzialmente
- NO consigli nutrizionali prima di completare assessment (ASS-001 to ASS-022)
- Troubleshooter deve verificare completion criteria per ogni check

### 2. **Context Enrichment Progressivo**
- Ogni interazione arricchisce `fitness_profile`
- Pattern recognition per personalità (perfectionist, chaotic, etc.)
- Memory di successi/fallimenti precedenti

### 3. **RAG Content Expansion**
- Current: 23 documenti base in `data/fitness_knowledge/`
- Target: Knowledge base comprehensiva con protocolli professionali
- Integration: Linee guida nutrizionisti italiani, evidenze scientifiche

### 4. **Troubleshooter Behavioral Intelligence**
- Estendere oltre "completion check"
- Riconoscimento blocchi motivazionali, emotional eating
- Strategie adattive per diverse personalità utente

---

**Questo workflow mantiene la robustezza di Penelope adattandola al coaching nutrizionale professionale, con checklist evidence-based e personalizzazione psicologica avanzata.**