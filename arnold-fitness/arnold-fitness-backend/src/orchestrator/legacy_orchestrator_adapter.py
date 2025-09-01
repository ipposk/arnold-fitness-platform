"""
Arnold Fitness Platform - Legacy Orchestrator Adapter
Adapter pattern to make legacy orchestrator compatible with Strategy pattern
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_orchestrator import BaseOrchestrator
from src.logger.logger import Logger
from src.db_context_manager.db_manager import DbContextManager
from src.context_validator.context_validator import ContextValidator


class LegacyOrchestratorAdapter(BaseOrchestrator):
    """
    Adapter class to integrate legacy Orchestrator with the new Strategy pattern.
    
    This adapter wraps the original Orchestrator class to provide compatibility
    with the BaseOrchestrator interface while preserving existing functionality.
    """
    
    def __init__(self, 
                 db_manager: DbContextManager,
                 validator: ContextValidator,
                 session_id: str = None,
                 logger: Logger = None,
                 **kwargs):
        """
        Initialize adapter with legacy orchestrator instance
        
        Args:
            db_manager: Database context manager
            validator: Context validator
            session_id: Session identifier
            logger: Logger instance
            **kwargs: Additional arguments for legacy orchestrator
        """
        super().__init__(db_manager, validator, session_id, logger)
        
        # Initialize legacy orchestrator
        try:
            from .orchestrator import Orchestrator
            
            # Initialize with legacy constructor parameters
            self.legacy_orchestrator = Orchestrator(
                db_manager=db_manager,
                validator=validator,
                logger=logger,
                **kwargs
            )
            
            self.logger.info("Legacy orchestrator adapter initialized successfully")
            
        except ImportError as e:
            error_msg = f"Failed to import legacy Orchestrator: {e}"
            self.logger.error(error_msg)
            raise ImportError(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to initialize legacy orchestrator: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def process_user_input(self, user_input: str, context: Dict = None) -> Dict:
        """
        Process user input using legacy orchestrator
        
        Args:
            user_input: User input text
            context: Session context
            
        Returns:
            Dict containing processed response and updated context
        """
        try:
            self.logger.debug(f"Processing user input through legacy orchestrator: {user_input[:100]}...")
            
            # Use context or load from session
            working_context = context or self.context or {}
            
            # Call legacy orchestrator's main processing method
            # Note: Legacy orchestrator might have different method signature
            result = self._call_legacy_method(user_input, working_context)
            
            # Standardize response format for compatibility
            standardized_result = self._standardize_response(result)
            
            # Update token usage from legacy orchestrator if available
            self._sync_token_usage()
            
            return standardized_result
            
        except Exception as e:
            return self.handle_error(e, "process_user_input")
    
    def initialize_session(self, client_info: Dict = None) -> Dict:
        """
        Initialize session using legacy orchestrator
        
        Args:
            client_info: Client information
            
        Returns:
            Dict containing initial session context
        """
        try:
            self.logger.debug("Initializing session through legacy orchestrator")
            
            # Initialize context based on legacy orchestrator patterns
            initial_context = {
                'session_id': self.session_id,
                'client_info': client_info or {},
                'initialized_at': datetime.now().isoformat(),
                'orchestrator_type': 'legacy',
                'workflow_state': 'initialized'
            }
            
            # If legacy orchestrator has initialization method, call it
            if hasattr(self.legacy_orchestrator, 'initialize_session'):
                legacy_result = self.legacy_orchestrator.initialize_session(client_info)
                initial_context.update(legacy_result.get('context', {}))
            
            self.context = initial_context
            return {
                'success': True,
                'context': initial_context,
                'message': 'Session initialized with legacy orchestrator'
            }
            
        except Exception as e:
            return self.handle_error(e, "initialize_session")
    
    def get_next_guidance(self, context: Dict) -> Dict:
        """
        Get next guidance using legacy orchestrator
        
        Args:
            context: Current session context
            
        Returns:
            Dict containing guidance and any context updates
        """
        try:
            self.logger.debug("Getting next guidance from legacy orchestrator")
            
            # Legacy orchestrator might not have this exact method
            # Try to adapt existing methods
            if hasattr(self.legacy_orchestrator, 'get_next_guidance'):
                result = self.legacy_orchestrator.get_next_guidance(context)
            else:
                # Fallback: generate basic guidance
                result = self._generate_fallback_guidance(context)
            
            return self._standardize_response(result)
            
        except Exception as e:
            return self.handle_error(e, "get_next_guidance")
    
    def _call_legacy_method(self, user_input: str, context: Dict) -> Dict:
        """
        Call appropriate legacy orchestrator method based on available interface
        
        Args:
            user_input: User input
            context: Session context
            
        Returns:
            Result from legacy orchestrator
        """
        # Try to find the main processing method in legacy orchestrator
        legacy_methods = [
            'process_user_input',
            'orchestrate_workflow',
            'handle_user_input',
            'process_input'
        ]
        
        for method_name in legacy_methods:
            if hasattr(self.legacy_orchestrator, method_name):
                method = getattr(self.legacy_orchestrator, method_name)
                try:
                    # Try different parameter combinations
                    if method_name in ['process_user_input', 'handle_user_input']:
                        return method(user_input, context)
                    else:
                        return method(user_input)
                except TypeError:
                    # Try with different parameter signature
                    continue
        
        # If no suitable method found, create fallback response
        return self._create_fallback_response(user_input, context)
    
    def _standardize_response(self, result: Any) -> Dict:
        """
        Standardize legacy orchestrator response to match BaseOrchestrator interface
        
        Args:
            result: Response from legacy orchestrator
            
        Returns:
            Standardized response dictionary
        """
        if isinstance(result, dict):
            # If it's already a dict, ensure required fields exist
            standardized = {
                'success': result.get('success', True),
                'response': result.get('response', result.get('message', '')),
                'context': result.get('context', self.context),
                'timestamp': datetime.now().isoformat(),
                'orchestrator_type': 'legacy'
            }
            
            # Preserve any additional fields from legacy response
            for key, value in result.items():
                if key not in standardized:
                    standardized[key] = value
                    
            return standardized
        
        elif isinstance(result, str):
            # If it's a string response, wrap it
            return {
                'success': True,
                'response': result,
                'context': self.context,
                'timestamp': datetime.now().isoformat(),
                'orchestrator_type': 'legacy'
            }
        
        else:
            # For any other type, convert to string
            return {
                'success': True,
                'response': str(result),
                'context': self.context,
                'timestamp': datetime.now().isoformat(),
                'orchestrator_type': 'legacy'
            }
    
    def _sync_token_usage(self):
        """Sync token usage from legacy orchestrator if available"""
        try:
            if hasattr(self.legacy_orchestrator, 'token_usage'):
                legacy_usage = self.legacy_orchestrator.token_usage
                if isinstance(legacy_usage, dict):
                    # Update our token usage with legacy data
                    for key in ['total_input_tokens', 'total_output_tokens', 'total_cost_usd']:
                        if key in legacy_usage:
                            self.token_usage[key] = legacy_usage[key]
        except Exception as e:
            self.logger.debug(f"Could not sync token usage from legacy orchestrator: {e}")
    
    def _generate_fallback_guidance(self, context: Dict) -> Dict:
        """Generate fallback guidance when legacy methods are not available"""
        return {
            'success': True,
            'response': "Welcome to Arnold Fitness Platform. How can I help you with your fitness goals today?",
            'guidance_type': 'fallback',
            'context': context
        }
    
    def _create_fallback_response(self, user_input: str, context: Dict) -> Dict:
        """Create fallback response when legacy orchestrator methods fail"""
        return {
            'success': True,
            'response': f"I received your input: '{user_input}'. The legacy system is processing your request.",
            'fallback': True,
            'context': context
        }