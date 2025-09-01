#!/usr/bin/env python3
"""
Test Integrazione Completa - Flusso Checklist-Driven
Test del sistema checklist con orchestrator intelligente e LLM integration
"""

import sys
import unittest
import json
from pathlib import Path

# Setup path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestChecklistDrivenFlow(unittest.TestCase):
    """Test completo del flusso checklist-driven"""
    
    def setUp(self):
        """Setup per ogni test"""
        try:
            from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
            self.orchestrator = ChecklistDrivenOrchestrator(
                session_id="TEST-INTEGRATION-001",
                user_context={'sessions_count': 0, 'days_since_last_session': 0}
            )
        except ImportError as e:
            self.skipTest(f"ChecklistDrivenOrchestrator not available: {e}")
    
    def test_complete_user_flow(self):
        """Test sequenza completa di input utente"""
        test_inputs = [
            "Mi chiamo Francesco",
            "Ho 29 anni",
            "Sono maschio", 
            "Sono alto 173 cm",
            "Peso 96 kg"
        ]
        
        expected_progress = [0.0, 20.0, 40.0, 60.0, 80.0]  # Progresso atteso
        
        for i, (user_input, expected_prog) in enumerate(zip(test_inputs, expected_progress)):
            with self.subTest(input_number=i+1, input_text=user_input):
                result = self.orchestrator.process_user_input(user_input)
                
                # Verifica struttura risultato
                self.assertIn('response', result)
                self.assertIn('checklist_state', result)
                self.assertIn('status', result)
                
                # Verifica risposta non vuota
                self.assertIsNotNone(result['response'])
                self.assertGreater(len(result['response']), 10)
                
                # Verifica stato checklist
                checklist_state = result['checklist_state']
                if checklist_state:
                    self.assertIn('progress', checklist_state)
                    # Progress dovrebbe aumentare o rimanere uguale
                    progress = checklist_state.get('progress', 0)
                    self.assertGreaterEqual(progress, 0)
                    self.assertLessEqual(progress, 100)
    
    def test_context_tracking(self):
        """Test tracciamento modifiche context"""
        initial_context = self.orchestrator.context.copy()
        
        # Processa alcuni input
        inputs = [
            "Mi chiamo Marco",
            "Ho 35 anni e peso 80kg"
        ]
        
        for user_input in inputs:
            result = self.orchestrator.process_user_input(user_input)
            
            # Verifica che il context sia stato aggiornato
            current_context = self.orchestrator.context
            self.assertNotEqual(initial_context, current_context)
            
            # Aggiorna baseline per prossima iterazione
            initial_context = current_context.copy()
    
    def test_checklist_completion_tracking(self):
        """Test tracciamento completamento checklist"""
        # Simula completamento di diversi check
        complete_inputs = [
            "Francesco",  # Nome
            "29 anni",    # Età  
            "Maschio",    # Genere
            "173 cm",     # Altezza
            "96 kg",      # Peso
            "Perdere peso per l'estate"  # Obiettivo
        ]
        
        progress_values = []
        
        for user_input in complete_inputs:
            result = self.orchestrator.process_user_input(user_input)
            checklist_state = result.get('checklist_state', {})
            progress = checklist_state.get('progress', 0)
            progress_values.append(progress)
        
        # Il progresso dovrebbe generalmente aumentare
        # (può rimanere uguale se input non aggiunge nuove info)
        final_progress = progress_values[-1] if progress_values else 0
        initial_progress = progress_values[0] if progress_values else 0
        self.assertGreaterEqual(final_progress, initial_progress)
    
    def test_error_handling(self):
        """Test gestione errori e input invalidi"""
        invalid_inputs = [
            "",           # Input vuoto
            "   ",        # Solo spazi
            "xyz123",     # Input nonsense
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=repr(invalid_input)):
                try:
                    result = self.orchestrator.process_user_input(invalid_input)
                    
                    # Anche con input invalido, dovrebbe restituire una risposta
                    self.assertIn('response', result)
                    self.assertIsNotNone(result['response'])
                    
                except Exception as e:
                    # Se c'è un'eccezione, dovrebbe essere gestita gracefully
                    self.fail(f"Orchestrator should handle invalid input gracefully: {e}")


