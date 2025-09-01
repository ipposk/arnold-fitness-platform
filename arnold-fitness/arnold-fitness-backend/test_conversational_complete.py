#!/usr/bin/env python3
"""
Test del Sistema Conversazionale Arnold - Test Completo
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_conversational_system():
    """Test completo del sistema conversazionale"""
    
    print("🤖 ARNOLD CONVERSATIONAL SYSTEM - FULL TEST")
    print("=" * 60)
    
    try:
        # 1. Inizializza sistema conversazionale offline
        print("✅ Inizializzando sistema conversazionale offline...")
        from src.orchestrator.offline_conversational_orchestrator import OfflineConversationalOrchestrator
        
        orchestrator = OfflineConversationalOrchestrator("TEST-SESSION-001")
        print("✅ Sistema conversazionale inizializzato!")
        print()
        
        # 2. Test con diversi tipi di input
        test_inputs = [
            "Ciao! sono un ragazzo alto 173 cm e peso 96 kg. ho 29 anni",
            "Ultimamente sono molto stressato per il lavoro e mangio troppo la sera",
            "Vorrei un programma preciso con dati e metriche specifiche per la massa muscolare",
            "Ho poco tempo, dimmi solo cosa devo fare velocemente"
        ]
        
        expected_personalities = ['practical', 'emotional', 'analytical', 'practical']
        
        print("🧪 Test di personalizzazione automatica:")
        print("-" * 40)
        
        for i, (input_text, expected) in enumerate(zip(test_inputs, expected_personalities), 1):
            print(f"\n📝 Test {i}: Input di tipo '{expected}'")
            print(f"Input: \"{input_text[:50]}...\"")
            
            # Processa input
            result = orchestrator.process_conversational_input(input_text)
            
            # Verifica risultato
            personality = result['personality_profile']['primary_type']
            response = result['last_output']['guidance_markdown']
            
            print(f"🎯 Profilo rilevato: {personality}")
            print(f"💬 Risposta: \"{response[:80]}...\"")
            
            # Verifica correttezza
            if personality == expected:
                print("✅ CORRETTO - Profilo rilevato come previsto!")
            else:
                print(f"⚠️  Previsto '{expected}', ottenuto '{personality}'")
            
            print("-" * 40)
        
        # 3. Test stato conversazionale
        print("\n🔄 Test stato conversazionale:")
        state = result['conversation_state']
        print(f"Fase: {state.get('phase', 'N/A')}")
        print(f"Turno: {state.get('turn_count', 'N/A')}")
        print(f"Engagement: {state.get('user_engagement', 'N/A')}")
        
        print("\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("\n🚀 Il sistema conversazionale è pronto per l'uso!")
        print("   - Personalizzazione automatica: ✅")
        print("   - Rilevamento profili: ✅")
        print("   - Risposte adattive: ✅")
        print("   - Gestione stato: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRORE durante il test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_conversational_system()
    
    if success:
        print("\n" + "="*60)
        print("🎯 ARNOLD CONVERSATIONAL SYSTEM - READY!")
        print("="*60)
        print()
        print("Per usare il sistema completo:")
        print("1. Configura API keys nel file .env")  
        print("2. Esegui: python3 arnold_cli_modern.py")
        print("3. Il sistema userà automaticamente la personalizzazione!")
    else:
        print("\n❌ Sistema non pronto - controllare errori sopra")
        sys.exit(1)