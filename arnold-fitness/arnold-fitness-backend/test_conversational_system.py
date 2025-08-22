#!/usr/bin/env python3
"""
Test Script per il Sistema Conversazionale di Arnold
"""

import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_personality_profiler():
    """Test del Personality Profiler"""
    
    print("\n=== TEST PERSONALITY PROFILER ===")
    
    try:
        from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter
        
        # Test analyzer
        analyzer = StyleAnalyzer()
        
        test_inputs = [
            "Ciao! Sono molto entusiasta di iniziare questo percorso con te!",
            "Salve, vorrei sapere specificamente quali sono le opzioni disponibili per perdere peso.",
            "non so... forse potrei provare qualcosa ma non sono sicuro che funzioni",
            "Ho 30 anni e lavoro molto, il problema è che mangio male la sera quando torno a casa stressato."
        ]
        
        for i, text in enumerate(test_inputs, 1):
            print(f"\nTest {i}: {text[:50]}...")
            
            style = analyzer.analyze_text(text)
            print(f"  Verbosità: {style.verbosity}")
            print(f"  Tono emotivo: {style.emotional_tone}")
            print(f"  Energia: {style.energy_level}")
            print(f"  Preoccupazione: {style.concern_level}")
            
            # Test mapper
            mapper = PersonalityMapper()
            profile = mapper.map_style_to_personality(style)
            print(f"  → Profilo primario: {profile.primary_type}")
            print(f"  → Comunicazione preferita: {profile.communication_preference}")
            
        print("\n✅ Personality Profiler: PASS")
        return True
        
    except Exception as e:
        print(f"\n❌ Personality Profiler: FAILED - {e}")
        return False

def test_question_generator():
    """Test del Question Generator"""
    
    print("\n=== TEST QUESTION GENERATOR ===")
    
    try:
        from src.adaptive_prompting import QuestionGenerator
        from src.personality_profiler.personality_mapper import PersonalityProfile
        from src.personality_profiler.style_analyzer import WritingStyle
        from src.conversation_director.flow_manager import ConversationState, ConversationPhase
        
        generator = QuestionGenerator()
        
        # Crea profili test
        analytical_profile = PersonalityProfile(
            primary_type="analytical",
            communication_preference="detailed",
            motivation_style="achievement",
            support_needs="low",
            information_processing="big_picture"
        )
        
        emotional_profile = PersonalityProfile(
            primary_type="emotional", 
            communication_preference="gentle",
            motivation_style="security",
            support_needs="high",
            information_processing="step_by_step"
        )
        
        writing_style = WritingStyle(
            verbosity="moderate",
            emotional_tone="neutral", 
            formality="semi_formal",
            technical_level="basic",
            openness="moderate",
            energy_level="moderate",
            concern_level="moderate"
        )
        
        conversation_state = ConversationState(
            phase=ConversationPhase.WARMUP,
            turn_count=1,
            user_engagement="medium",
            information_completeness=0.1,
            relationship_strength="building",
            last_topic="introduction",
            pending_followups=[]
        )
        
        # Test diverse domande
        print("\n--- Domande di apertura ---")
        
        analytical_q = generator.generate_warmup_question(analytical_profile, writing_style, 1)
        print(f"Analitico: {analytical_q}")
        
        emotional_q = generator.generate_warmup_question(emotional_profile, writing_style, 1)  
        print(f"Emotivo: {emotional_q}")
        
        # Test follow-up
        print("\n--- Follow-up ---")
        followup = generator.generate_followup_question(
            "non so bene cosa dire...", "general", emotional_profile, writing_style
        )
        print(f"Follow-up gentile: {followup}")
        
        print("\n✅ Question Generator: PASS")
        return True
        
    except Exception as e:
        print(f"\n❌ Question Generator: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_flow():
    """Test del flusso conversazionale completo"""
    
    print("\n=== TEST CONVERSATION FLOW ===")
    
    try:
        from src.conversation_director import FlowManager, QuestionSelector, ContextBridge
        from src.personality_profiler import StyleAnalyzer, PersonalityMapper
        
        # Simula una mini conversazione
        flow_manager = FlowManager()
        question_selector = QuestionSelector() 
        context_bridge = ContextBridge()
        analyzer = StyleAnalyzer()
        mapper = PersonalityMapper()
        
        # Simula input utente
        user_input = "Ciao Arnold! Sono Francesco, ho 32 anni e ultimamente sto mangiando molto male a causa dello stress lavorativo."
        
        # Analizza profilo
        style = analyzer.analyze_text(user_input)
        profile = mapper.map_style_to_personality(style)
        
        print(f"Profilo identificato: {profile.primary_type}")
        print(f"Stile: {style.emotional_tone}, {style.verbosity}, preoccupazione: {style.concern_level}")
        
        # Simula checklist context
        mock_context = {
            "checklist": [
                {
                    "title": "Initial Assessment",
                    "tasks": [
                        {
                            "checks": [
                                {"check_id": "basic_demographics", "state": "pending", "description": "Collect basic info"},
                                {"check_id": "health_goals", "state": "pending", "description": "Identify health goals"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        conversation_history = [{"user": user_input, "arnold": None, "timestamp": "2024-01-01T12:00:00"}]
        
        # Test conversational step
        conversational_step = context_bridge.get_next_conversational_step(
            mock_context, conversation_history, profile, style
        )
        
        print(f"Fase conversazione: {conversational_step.get('conversation_state').phase.value}")
        print(f"Prossima domanda disponibile: {'Sì' if conversational_step.get('next_question') else 'No'}")
        
        print("\n✅ Conversation Flow: PASS") 
        return True
        
    except Exception as e:
        print(f"\n❌ Conversation Flow: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_integration():
    """Test basic dell'integrazione CLI"""
    
    print("\n=== TEST CLI INTEGRATION ===")
    
    try:
        # Test import delle componenti principali
        from src.orchestrator.conversational_orchestrator import ConversationalOrchestrator
        print("✓ ConversationalOrchestrator import successful")
        
        from src.llm_interfaces.enhanced_llm_interfaces import create_enhanced_llm_interfaces
        print("✓ Enhanced LLM interfaces import successful")
        
        print("\n✅ CLI Integration: PASS")
        return True
        
    except Exception as e:
        print(f"\n❌ CLI Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Esegue tutti i test"""
    
    print("🚀 ARNOLD CONVERSATIONAL SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Personality Profiler", test_personality_profiler),
        ("Question Generator", test_question_generator), 
        ("Conversation Flow", test_conversation_flow),
        ("CLI Integration", test_cli_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Il sistema conversazionale è pronto!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Sistemare prima del deploy.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)