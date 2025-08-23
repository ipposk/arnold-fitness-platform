"""
Checklist-Driven Orchestrator - Orchestrator che segue rigorosamente le checklist
Rispetta la visione originale: checklist come binario obbligatorio per mantenere contesto
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid

# Import componenti esistenti
from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter

class ChecklistDrivenOrchestrator:
    """
    Orchestrator che implementa rigorosamente la logica checklist-driven:
    1. Determina quale checklist usare (onboarding/daily/reconnection)
    2. Trova il check corrente (primo in_progress o primo pending)
    3. Genera query RAG basata sul check corrente + context
    4. Personalizza SOLO lo stile di comunicazione, mai il contenuto
    5. Usa troubleshooter per garantire completezza prima di avanzare
    """
    
    def __init__(self, session_id: str, user_context: Dict = None):
        self.session_id = session_id
        self.context = user_context or {}
        
        # Componenti personalizzazione (per stile comunicativo) - con fallback sicuro
        try:
            self.style_analyzer = StyleAnalyzer()
            self.personality_mapper = PersonalityMapper() 
            self.empathy_adapter = EmpathyAdapter()
        except:
            # Usa versioni mock se i componenti non sono disponibili
            self.style_analyzer = None
            self.personality_mapper = None
            self.empathy_adapter = None
        
        # Percorsi checklist
        self.checklist_dir = Path("data/checklists")
        
        # Stato attuale
        self.current_checklist = None
        self.current_check = None
        self.personality_profile = None
        
        # Inizializza checklist all'avvio
        self._initialize_checklist()
    
    def _initialize_checklist(self) -> None:
        """Inizializza la checklist appropriata all'avvio"""
        try:
            checklist_type = self._determine_checklist_type()
            self.current_checklist = self._load_checklist(checklist_type)
            
            # Imposta il primo check come in_progress se tutto è pending
            first_check = self._find_first_pending_check()
            if first_check:
                first_check['state'] = 'in_progress'
                self.current_check = first_check
        except Exception as e:
            print(f"Warning: Could not initialize checklist: {e}")
    
    def _find_first_pending_check(self) -> Optional[Dict]:
        """Trova il primo check pending nella checklist"""
        if not self.current_checklist:
            return None
            
        for task in self.current_checklist.get('tasks', []):
            if self._check_dependencies_satisfied(task):
                for check in task.get('checks', []):
                    if check['state'] == 'pending':
                        return check
        return None
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Processo principale che segue rigorosamente la logica checklist-driven
        """
        try:
            # STEP 1: Analizza personalità dell'utente (SOLO per stile comunicativo)
            self.personality_profile = self._analyze_user_personality(user_input)
            
            # STEP 2: Determina quale checklist utilizzare (solo se non già caricata)
            if not self.current_checklist:
                checklist_type = self._determine_checklist_type()
                self.current_checklist = self._load_checklist(checklist_type)
            
            # STEP 3: Trova il check corrente (primo in_progress o pending)
            self.current_check = self._find_current_check()
            
            if not self.current_check:
                return self._generate_completion_response()
            
            # STEP 4: Usa troubleshooter per verificare se l'input completa il check corrente
            completion_result = self._check_completion_with_troubleshooter(user_input)
            
            if completion_result['is_complete']:
                # STEP 5a: Marca come completed e avanza al prossimo
                self._mark_check_completed(self.current_check['check_id'], completion_result['extracted_data'])
                self._advance_to_next_check()
                return self._generate_advancement_response()
            else:
                # STEP 5b: Richiedi completamento del check corrente
                return self._generate_completion_request_response(completion_result['missing_data'])
                
        except Exception as e:
            return self._generate_error_response(str(e))
    
    def _determine_checklist_type(self) -> str:
        """
        Determina quale checklist usare basandosi sul contesto utente
        """
        # Simulazione - nella realtà useresti dati di sessione da DynamoDB
        sessions_count = self.context.get('sessions_count', 0)
        days_since_last = self.context.get('days_since_last_session', 0)
        
        if sessions_count == 0:
            return 'onboarding'
        elif days_since_last > 30:
            return 'reconnection'
        else:
            return 'daily_checkin'
    
    def _load_checklist(self, checklist_type: str) -> Dict:
        """
        Carica la checklist appropriata dal file JSON
        """
        checklist_files = {
            'onboarding': 'onboarding_checklist.json',
            'daily_checkin': 'daily_checkin_checklist.json', 
            'reconnection': 'reconnection_checklist.json',
            'initial_assessment': 'initial_assessment_checklist.json'  # fallback
        }
        
        filename = checklist_files.get(checklist_type, 'initial_assessment_checklist.json')
        checklist_path = self.checklist_dir / filename
        
        try:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                checklist_data = json.load(f)
                return checklist_data[0] if isinstance(checklist_data, list) else checklist_data
        except FileNotFoundError:
            # Fallback al assessment iniziale
            fallback_path = self.checklist_dir / 'initial_assessment_checklist.json'
            with open(fallback_path, 'r', encoding='utf-8') as f:
                checklist_data = json.load(f)
                return checklist_data[0] if isinstance(checklist_data, list) else checklist_data
    
    def _find_current_check(self) -> Optional[Dict]:
        """
        Trova il check corrente: primo in_progress, altrimenti primo pending
        """
        # Prima cerca in_progress
        for task in self.current_checklist.get('tasks', []):
            for check in task.get('checks', []):
                if check['state'] == 'in_progress':
                    return check
        
        # Poi cerca primo pending
        for task in self.current_checklist.get('tasks', []):
            for check in task.get('checks', []):
                if check['state'] == 'pending':
                    # Verifica dipendenze se esistono
                    if self._check_dependencies_satisfied(task):
                        return check
        
        return None
    
    def _check_dependencies_satisfied(self, task: Dict) -> bool:
        """
        Verifica se le dipendenze del task sono soddisfatte
        """
        depends_on = task.get('depends_on', [])
        if not depends_on:
            return True
            
        # Verifica che tutti i task dipendenti siano completati
        for task_id in depends_on:
            if not self._is_task_completed(task_id):
                return False
        return True
    
    def _is_task_completed(self, task_id: str) -> bool:
        """
        Verifica se un task è completato
        """
        for task in self.current_checklist.get('tasks', []):
            if task['task_id'] == task_id:
                # Task completato se tutti i suoi check sono completati
                return all(check['state'] == 'completed' for check in task.get('checks', []))
        return False
    
    def _check_completion_with_troubleshooter(self, user_input: str) -> Dict:
        """
        Usa logica troubleshooter per verificare se l'input completa il check corrente
        """
        check = self.current_check
        required_data = check.get('required_data', [])
        
        # Estrazione dati semplificata (nella realtà useresti LLM dedicato)
        extracted_data = self._extract_data_from_input(user_input, required_data)
        missing_data = [field for field in required_data if field not in extracted_data]
        
        return {
            'is_complete': len(missing_data) == 0,
            'extracted_data': extracted_data,
            'missing_data': missing_data
        }
    
    def _extract_data_from_input(self, user_input: str, required_fields: List[str]) -> Dict:
        """
        Estrae dati dall'input dell'utente (versione semplificata)
        Nella realtà useresti un LLM dedicato per l'estrazione
        """
        extracted = {}
        lower_input = user_input.lower()
        
        # Pattern semplici per demo
        if 'first_name' in required_fields or 'name' in required_fields:
            if 'mi chiamo' in lower_input or 'sono' in lower_input:
                # Estrazione semplificata del nome
                words = user_input.split()
                if 'mi chiamo' in lower_input:
                    name_idx = lower_input.split().index('chiamo') + 1
                    if name_idx < len(words):
                        extracted['first_name'] = words[name_idx].strip(',.!?')
                elif 'sono' in lower_input:
                    name_idx = lower_input.split().index('sono') + 1  
                    if name_idx < len(words):
                        extracted['first_name'] = words[name_idx].strip(',.!?')
            else:
                # Se è solo una parola e contiene solo lettere, probabilmente è un nome
                words = user_input.strip().split()
                if len(words) == 1 and words[0].isalpha() and len(words[0]) > 1:
                    extracted['first_name'] = words[0].strip(',.!?')
                # Se ci sono 2-3 parole e sembrano nomi (solo lettere)
                elif 1 <= len(words) <= 3 and all(word.isalpha() for word in words):
                    extracted['first_name'] = words[0].strip(',.!?')
        
        if 'age' in required_fields:
            import re
            # Pattern più flessibili per età
            age_patterns = [
                r'\b(\d{1,2})\s*(anni|years old|anno)',  # "29 anni", "29 anno"
                r'ho\s+(\d{1,2})\s*(anni|anno)',          # "ho 29 anni"
                r'^(\d{1,2})$'                             # solo numero "29"
            ]
            
            for pattern in age_patterns:
                age_match = re.search(pattern, lower_input)
                if age_match:
                    try:
                        age = int(age_match.group(1))
                        if 10 <= age <= 120:  # Range ragionevole
                            extracted['age'] = age
                            break
                    except (ValueError, IndexError):
                        continue
        
        if 'height_cm' in required_fields:
            import re  
            height_match = re.search(r'(\d{1,3})\s*cm|(\d\.\d{2})\s*m', lower_input)
            if height_match:
                if height_match.group(1):  # cm
                    extracted['height_cm'] = int(height_match.group(1))
                elif height_match.group(2):  # meters
                    extracted['height_cm'] = int(float(height_match.group(2)) * 100)
        
        if 'weight_kg' in required_fields:
            import re
            weight_match = re.search(r'(\d{1,3})\s*kg', lower_input)
            if weight_match:
                extracted['weight_kg'] = int(weight_match.group(1))
                extracted['measurement_date'] = datetime.now().isoformat()
        
        return extracted
    
    def _mark_check_completed(self, check_id: str, extracted_data: Dict) -> None:
        """
        Marca un check come completato e aggiorna il context
        """
        # Aggiorna lo stato nella checklist
        for task in self.current_checklist.get('tasks', []):
            for check in task.get('checks', []):
                if check['check_id'] == check_id:
                    check['state'] = 'completed'
                    check['timestamp'] = datetime.now().isoformat()
                    check['notes'] = f"Completed with data: {extracted_data}"
                    
                    # Aggiorna il context JSON seguendo il context_path
                    if check.get('context_path'):
                        self._update_context_path(check['context_path'], extracted_data)
                    break
    
    def _update_context_path(self, context_path: str, data: Dict) -> None:
        """
        Aggiorna il context JSON seguendo il path specificato
        """
        # Navigazione nel context JSON (es: "user_profile.personal_info.name")
        path_parts = context_path.split('.')
        current = self.context
        
        # Crea la struttura se non esiste
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Aggiorna i dati
        final_key = path_parts[-1]
        if final_key not in current:
            current[final_key] = {}
        current[final_key].update(data)
    
    def _advance_to_next_check(self) -> None:
        """
        Avanza al prossimo check pending e lo marca come in_progress
        """
        next_check = self._find_next_pending_check()
        if next_check:
            next_check['state'] = 'in_progress'
            self.current_check = next_check
    
    def _find_next_pending_check(self) -> Optional[Dict]:
        """
        Trova il prossimo check pending dopo quello corrente
        """
        current_found = False
        
        for task in self.current_checklist.get('tasks', []):
            for check in task.get('checks', []):
                if current_found and check['state'] == 'pending':
                    if self._check_dependencies_satisfied(task):
                        return check
                elif check['check_id'] == self.current_check['check_id']:
                    current_found = True
        
        return None
    
    def _analyze_user_personality(self, user_input: str) -> Dict:
        """
        Analizza la personalità SOLO per personalizzare lo stile comunicativo
        """
        if self.style_analyzer and self.personality_mapper:
            try:
                style_analysis = self.style_analyzer.analyze_text(user_input)
                personality = self.personality_mapper.map_to_profile(style_analysis)
                return personality
            except:
                pass
        
        # Fallback semplice se i componenti personalizzazione non sono disponibili
        return {'primary_type': 'practical', 'communication_preference': 'encouraging'}
    
    def _generate_completion_request_response(self, missing_data: List[str]) -> Dict:
        """
        Genera risposta che chiede il completamento del check corrente
        Personalizzata in base al profilo dell'utente
        """
        check = self.current_check
        base_question = self._generate_check_question(check, missing_data)
        
        # Personalizza lo stile basandosi sul profilo
        personalized_question = self._personalize_question_style(base_question, self.personality_profile)
        
        return {
            'response': personalized_question,
            'checklist_state': {
                'current_check_id': check['check_id'],
                'phase': self.current_checklist['phase_id'],
                'progress': self._calculate_progress()
            },
            'context_updates': {},  # Nessun aggiornamento fino al completamento
            'status': 'awaiting_completion'
        }
    
    def _generate_check_question(self, check: Dict, missing_data: List[str]) -> str:
        """
        Genera la domanda base per il check (senza personalizzazione)
        """
        # Usa esempi dalla checklist se disponibili
        if check.get('example_questions'):
            return check['example_questions'][0]
        
        # Altrimenti genera basandosi sui dati mancanti
        if 'first_name' in missing_data:
            return "Come ti chiami?"
        elif 'age' in missing_data:
            return "Quanti anni hai?"
        elif 'height_cm' in missing_data:
            return "Quanto sei alto?"
        elif 'weight_kg' in missing_data:
            return "Quanto pesi attualmente?"
        else:
            return f"Per completare '{check['description']}', ho bisogno di: {', '.join(missing_data)}"
    
    def _personalize_question_style(self, base_question: str, profile: Dict) -> str:
        """
        Personalizza SOLO lo stile della domanda basandosi sul profilo
        """
        if not profile:
            return base_question
            
        personality_type = profile.get('primary_type', 'neutral')
        
        if personality_type == 'analytical':
            return f"Per completare l'assessment iniziale, {base_question.lower()}"
        elif personality_type == 'emotional':
            return f"Mi aiuteresti a conoscerti meglio? {base_question}"
        elif personality_type == 'practical':
            return f"Perfetto! Adesso {base_question.lower()}"
        elif personality_type == 'social':
            return f"Che bello iniziare a conoscerti! {base_question}"
        else:
            return base_question
    
    def _generate_advancement_response(self) -> Dict:
        """
        Genera risposta quando si avanza al check successivo
        """
        if not self.current_check:
            return self._generate_completion_response()
            
        next_question = self._generate_check_question(self.current_check, self.current_check.get('required_data', []))
        personalized_next = self._personalize_question_style(next_question, self.personality_profile)
        
        return {
            'response': f"Perfetto! {personalized_next}",
            'checklist_state': {
                'current_check_id': self.current_check['check_id'],
                'phase': self.current_checklist['phase_id'],
                'progress': self._calculate_progress(),
                'just_completed': True
            },
            'context_updates': self.context,
            'status': 'advancing'
        }
    
    def _generate_completion_response(self) -> Dict:
        """
        Genera risposta quando tutta la checklist è completata
        """
        return {
            'response': "🎉 Fantastico! Abbiamo completato l'assessment iniziale. Ora posso creare un piano personalizzato per te!",
            'checklist_state': {
                'current_check_id': None,
                'phase': 'completed',
                'progress': 100.0
            },
            'context_updates': self.context,
            'status': 'completed'
        }
    
    def _generate_error_response(self, error: str) -> Dict:
        """
        Genera risposta di errore
        """
        return {
            'response': "Mi dispiace, ho avuto un problema tecnico. Potresti ripetere?",
            'checklist_state': {
                'error': error
            },
            'context_updates': {},
            'status': 'error'
        }
    
    def _calculate_progress(self) -> float:
        """
        Calcola la percentuale di completamento della checklist
        """
        total_checks = 0
        completed_checks = 0
        
        for task in self.current_checklist.get('tasks', []):
            for check in task.get('checks', []):
                total_checks += 1
                if check['state'] == 'completed':
                    completed_checks += 1
        
        return (completed_checks / total_checks * 100) if total_checks > 0 else 0
    
    def get_checklist_context(self) -> Dict:
        """
        Restituisce il contesto completo della checklist per il CLI
        """
        if not self.current_checklist:
            return {}
            
        previous_check = self._find_previous_check()
        next_check = self._find_next_pending_check()
        
        return {
            'checklist': self.current_checklist,
            'current_check': self.current_check,
            'previous_check': previous_check,
            'next_check': next_check,
            'progress': self._calculate_progress()
        }
    
    def _find_previous_check(self) -> Optional[Dict]:
        """
        Trova il check precedente (ultimo completato)
        """
        if not self.current_check:
            return None
            
        previous = None
        for task in self.current_checklist.get('tasks', []):
            for check in task.get('checks', []):
                if check['check_id'] == self.current_check['check_id']:
                    return previous
                if check['state'] == 'completed':
                    previous = check
        return previous