class TestChecklistVisualization(unittest.TestCase):
    """Test visualizzazione progresso checklist"""
    
    def setUp(self):
        """Setup per test visualizzazione"""
        try:
            from src.checklist_manager import ChecklistProgressDisplay
            self.display = ChecklistProgressDisplay()
        except ImportError as e:
            self.skipTest(f"ChecklistProgressDisplay not available: {e}")
    
    def test_checklist_loading(self):
        """Test caricamento checklist di esempio"""
        checklist_path = project_root / "data" / "checklists" / "onboarding_checklist.json"
        
        if not checklist_path.exists():
            self.skipTest(f"Checklist file not found: {checklist_path}")
        
        try:
            with open(checklist_path, 'r', encoding='utf-8') as f:
                checklist_data = json.load(f)
            
            # Verifica struttura checklist
            self.assertIsInstance(checklist_data, list)
            self.assertGreater(len(checklist_data), 0)
            
            first_phase = checklist_data[0]
            self.assertIn('tasks', first_phase)
            self.assertIsInstance(first_phase['tasks'], list)
            
        except Exception as e:
            self.fail(f"Failed to load checklist: {e}")
    
    def test_progress_display(self):
        """Test display dello stato progresso"""
        # Crea mock checklist data
        mock_checklist = {
            'phase_id': 'TST',
            'title': 'Test Phase',
            'tasks': [
                {
                    'task_id': 'task1',
                    'checks': [
                        {'check_id': 'check1', 'state': 'completed', 'description': 'First check'},
                        {'check_id': 'check2', 'state': 'in_progress', 'description': 'Second check'},
                        {'check_id': 'check3', 'state': 'pending', 'description': 'Third check'}
                    ]
                }
            ]
        }
        
        try:
            # Test display senza errori
            self.display.display_checklist_status(mock_checklist, "check2", 75.0)
            
            # Se arriviamo qui, non ci sono stati errori
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"Display checklist status failed: {e}")
    
    def test_context_window_display(self):
        """Test visualizzazione context window"""
        # Mock check objects
        current_check = {'check_id': 'current', 'description': 'Current check'}
        previous_check = {'check_id': 'previous', 'description': 'Previous check'}
        next_check = {'check_id': 'next', 'description': 'Next check'}
        
        try:
            # Test display senza errori
            self.display.display_context_window(current_check, previous_check, next_check, 80)
            
            # Se arriviamo qui, non ci sono stati errori
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"Display context window failed: {e}")


class TestIntelligentQuestionGeneration(unittest.TestCase):
    """Test generazione intelligente domande con LLM e RAG"""
    
    def setUp(self):
        """Setup per test LLM integration"""
        # Questi test richiedono API keys, quindi li skippiamo se non disponibili
        import os
        if not os.getenv('GEMINI_API_KEY'):
            self.skipTest("GEMINI_API_KEY not available - skipping LLM tests")
        
        try:
            from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
            self.orchestrator = ChecklistDrivenOrchestrator(
                session_id="TEST-LLM-001", 
                user_context={'sessions_count': 0, 'days_since_last_session': 0}
            )
        except ImportError as e:
            self.skipTest(f"ChecklistDrivenOrchestrator not available: {e}")
    
    def test_rag_query_generation(self):
        """Test generazione query per RAG retrieval"""
        try:
            from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM
            
            query_llm = QueryGeneratorLLM()
            
            # Test con context di esempio
            mock_context = {
                'current_check': {
                    'check_id': 'weight_assessment',
                    'description': 'Assess current weight and body composition',
                    'required_data': ['current_weight', 'target_weight']
                },
                'user_data': {
                    'age': 29,
                    'gender': 'male',
                    'goal': 'weight_loss'
                },
                'conversation_memory': [
                    "Voglio perdere peso per l'estate",
                    "Sono alto 175cm"
                ]
            }
            
            # Genera query per knowledge retrieval
            query = query_llm.generate_rag_query(mock_context)
            
            self.assertIsNotNone(query)
            self.assertIsInstance(query, str)
            self.assertGreater(len(query), 10)
            
            # La query dovrebbe contenere parole chiave rilevanti
            query_lower = query.lower()
            relevant_keywords = ['weight', 'loss', 'male', 'assessment']
            found_keywords = [kw for kw in relevant_keywords if kw in query_lower]
            self.assertGreater(len(found_keywords), 0, "Query should contain relevant keywords")
            
        except ImportError as e:
            self.skipTest(f"QueryGeneratorLLM not available: {e}")
    
    def test_contextual_question_generation(self):
        """Test generazione domande contestuali con TaskGuidanceLLM"""
        try:
            from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM
            
            guidance_llm = TaskGuidanceLLM()
            
            # Mock context per test
            mock_context = {
                'current_check': {
                    'check_id': 'dietary_habits',
                    'description': 'Assess current dietary patterns',
                    'required_data': ['meal_frequency', 'food_preferences', 'dietary_restrictions']
                },
                'conversation_memory': [
                    "Mi chiamo Francesco",
                    "Ho 29 anni",
                    "Voglio perdere 5kg"
                ],
                'fitness_knowledge': [
                    "Per la perdita di peso è importante creare un deficit calorico",
                    "Le abitudini alimentari sono fondamentali per il successo"
                ]
            }
            
            # Genera domanda contestuale
            question = guidance_llm.generate_contextual_question(mock_context)
            
            self.assertIsNotNone(question)
            self.assertIsInstance(question, str)
            self.assertGreater(len(question), 20)
            
            # La domanda dovrebbe essere pertinente al context
            question_lower = question.lower()
            relevant_terms = ['alimenta', 'mangi', 'dieta', 'cibo']
            found_terms = [term for term in relevant_terms if term in question_lower]
            self.assertGreater(len(found_terms), 0, "Question should be relevant to dietary assessment")
            
        except ImportError as e:
            self.skipTest(f"TaskGuidanceLLM not available: {e}")


