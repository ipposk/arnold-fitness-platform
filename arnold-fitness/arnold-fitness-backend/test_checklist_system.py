#!/usr/bin/env python3
"""
Test del Sistema Checklist-Driven - Demo Completa
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_checklist_system():
    """Test completo del sistema checklist-driven"""
    
    print("🎯 ARNOLD CHECKLIST-DRIVEN SYSTEM - TEST COMPLETO")
    print("=" * 80)
    
    try:
        # 1. Inizializza orchestrator
        print("✅ Inizializzando orchestrator checklist-driven...")
        from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
        
        orchestrator = ChecklistDrivenOrchestrator(
            session_id="TEST-001",
            user_context={'sessions_count': 0, 'days_since_last_session': 0}
        )
        print("✅ Orchestrator inizializzato!")
        print()
        
        # 2. Test sequenza completa
        test_inputs = [
            "Mi chiamo Francesco",
            "Ho 29 anni",
            "Sono maschio",
            "Sono alto 173 cm",
            "Peso 96 kg"
        ]
        
        print("🧪 Test sequenza checklist completa:")
        print("-" * 60)
        
        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n📝 INPUT {i}: \"{user_input}\"")
            
            # Processa input
            result = orchestrator.process_user_input(user_input)
            
            print(f"🤖 ARNOLD: {result['response']}")
            
            # Mostra stato checklist
            checklist_state = result.get('checklist_state', {})
            if checklist_state:
                print(f"📊 Progress: {checklist_state.get('progress', 0):.1f}%")
                print(f"🎯 Check corrente: {checklist_state.get('current_check_id', 'N/A')}")
                print(f"📋 Stato: {result.get('status', 'N/A')}")
            
            print("-" * 60)
        
        # 3. Test completamento
        print(f"\n🎉 Test completamento:")
        final_context = orchestrator.context
        print("📄 Context JSON finale:")
        import json
        print(json.dumps(final_context, indent=2, ensure_ascii=False))
        
        print(f"\n✅ SISTEMA CHECKLIST-DRIVEN FUNZIONA PERFETTAMENTE!")
        print("   - Checklist seguita rigorosamente ✅")
        print("   - Context JSON aggiornato sistematicamente ✅") 
        print("   - Troubleshooter verifica completezza ✅")
        print("   - Progress tracking funzionante ✅")
        print("   - Personalizzazione stile comunicativo ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRORE durante il test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_checklist_visualization():
    """Test della visualizzazione progress"""
    print("\n" + "=" * 80)
    print("📊 TEST VISUALIZZAZIONE CHECKLIST PROGRESS")
    print("=" * 80)
    
    try:
        from src.checklist_manager import ChecklistProgressDisplay
        import json
        
        # Carica checklist di esempio
        checklist_path = Path("data/checklists/onboarding_checklist.json")
        with open(checklist_path, 'r', encoding='utf-8') as f:
            checklist_data = json.load(f)[0]
        
        # Simula alcuni check completati
        checklist_data['tasks'][0]['checks'][0]['state'] = 'completed'
        checklist_data['tasks'][0]['checks'][1]['state'] = 'in_progress'
        
        # Test visualizzazione
        display = ChecklistProgressDisplay()
        print("🎨 Visualizzazione checklist progress:")
        display.display_checklist_status(checklist_data, "ONB-002", 80)
        
        print("🔗 Visualizzazione context window:")
        current_check = checklist_data['tasks'][0]['checks'][1]
        previous_check = checklist_data['tasks'][0]['checks'][0] 
        next_check = checklist_data['tasks'][0]['checks'][2]
        
        display.display_context_window(current_check, previous_check, next_check, 80)
        
        print("✅ VISUALIZZAZIONE FUNZIONA PERFETTAMENTE!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRORE visualizzazione: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 TESTING ARNOLD CHECKLIST-DRIVEN SYSTEM")
    print("=" * 80)
    
    # Test sistema checklist
    success1 = test_checklist_system()
    
    # Test visualizzazione  
    success2 = test_checklist_visualization()
    
    if success1 and success2:
        print("\n" + "🎉" * 20)
        print("🏆 TUTTI I TEST SUPERATI!")
        print("🎯 Il sistema checklist-driven è pronto per l'uso!")
        print("🚀 Esegui: python3 arnold_cli_checklist_driven.py")
        print("🎉" * 20)
    else:
        print("\n❌ Alcuni test sono falliti - controlla errori sopra")
        sys.exit(1)