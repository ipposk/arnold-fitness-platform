#!/usr/bin/env python3
"""Debug Orchestrator Checklist-Driven"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_orchestrator():
    print("🔍 DEBUG ORCHESTRATOR CHECKLIST-DRIVEN")
    print("=" * 60)
    
    try:
        from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
        
        print("✅ Import orchestrator OK")
        
        # Test inizializzazione
        orchestrator = ChecklistDrivenOrchestrator(
            session_id="DEBUG-001",
            user_context={'sessions_count': 0, 'days_since_last_session': 0}
        )
        
        print("✅ Orchestrator creato OK")
        
        # Test determinazione checklist
        checklist_type = orchestrator._determine_checklist_type()
        print(f"📋 Tipo checklist determinato: {checklist_type}")
        
        # Test caricamento checklist
        try:
            checklist = orchestrator._load_checklist(checklist_type)
            print(f"✅ Checklist caricata: {checklist.get('title', 'N/A')}")
            print(f"📋 Phase ID: {checklist.get('phase_id', 'N/A')}")
            print(f"🔢 Tasks: {len(checklist.get('tasks', []))}")
        except Exception as e:
            print(f"❌ Errore caricamento checklist: {e}")
            import traceback
            traceback.print_exc()
        
        # Test find current check
        try:
            current_check = orchestrator._find_current_check()
            if current_check:
                print(f"✅ Check corrente trovato: {current_check['check_id']}")
            else:
                print("❌ Nessun check corrente trovato")
        except Exception as e:
            print(f"❌ Errore find current check: {e}")
            import traceback
            traceback.print_exc()
        
        # Test process input
        try:
            result = orchestrator.process_user_input("Mi chiamo Francesco")
            print(f"✅ Process input OK: {result.get('status', 'N/A')}")
            print(f"📝 Response: {result.get('response', 'N/A')[:50]}...")
        except Exception as e:
            print(f"❌ Errore process input: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ ERRORE CRITICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_orchestrator()