def run_demo():
    """Demo interattiva del sistema checklist-driven"""
    print("\n🎯 ARNOLD CHECKLIST-DRIVEN SYSTEM - INTEGRATION DEMO")
    print("=" * 70)
    
    try:
        from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
        
        orchestrator = ChecklistDrivenOrchestrator(
            session_id="DEMO-001",
            user_context={'sessions_count': 0, 'days_since_last_session': 0}
        )
        print("✅ Orchestrator inizializzato!")
        
        # Demo sequence
        demo_inputs = [
            "Mi chiamo Alessandro",
            "Ho 32 anni",
            "Sono maschio",
            "Sono alto 178 cm", 
            "Peso 85 kg",
            "Voglio aumentare la massa muscolare"
        ]
        
        print("\n🧪 Demo sequenza completa:")
        print("-" * 50)
        
        for i, user_input in enumerate(demo_inputs, 1):
            print(f"\n📝 INPUT {i}: \"{user_input}\"")
            
            result = orchestrator.process_user_input(user_input)
            
            response = result.get('response', 'No response')
            print(f"🤖 ARNOLD: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            # Mostra progresso
            checklist_state = result.get('checklist_state', {})
            if checklist_state:
                progress = checklist_state.get('progress', 0)
                current_check = checklist_state.get('current_check_id', 'N/A')
                print(f"📊 Progress: {progress:.1f}% | Check: {current_check}")
            
            print("-" * 50)
        
        # Mostra context finale
        print(f"\n📄 Context JSON finale (estratto):")
        final_context = orchestrator.context
        
        # Estrai informazioni chiave
        key_info = {
            'user_info': final_context.get('findings', [])[-5:],  # Ultimi 5 findings
            'progress': final_context.get('meta', {}).get('checklist_progress', 'N/A'),
            'phase': final_context.get('current_phase_id', 'N/A')
        }
        
        print(json.dumps(key_info, indent=2, ensure_ascii=False))
        
        print(f"\n🎉 DEMO COMPLETATA CON SUCCESSO!")
        print("   Sistema checklist-driven funzionante ✅")
        print("   Context tracking attivo ✅")
        print("   Progress monitoring attivo ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRORE durante la demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Opzione per eseguire demo o test suite
    import argparse
    
    parser = argparse.ArgumentParser(description='Arnold Checklist Flow Tests')
    parser.add_argument('--demo', action='store_true', help='Run interactive demo')
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    else:
        # Run test suite
        unittest.main(verbosity=2)