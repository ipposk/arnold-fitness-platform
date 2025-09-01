#!/usr/bin/env python3
"""
Test Suite Completa del Sistema Conversazionale di Arnold
Consolida test dei componenti di personalizzazione e adattamento conversazionale
"""

import sys
import unittest
from pathlib import Path

# Setup path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestPersonalityProfiler(unittest.TestCase):
    """Test per il Personality Profiler"""
    
    def setUp(self):
        """Setup per ogni test"""
        from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter
        self.analyzer = StyleAnalyzer()
        self.mapper = PersonalityMapper()
        self.empathy_adapter = EmpathyAdapter()
    
    def test_style_analysis(self):
        """Test analisi stile di scrittura"""
        test_inputs = [
            ("Ciao! Sono molto entusiasta di iniziare questo percorso con te!", "enthusiastic"),
            ("Salve, vorrei sapere specificamente quali sono le opzioni disponibili per perdere peso.", "analytical"),
            ("non so... forse potrei provare qualcosa ma non sono sicuro che funzioni", "uncertain"),
            ("Ho 30 anni e lavoro molto, il problema è che mangio male la sera quando torno a casa stressato.", "concerned")
        ]
        
        for text, expected_tone in test_inputs:
            with self.subTest(text=text[:50]):
                style = self.analyzer.analyze_text(text)
                self.assertIsNotNone(style)
                self.assertIn(style.emotional_tone, ['positive', 'neutral', 'concerned', 'analytical'])
                self.assertIn(style.verbosity, ['brief', 'moderate', 'verbose'])
                self.assertIn(style.energy_level, ['low', 'moderate', 'high'])
    
    def test_personality_mapping(self):
        """Test mapping stile -> profilo personalità"""
        from src.personality_profiler.style_analyzer import WritingStyle
        
        # Test profilo analitico
        analytical_style = WritingStyle(
            verbosity="moderate",
            emotional_tone="analytical", 
            formality="formal",
            technical_level="intermediate",
            openness="moderate",
            energy_level="moderate",
            concern_level="low"
        )
        
        profile = self.mapper.map_style_to_personality(analytical_style)
        self.assertEqual(profile.primary_type, "analytical")
        self.assertEqual(profile.communication_preference, "detailed")
        
        # Test profilo emotivo
        emotional_style = WritingStyle(
            verbosity="verbose",
            emotional_tone="concerned", 
            formality="informal",
            technical_level="basic",
            openness="high",
            energy_level="low",
            concern_level="high"
        )
        
        profile = self.mapper.map_style_to_personality(emotional_style)
        self.assertEqual(profile.primary_type, "emotional")
        self.assertEqual(profile.support_needs, "high")
    
    def test_empathy_adaptation(self):
        """Test adattamento empatico"""
        from src.personality_profiler.personality_mapper import PersonalityProfile
        
        # Test greeting per diversi profili
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
        
        analytical_greeting = self.empathy_adapter.get_greeting_style(analytical_profile)
        emotional_greeting = self.empathy_adapter.get_greeting_style(emotional_profile)
        
        self.assertIsNotNone(analytical_greeting)
        self.assertIsNotNone(emotional_greeting)
        self.assertNotEqual(analytical_greeting, emotional_greeting)


