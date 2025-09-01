"""
Arnold Fitness Platform - Conversation Engine
Main coordination class for personality-aware conversational system
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..personality.personality_mapper import PersonalityMapper
from ..personality.empathy_adapter import EmpathyAdapter
from ..personality.style_analyzer import StyleAnalyzer
from ..prompting.prompt_personalizer import PromptPersonalizer
from ..prompting.question_generator import QuestionGenerator
from ..prompting.tone_adjuster import ToneAdjuster
from ..flow.flow_manager import FlowManager
from ..flow.question_selector import QuestionSelector
from .context_bridge import ContextBridge


class ConversationEngine:
    """
    Main coordination class for Arnold's conversational system.
    
    Integrates personality analysis, adaptive prompting, and flow management
    to create natural, personalized fitness coaching conversations.
    """
    
    def __init__(self, logger=None):
        """Initialize conversation engine with all subsystems"""
        self.logger = logger
        
        # Initialize personality system
        self.personality_mapper = PersonalityMapper()
        self.empathy_adapter = EmpathyAdapter()
        self.style_analyzer = StyleAnalyzer()
        
        # Initialize prompting system
        self.prompt_personalizer = PromptPersonalizer()
        self.question_generator = QuestionGenerator()
        self.tone_adjuster = ToneAdjuster()
        
        # Initialize flow management
        self.flow_manager = FlowManager()
        self.question_selector = QuestionSelector()
        self.context_bridge = ContextBridge()
        
        # Engine state
        self.current_personality_profile = None
        self.conversation_state = {}
        
        if self.logger:
            self.logger.info("ConversationEngine initialized with all subsystems")
    
    def analyze_user_personality(self, user_input: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Analyze user personality from input and conversation history
        
        Args:
            user_input: Latest user input
            conversation_history: Previous conversation messages
            
        Returns:
            Dict containing personality analysis
        """
        try:
            # Analyze personality traits
            personality_profile = self.personality_mapper.analyze_personality(
                user_input, conversation_history or []
            )
            
            # Analyze communication style
            style_analysis = self.style_analyzer.analyze_writing_style(user_input)
            
            # Update current profile
            self.current_personality_profile = {
                'personality': personality_profile,
                'style': style_analysis,
                'updated_at': datetime.now().isoformat()
            }
            
            if self.logger:
                self.logger.debug(f"User personality analyzed: {personality_profile.get('primary_type', 'unknown')}")
            
            return self.current_personality_profile
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Personality analysis error: {e}")
            return {}
    
    def generate_personalized_response(self, 
                                     user_input: str, 
                                     context: Dict,
                                     response_type: str = "guidance") -> Dict:
        """
        Generate personalized response based on user personality and context
        
        Args:
            user_input: User's input message
            context: Current conversation context
            response_type: Type of response (guidance, question, encouragement)
            
        Returns:
            Dict containing personalized response
        """
        try:
            # Ensure we have personality profile
            if not self.current_personality_profile:
                self.analyze_user_personality(user_input, context.get('conversation_history', []))
            
            # Bridge context for conversational use
            conversation_context = self.context_bridge.bridge_checklist_to_conversation(context)
            
            # Update conversation state
            self.conversation_state = self.flow_manager.update_conversation_state(
                user_input, conversation_context
            )
            
            # Generate base content based on type
            if response_type == "question":
                base_response = self._generate_question(conversation_context)
            elif response_type == "encouragement":
                base_response = self._generate_encouragement(conversation_context)
            else:
                base_response = self._generate_guidance(user_input, conversation_context)
            
            # Personalize the response
            personalized_prompt = self.prompt_personalizer.personalize_prompt(
                base_response,
                self.current_personality_profile.get('personality', {}),
                conversation_context
            )
            
            # Adjust tone based on personality
            final_response = self.tone_adjuster.adjust_tone(
                personalized_prompt,
                self.current_personality_profile.get('personality', {}),
                self.conversation_state
            )
            
            # Apply empathy adaptations
            empathetic_response = self.empathy_adapter.adapt_empathy_level(
                final_response,
                self.current_personality_profile.get('personality', {}),
                conversation_context
            )
            
            return {
                'success': True,
                'response': empathetic_response,
                'personality_profile': self.current_personality_profile,
                'conversation_state': self.conversation_state,
                'response_metadata': {
                    'type': response_type,
                    'personalized': True,
                    'empathy_adapted': True,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Response generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_response': "I understand you're working on your fitness goals. Let me help you with that."
            }
    
    def _generate_question(self, context: Dict) -> str:
        """Generate contextual question"""
        try:
            questions = self.question_generator.generate_contextual_questions(
                context.get('current_phase', 'assessment'),
                context.get('user_data', {}),
                self.current_personality_profile.get('personality', {})
            )
            
            selected_question = self.question_selector.select_best_question(
                questions, context, self.conversation_state
            )
            
            return selected_question.get('text', 'What would you like to work on today?')
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Question generation error: {e}")
            return "What would you like to work on today?"
    
    def _generate_guidance(self, user_input: str, context: Dict) -> str:
        """Generate contextual guidance"""
        try:
            # This would typically integrate with the RAG system
            # For now, return contextual guidance based on current phase
            current_phase = context.get('current_phase', 'general')
            
            guidance_templates = {
                'assessment': f"I understand you mentioned: '{user_input}'. Let's explore this further to create your personalized fitness plan.",
                'planning': f"Based on what you've shared about '{user_input}', here's what I recommend for your fitness journey.",
                'implementation': f"Great progress! Regarding '{user_input}', let's focus on the next steps in your program.",
                'monitoring': f"I see you've mentioned '{user_input}'. Let's evaluate how this fits with your current progress."
            }
            
            return guidance_templates.get(current_phase, f"Thank you for sharing about '{user_input}'. Let me help you with your fitness goals.")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Guidance generation error: {e}")
            return "Let me help you with your fitness goals."
    
    def _generate_encouragement(self, context: Dict) -> str:
        """Generate encouraging message"""
        encouragements = [
            "You're making great progress on your fitness journey!",
            "Every step forward is a victory worth celebrating!",
            "Your dedication to your health is truly inspiring!",
            "Keep up the excellent work - you're stronger than you know!"
        ]
        
        import random
        return random.choice(encouragements)
    
    def get_conversation_insights(self) -> Dict:
        """Get insights about the current conversation state"""
        return {
            'personality_profile': self.current_personality_profile,
            'conversation_state': self.conversation_state,
            'engine_status': 'active',
            'subsystems': {
                'personality_mapper': 'initialized',
                'prompt_personalizer': 'initialized',
                'flow_manager': 'initialized',
                'context_bridge': 'initialized'
            }
        }
    
    def reset_conversation(self):
        """Reset conversation state for new session"""
        self.current_personality_profile = None
        self.conversation_state = {}
        
        if self.logger:
            self.logger.info("Conversation engine reset for new session")