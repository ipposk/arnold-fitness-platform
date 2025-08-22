"""
Conversation Director Module

Gestisce il flusso conversazionale naturale integrando il sistema checklist
con un approccio personalizzato basato sul profilo dell'utente.
"""

from .question_selector import QuestionSelector
from .flow_manager import FlowManager, ConversationState, ConversationPhase
from .context_bridge import ContextBridge

__all__ = ['QuestionSelector', 'FlowManager', 'ConversationState', 'ConversationPhase', 'ContextBridge']