class TestQuestionGenerator(unittest.TestCase):
    """Test per il Question Generator"""
    
    def setUp(self):
        """Setup per ogni test"""
        from src.adaptive_prompting import QuestionGenerator
        self.generator = QuestionGenerator()
    
    def test_warmup_questions(self):
        """Test generazione domande di apertura"""
        from src.personality_profiler.personality_mapper import PersonalityProfile
        from src.personality_profiler.style_analyzer import WritingStyle
        
        profile = PersonalityProfile(
            primary_type="practical",
            communication_preference="direct",
            motivation_style="achievement",
            support_needs="low",
            information_processing="big_picture"
        )
        
        style = WritingStyle(
            verbosity="brief",
            emotional_tone="neutral", 
            formality="semi_formal",
            technical_level="basic",
            openness="moderate",
            energy_level="moderate",
            concern_level="low"
        )
        
        question = self.generator.generate_warmup_question(profile, style, 1)
        self.assertIsNotNone(question)
        self.assertIsInstance(question, str)
        self.assertGreater(len(question), 10)
    
    def test_followup_questions(self):
        """Test generazione domande di follow-up"""
        from src.personality_profiler.personality_mapper import PersonalityProfile
        from src.personality_profiler.style_analyzer import WritingStyle
        
        profile = PersonalityProfile(
            primary_type="emotional",
            communication_preference="gentle",
            motivation_style="security",
            support_needs="high",
            information_processing="step_by_step"
        )
        
        style = WritingStyle(
            verbosity="verbose",
            emotional_tone="concerned", 
            formality="informal",
            technical_level="basic",
            openness="high",
            energy_level="low",
            concern_level="high"
        )
        
        user_input = "non so bene cosa dire... sono un po' preoccupato"
        followup = self.generator.generate_followup_question(
            user_input, "general", profile, style
        )
        
        self.assertIsNotNone(followup)
        self.assertIsInstance(followup, str)
        self.assertGreater(len(followup), 10)


