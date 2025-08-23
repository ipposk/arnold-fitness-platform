#!/usr/bin/env python3
"""Debug Process Input Step by Step"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_process_input():
    print("🔍 DEBUG PROCESS INPUT STEP BY STEP")
    print("=" * 60)
    
    try:
        from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
        
        orchestrator = ChecklistDrivenOrchestrator(
            session_id="DEBUG-001",
            user_context={'sessions_count': 0, 'days_since_last_session': 0}
        )
        
        print(f"✅ Orchestrator inizializzato")
        
        user_input = "Mi chiamo Francesco"
        print(f"📝 Processing input: '{user_input}'")
        
        try:
            # STEP 1: Analizza personalità
            print("\n🧠 STEP 1: Analizza personalità...")
            personality_profile = orchestrator._analyze_user_personality(user_input)
            print(f"✅ Personality: {personality_profile}")
            
            # STEP 2: Checklist (già caricata)
            print(f"\n📋 STEP 2: Checklist già caricata: {orchestrator.current_checklist is not None}")
            print(f"   Current check: {orchestrator.current_check['check_id'] if orchestrator.current_check else 'None'}")
            
            # STEP 3: Find current check
            print(f"\n🎯 STEP 3: Find current check...")
            current_check = orchestrator._find_current_check()
            print(f"✅ Current check found: {current_check['check_id'] if current_check else 'None'}")
            
            # STEP 4: Check completion
            print(f"\n🔍 STEP 4: Check completion with troubleshooter...")
            completion_result = orchestrator._check_completion_with_troubleshooter(user_input)
            print(f"✅ Completion result: {completion_result}")
            
            # STEP 5: Generate response
            print(f"\n💬 STEP 5: Generate response...")
            if completion_result['is_complete']:
                print("   → Check completato, advancing...")
                orchestrator._mark_check_completed(current_check['check_id'], completion_result['extracted_data'])
                orchestrator._advance_to_next_check()
                response = orchestrator._generate_advancement_response()
            else:
                print("   → Check incompleto, richiedendo completamento...")
                response = orchestrator._generate_completion_request_response(completion_result['missing_data'])
            
            print(f"✅ Response generated: {response}")
            
        except Exception as e:
            print(f"❌ ERRORE in process_user_input: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ ERRORE CRITICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_process_input()