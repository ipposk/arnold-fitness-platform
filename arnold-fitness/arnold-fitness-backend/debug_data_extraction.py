#!/usr/bin/env python3
"""Debug Data Extraction"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_data_extraction():
    print("🔍 DEBUG DATA EXTRACTION")
    print("=" * 50)
    
    try:
        from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
        
        orchestrator = ChecklistDrivenOrchestrator(
            session_id="DEBUG-001",
            user_context={'sessions_count': 0, 'days_since_last_session': 0}
        )
        
        print(f"✅ Orchestrator inizializzato")
        print(f"📋 Current check: {orchestrator.current_check['check_id'] if orchestrator.current_check else 'None'}")
        
        if orchestrator.current_check:
            required_data = orchestrator.current_check.get('required_data', [])
            print(f"🔢 Required data: {required_data}")
            
            # Test estrazione dati
            test_input = "Mi chiamo Francesco"
            print(f"📝 Test input: '{test_input}'")
            
            extracted = orchestrator._extract_data_from_input(test_input, required_data)
            print(f"📄 Extracted data: {extracted}")
            
            missing = [field for field in required_data if field not in extracted]
            print(f"❌ Missing data: {missing}")
            
            # Test troubleshooter
            completion_result = orchestrator._check_completion_with_troubleshooter(test_input)
            print(f"🔍 Completion result: {completion_result}")
            
            # Test generazione risposta
            if not completion_result['is_complete']:
                question = orchestrator._generate_check_question(orchestrator.current_check, completion_result['missing_data'])
                print(f"❓ Generated question: '{question}'")
                
                personalized = orchestrator._personalize_question_style(question, {'primary_type': 'practical'})
                print(f"🎨 Personalized: '{personalized}'")
        
    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_extraction()