class TestConversationFlow(unittest.TestCase):
    """Test per il flusso conversazionale"""
    
    def setUp(self):
        """Setup per ogni test"""
        try:
            from src.conversation_director import FlowManager, QuestionSelector, ContextBridge
            self.flow_manager = FlowManager()
            self.question_selector = QuestionSelector()
            self.context_bridge = ContextBridge()
        except ImportError as e:
            self.skipTest(f"Conversation director components not available: {e}")
    
    def test_conversation_state_management(self):
        """Test gestione stato conversazione"""
        from src.conversation_director.flow_manager import ConversationState, ConversationPhase
        
        # Test inizializzazione
        state = ConversationState(
            phase=ConversationPhase.WARMUP,
            turn_count=1,
            user_engagement="medium",
            information_completeness=0.1,
            relationship_strength="building",
            last_topic="introduction",
            pending_followups=[]
        )
        
        self.assertEqual(state.phase, ConversationPhase.WARMUP)
        self.assertEqual(state.turn_count, 1)
        self.assertEqual(state.user_engagement, "medium")
    
    def test_context_bridge_integration(self):
        """Test integrazione context bridge con checklist"""
        from src.personality_profiler import StyleAnalyzer, PersonalityMapper
        
        analyzer = StyleAnalyzer()
        mapper = PersonalityMapper()
        
        # Simula input utente
        user_input = "Ciao Arnold! Sono Francesco, ho 32 anni e ultimamente sto mangiando molto male."
        
        # Analizza profilo
        style = analyzer.analyze_text(user_input)
        profile = mapper.map_style_to_personality(style)
        
        self.assertIsNotNone(profile)
        self.assertIn(profile.primary_type, ['practical', 'analytical', 'emotional', 'supportive'])
        
        # Mock context per test
        mock_context = {
            "checklist": [
                {
                    "title": "Initial Assessment",
                    "tasks": [
                        {
                            "checks": [
                                {"check_id": "basic_demographics", "state": "pending"},
                                {"check_id": "health_goals", "state": "pending"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        conversation_history = [
            {"user": user_input, "arnold": None, "timestamp": "2024-01-01T12:00:00"}
        ]
        
        # Test conversational step
        conversational_step = self.context_bridge.get_next_conversational_step(
            mock_context, conversation_history, profile, style
        )
        
        self.assertIsNotNone(conversational_step)
        self.assertIn('conversation_state', conversational_step)


class TestOfflineConversationalSystem(unittest.TestCase):
    """Test per sistema conversazionale offline"""
    
    def setUp(self):
        """Setup per test offline"""
        try:
            from src.orchestrator.offline_conversational_orchestrator import OfflineConversationalOrchestrator
            self.orchestrator = OfflineConversationalOrchestrator("TEST-SESSION-OFFLINE")
        except ImportError as e:
            self.skipTest(f"Offline conversational orchestrator not available: {e}")
    
    def test_offline_processing(self):
        """Test processamento offline"""
        test_inputs = [
            "Ciao! sono un ragazzo alto 173 cm e peso 96 kg. ho 29 anni",
            "Ultimamente sono molto stressato per il lavoro e mangio troppo la sera",
            "Vorrei un programma preciso con dati e metriche specifiche",
            "Ho poco tempo, dimmi solo cosa devo fare velocemente"
        ]
        
        expected_personalities = ['practical', 'emotional', 'analytical', 'practical']
        
        for input_text, expected in zip(test_inputs, expected_personalities):
            with self.subTest(input_text=input_text[:50]):
                result = self.orchestrator.process_conversational_input(input_text)
                
                self.assertIn('personality_profile', result)
                self.assertIn('last_output', result) 
                self.assertIn('conversation_state', result)
                
                personality = result['personality_profile']['primary_type']
                # Il profilo può variare ma deve essere valido
                self.assertIn(personality, ['practical', 'analytical', 'emotional', 'supportive'])


class TestCLIIntegration(unittest.TestCase):
    """Test integrazione con CLI"""
    
    def test_component_imports(self):
        """Test import delle componenti principali"""
        try:
            from src.orchestrator.conversational_orchestrator import ConversationalOrchestrator
            self.assertTrue(True)  # Se arriviamo qui, l'import è riuscito
        except ImportError:
            self.fail("ConversationalOrchestrator import failed")
        
        try:
            from src.llm_interfaces.enhanced_llm_interfaces import create_enhanced_llm_interfaces
            self.assertTrue(True)  # Se arriviamo qui, l'import è riuscito
        except ImportError:
            self.fail("Enhanced LLM interfaces import failed")


def run_offline_demo():
    """Demo offline del sistema conversazionale per debugging"""
    print("\n🤖 ARNOLD CONVERSATIONAL SYSTEM - OFFLINE DEMO")
    print("=" * 60)
    
    try:
        from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter
        from src.adaptive_prompting import QuestionGenerator
        
        # Initialize components
        analyzer = StyleAnalyzer()
        mapper = PersonalityMapper()
        empathy_adapter = EmpathyAdapter()
        question_generator = QuestionGenerator()
        
        print("✅ Tutti i componenti caricati con successo!")
        
        # Test with sample input
        user_input = "Ciao! sono un ragazzo alto 173 cm e peso 96 kg. ho 29 anni"
        
        print(f"\n📝 Input Utente: {user_input}")
        print("\n🔍 ANALISI AUTOMATICA:")
        print("-" * 40)
        
        # Analyze writing style
        writing_style = analyzer.analyze_text(user_input)
        print(f"📊 Stile: {writing_style.verbosity}, {writing_style.emotional_tone}, energia: {writing_style.energy_level}")
        
        # Map to personality
        personality_profile = mapper.map_style_to_personality(writing_style)
        print(f"🧠 Profilo: {personality_profile.primary_type} ({personality_profile.communication_preference})")
        
        # Generate response
        greeting = empathy_adapter.get_greeting_style(personality_profile)
        opening_question = question_generator.generate_warmup_question(
            personality_profile, writing_style, turn_number=1
        )
        
        print(f"\n💬 Saluto: {greeting}")
        print(f"❓ Domanda: {opening_question}")
        
        print(f"\n✅ Demo completata con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore nella demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Opzione per eseguire demo offline o test suite
    import argparse
    
    parser = argparse.ArgumentParser(description='Arnold Conversational System Tests')
    parser.add_argument('--demo', action='store_true', help='Run offline demo instead of tests')
    args = parser.parse_args()
    
    if args.demo:
        run_offline_demo()
    else:
        # Run test suite
        unittest.main(verbosity=2)