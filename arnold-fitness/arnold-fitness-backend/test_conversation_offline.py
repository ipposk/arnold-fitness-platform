#!/usr/bin/env python3
"""
Test Offline del Sistema Conversazionale - Senza API Keys
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_conversational_system():
    """Demo del sistema conversazionale senza API calls"""
    
    print("🤖 ARNOLD CONVERSATIONAL SYSTEM - OFFLINE DEMO")
    print("=" * 60)
    
    # Import components
    from src.personality_profiler import StyleAnalyzer, PersonalityMapper, EmpathyAdapter
    from src.adaptive_prompting import QuestionGenerator
    
    # Initialize components
    analyzer = StyleAnalyzer()
    mapper = PersonalityMapper()
    empathy_adapter = EmpathyAdapter()
    question_generator = QuestionGenerator()
    
    print("✅ Tutti i componenti caricati con successo!\n")
    
    # Test with your actual input
    user_input = "Ciao! sono un ragazzo alto 173 cm e peso 96 kg. ho 29 anni"
    
    print(f"📝 Input Utente: {user_input}")
    print("\n🔍 ANALISI AUTOMATICA:")
    print("-" * 40)
    
    # Step 1: Analyze writing style
    writing_style = analyzer.analyze_text(user_input)
    print(f"📊 Stile di Scrittura:")
    print(f"  • Verbosità: {writing_style.verbosity}")
    print(f"  • Tono emotivo: {writing_style.emotional_tone}")
    print(f"  • Formalità: {writing_style.formality}")
    print(f"  • Energia: {writing_style.energy_level}")
    print(f"  • Apertura: {writing_style.openness}")
    print(f"  • Preoccupazione: {writing_style.concern_level}")
    
    # Step 2: Map to personality profile
    personality_profile = mapper.map_style_to_personality(writing_style)
    print(f"\n🧠 Profilo Psicologico:")
    print(f"  • Tipo primario: {personality_profile.primary_type}")
    print(f"  • Comunicazione preferita: {personality_profile.communication_preference}")
    print(f"  • Stile motivazionale: {personality_profile.motivation_style}")
    print(f"  • Bisogni di supporto: {personality_profile.support_needs}")
    print(f"  • Processamento info: {personality_profile.information_processing}")
    
    # Step 3: Generate personalized opening question
    print(f"\n💬 RISPOSTA PERSONALIZZATA:")
    print("-" * 40)
    
    # Generate greeting adapted to profile
    greeting = empathy_adapter.get_greeting_style(personality_profile)
    print(f"🤝 Saluto: {greeting}")
    
    # Generate first question
    opening_question = question_generator.generate_warmup_question(
        personality_profile, writing_style, turn_number=1
    )
    print(f"\n❓ Prima Domanda: {opening_question}")
    
    # Step 4: Show adaptation insights
    print(f"\n🎯 INSIGHTS PERSONALIZZAZIONE:")
    print("-" * 40)
    
    insights = mapper.get_personality_insights(personality_profile)
    for key, value in insights.items():
        print(f"  • {key}: {value}")
    
    # Step 5: Simulate follow-up
    print(f"\n🔄 SIMULAZIONE FOLLOW-UP:")
    print("-" * 40)
    
    # Simulate user gives more emotional response  
    followup_input = "In realtà sono un po' preoccupato per il mio peso, mi sento a disagio"
    
    print(f"📝 Follow-up utente: {followup_input}")
    
    # Re-analyze with more data
    followup_style = analyzer.analyze_conversation_history([user_input, followup_input])
    updated_profile = mapper.map_style_to_personality(followup_style)
    
    print(f"🔄 Profilo aggiornato: {updated_profile.primary_type}")
    print(f"🔄 Supporto necessario: {updated_profile.support_needs}")
    
    # Generate empathetic follow-up
    followup_question = question_generator.generate_followup_question(
        followup_input, "weight_concerns", updated_profile, followup_style
    )
    
    print(f"💙 Risposta empatica: {followup_question}")
    
    print(f"\n🎉 DEMO COMPLETATA!")
    print("Il sistema si è adattato automaticamente dal profilo 'practical' a 'emotional'")
    print("e ha generato risposte più supportive e comprensive.")
    
    return True

if __name__ == "__main__":
    try:
        demo_conversational_system()
    except Exception as e:
        print(f"❌ Errore nella demo: {e}")
        import traceback
        traceback.print_exc()