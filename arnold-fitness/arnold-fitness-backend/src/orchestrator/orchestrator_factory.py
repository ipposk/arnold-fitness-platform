"""
Arnold Fitness Platform - Orchestrator Factory
Factory pattern implementation for creating appropriate orchestrator instances
"""

from typing import Dict, Optional, Union
from enum import Enum

from src.logger.logger import Logger
from src.db_context_manager.db_manager import DbContextManager
from src.context_validator.context_validator import ContextValidator
from .base_orchestrator import BaseOrchestrator


class OrchestratorType(Enum):
    """Enumeration of available orchestrator types"""
    LEGACY = "legacy"
    CHECKLIST = "checklist"
    CONVERSATIONAL = "conversational"
    AUTO = "auto"  # Automatically select best orchestrator


class OrchestratorFactory:
    """
    Factory class for creating orchestrator instances using Strategy pattern
    
    This factory encapsulates the logic for selecting and instantiating the
    appropriate orchestrator based on session requirements, user preferences,
    or context analysis.
    """
    
    @staticmethod
    def create_orchestrator(
        orchestrator_type: Union[str, OrchestratorType],
        db_manager: DbContextManager,
        validator: ContextValidator,
        session_id: str = None,
        logger: Logger = None,
        context: Dict = None,
        **kwargs
    ) -> BaseOrchestrator:
        """
        Create and return appropriate orchestrator instance
        
        Args:
            orchestrator_type: Type of orchestrator to create
            db_manager: Database context manager
            validator: Context validator
            session_id: Optional session identifier
            logger: Optional logger instance
            context: Optional context for auto-selection
            **kwargs: Additional arguments for orchestrator initialization
            
        Returns:
            BaseOrchestrator instance
            
        Raises:
            ValueError: If orchestrator_type is invalid
            ImportError: If required orchestrator class cannot be imported
        """
        # Convert string to enum if needed
        if isinstance(orchestrator_type, str):
            try:
                orchestrator_type = OrchestratorType(orchestrator_type.lower())
            except ValueError:
                raise ValueError(f"Invalid orchestrator type: {orchestrator_type}")
        
        # Auto-select orchestrator if requested
        if orchestrator_type == OrchestratorType.AUTO:
            orchestrator_type = OrchestratorFactory._auto_select_orchestrator(
                context, session_id, logger
            )
        
        # Initialize logger if not provided
        if logger is None:
            logger = Logger()
        
        logger.info(f"Creating {orchestrator_type.value} orchestrator for session {session_id}")
        
        # Create orchestrator instance based on type
        if orchestrator_type == OrchestratorType.CHECKLIST:
            return OrchestratorFactory._create_checklist_orchestrator(
                db_manager, validator, session_id, logger, **kwargs
            )
        
        elif orchestrator_type == OrchestratorType.CONVERSATIONAL:
            return OrchestratorFactory._create_conversational_orchestrator(
                db_manager, validator, session_id, logger, **kwargs
            )
        
        elif orchestrator_type == OrchestratorType.LEGACY:
            return OrchestratorFactory._create_legacy_orchestrator(
                db_manager, validator, session_id, logger, **kwargs
            )
        
        else:
            raise ValueError(f"Unsupported orchestrator type: {orchestrator_type}")
    
    @staticmethod
    def _auto_select_orchestrator(
        context: Dict = None, 
        session_id: str = None, 
        logger: Logger = None
    ) -> OrchestratorType:
        """
        Automatically select the best orchestrator based on context analysis
        
        Args:
            context: Session context for analysis
            session_id: Session identifier
            logger: Logger instance
            
        Returns:
            OrchestratorType enum value
        """
        if logger:
            logger.debug("Auto-selecting orchestrator based on context analysis")
        
        # Default to checklist for new sessions
        if not context:
            return OrchestratorType.CHECKLIST
        
        # Analysis logic for orchestrator selection
        checklist_progress = context.get('checklist_progress', {})
        conversation_history = context.get('conversation_history', [])
        user_preferences = context.get('user_preferences', {})
        
        # If user has preference, respect it
        preferred_mode = user_preferences.get('interface_mode')
        if preferred_mode in [t.value for t in OrchestratorType if t != OrchestratorType.AUTO]:
            return OrchestratorType(preferred_mode)
        
        # If checklist is active and incomplete, use checklist orchestrator
        if checklist_progress:
            current_checklist = checklist_progress.get('current_checklist')
            if current_checklist and not checklist_progress.get('completed', False):
                return OrchestratorType.CHECKLIST
        
        # If there's extensive conversation history, use conversational orchestrator
        if len(conversation_history) > 10:
            return OrchestratorType.CONVERSATIONAL
        
        # Default to checklist for structured coaching
        return OrchestratorType.CHECKLIST
    
    @staticmethod
    def _create_checklist_orchestrator(
        db_manager: DbContextManager,
        validator: ContextValidator,
        session_id: str,
        logger: Logger,
        **kwargs
    ) -> BaseOrchestrator:
        """Create checklist-driven orchestrator instance"""
        try:
            from .checklist_driven_orchestrator import ChecklistDrivenOrchestrator
            return ChecklistDrivenOrchestrator(
                db_manager=db_manager,
                validator=validator,
                session_id=session_id,
                logger=logger,
                **kwargs
            )
        except ImportError as e:
            logger.error(f"Failed to import ChecklistDrivenOrchestrator: {e}")
            raise ImportError(f"ChecklistDrivenOrchestrator not available: {e}")
    
    @staticmethod
    def _create_conversational_orchestrator(
        db_manager: DbContextManager,
        validator: ContextValidator,
        session_id: str,
        logger: Logger,
        **kwargs
    ) -> BaseOrchestrator:
        """Create conversational orchestrator instance"""
        try:
            from .conversational_orchestrator import ConversationalOrchestrator
            return ConversationalOrchestrator(
                db_manager=db_manager,
                validator=validator,
                session_id=session_id,
                logger=logger,
                **kwargs
            )
        except ImportError as e:
            logger.error(f"Failed to import ConversationalOrchestrator: {e}")
            raise ImportError(f"ConversationalOrchestrator not available: {e}")
    
    @staticmethod
    def _create_legacy_orchestrator(
        db_manager: DbContextManager,
        validator: ContextValidator,
        session_id: str,
        logger: Logger,
        **kwargs
    ) -> BaseOrchestrator:
        """Create legacy orchestrator instance with adapter pattern"""
        try:
            from .legacy_orchestrator_adapter import LegacyOrchestratorAdapter
            return LegacyOrchestratorAdapter(
                db_manager=db_manager,
                validator=validator,
                session_id=session_id,
                logger=logger,
                **kwargs
            )
        except ImportError as e:
            logger.error(f"Failed to import LegacyOrchestratorAdapter: {e}")
            raise ImportError(f"LegacyOrchestratorAdapter not available: {e}")
    
    @staticmethod
    def list_available_orchestrators() -> Dict[str, str]:
        """
        List all available orchestrator types with descriptions
        
        Returns:
            Dict mapping orchestrator types to descriptions
        """
        return {
            OrchestratorType.CHECKLIST.value: "Structured checklist-driven fitness coaching with RAG-enhanced questions",
            OrchestratorType.CONVERSATIONAL.value: "Natural conversation flow with personality adaptation",
            OrchestratorType.LEGACY.value: "Original orchestrator for debugging and compatibility",
            OrchestratorType.AUTO.value: "Automatically select best orchestrator based on context"
        }
    
    @staticmethod
    def get_recommended_orchestrator(user_type: str = "beginner") -> OrchestratorType:
        """
        Get recommended orchestrator for different user types
        
        Args:
            user_type: Type of user (beginner, intermediate, advanced, trainer)
            
        Returns:
            Recommended OrchestratorType
        """
        recommendations = {
            "beginner": OrchestratorType.CHECKLIST,     # Structured guidance
            "intermediate": OrchestratorType.AUTO,      # Flexible based on context
            "advanced": OrchestratorType.CONVERSATIONAL, # Natural conversation
            "trainer": OrchestratorType.CONVERSATIONAL,  # Professional conversation
            "debug": OrchestratorType.LEGACY            # Development/debugging
        }
        
        return recommendations.get(user_type.lower(), OrchestratorType.CHECKLIST)