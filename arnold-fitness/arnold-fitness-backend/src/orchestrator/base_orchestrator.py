"""
Arnold Fitness Platform - Base Orchestrator
Abstract base class implementing Strategy pattern for orchestrator unification
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from src.logger.logger import Logger
from src.db_context_manager.db_manager import DbContextManager
from src.context_validator.context_validator import ContextValidator


class BaseOrchestrator(ABC):
    """
    Abstract base class for all Arnold orchestrators implementing Strategy pattern.
    
    This class defines the common interface and shared functionality for all
    orchestrator implementations (legacy, checklist-driven, conversational).
    """
    
    def __init__(self, 
                 db_manager: DbContextManager,
                 validator: ContextValidator,
                 session_id: str = None,
                 logger: Logger = None):
        """
        Initialize base orchestrator with common dependencies
        
        Args:
            db_manager: Database context manager instance
            validator: Context validator instance  
            session_id: Optional session identifier
            logger: Optional logger instance
        """
        self.db_manager = db_manager
        self.validator = validator
        self.session_id = session_id
        self.logger = logger or Logger()
        
        # Common orchestrator state
        self.context = {}
        self.token_usage = {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cost_usd': 0.0,
            'operations': []
        }
        self.workflow_state = "initialized"
        self.errors = []
        
        self.logger.info(f"Initialized {self.__class__.__name__} for session {session_id}")
    
    # Abstract Methods - Must be implemented by all subclasses
    
    @abstractmethod
    def process_user_input(self, user_input: str, context: Dict = None) -> Dict:
        """
        Process user input through orchestrator-specific workflow
        
        Args:
            user_input: Raw user input text
            context: Optional context dictionary
            
        Returns:
            Dict containing response and updated context
        """
        pass
    
    @abstractmethod
    def initialize_session(self, client_info: Dict = None) -> Dict:
        """
        Initialize a new coaching session
        
        Args:
            client_info: Optional client information
            
        Returns:
            Dict containing initial session context
        """
        pass
    
    @abstractmethod
    def get_next_guidance(self, context: Dict) -> Dict:
        """
        Generate next guidance or question based on current context
        
        Args:
            context: Current session context
            
        Returns:
            Dict containing guidance text and any updates
        """
        pass
    
    # Concrete Methods - Shared functionality across all orchestrators
    
    def update_token_usage(self, operation_name: str, input_tokens: int, 
                          output_tokens: int, cost_usd: float = 0.0):
        """Update token usage tracking"""
        self.token_usage['total_input_tokens'] += input_tokens
        self.token_usage['total_output_tokens'] += output_tokens
        self.token_usage['total_cost_usd'] += cost_usd
        
        operation = {
            'operation': operation_name,
            'timestamp': datetime.now().isoformat(),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': cost_usd
        }
        self.token_usage['operations'].append(operation)
        
        self.logger.debug(f"Token usage - {operation_name}: {input_tokens}+{output_tokens} tokens, ${cost_usd:.4f}")
    
    def get_token_usage_summary(self) -> Dict:
        """Get current token usage summary"""
        return {
            'total_input_tokens': self.token_usage['total_input_tokens'],
            'total_output_tokens': self.token_usage['total_output_tokens'],
            'total_tokens': self.token_usage['total_input_tokens'] + self.token_usage['total_output_tokens'],
            'total_cost_usd': self.token_usage['total_cost_usd'],
            'operations_count': len(self.token_usage['operations'])
        }
    
    def validate_context(self, context: Dict) -> Tuple[bool, List[str]]:
        """
        Validate context using the context validator
        
        Args:
            context: Context to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            is_valid = self.validator.validate(context)
            return is_valid, []
        except Exception as e:
            error_msg = f"Context validation error: {str(e)}"
            self.logger.error(error_msg)
            return False, [error_msg]
    
    def persist_context(self, context: Dict) -> bool:
        """
        Persist context to database
        
        Args:
            context: Context to persist
            
        Returns:
            bool indicating success
        """
        try:
            if self.session_id:
                self.db_manager.store_context(self.session_id, context)
                self.logger.debug(f"Context persisted for session {self.session_id}")
                return True
            else:
                self.logger.warning("No session_id provided, cannot persist context")
                return False
        except Exception as e:
            error_msg = f"Context persistence error: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def load_context(self) -> Optional[Dict]:
        """
        Load context from database
        
        Returns:
            Dict containing loaded context or None if not found
        """
        try:
            if self.session_id:
                context = self.db_manager.load_context(self.session_id)
                if context:
                    self.context = context
                    self.logger.debug(f"Context loaded for session {self.session_id}")
                return context
            else:
                self.logger.warning("No session_id provided, cannot load context")
                return None
        except Exception as e:
            error_msg = f"Context loading error: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return None
    
    def handle_error(self, error: Exception, context: str = "") -> Dict:
        """
        Common error handling across all orchestrators
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            
        Returns:
            Dict containing error response
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.errors.append(error_msg)
        self.logger.error(error_msg)
        
        return {
            'success': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat(),
            'orchestrator_type': self.__class__.__name__
        }
    
    def get_orchestrator_status(self) -> Dict:
        """Get current orchestrator status and metrics"""
        return {
            'orchestrator_type': self.__class__.__name__,
            'session_id': self.session_id,
            'workflow_state': self.workflow_state,
            'errors_count': len(self.errors),
            'token_usage': self.get_token_usage_summary(),
            'timestamp': datetime.now().isoformat()
        }
    
    # Template method defining common workflow
    def execute_workflow(self, user_input: str, context: Dict = None) -> Dict:
        """
        Template method defining common orchestrator workflow
        
        Args:
            user_input: User input to process
            context: Optional context override
            
        Returns:
            Dict containing workflow results
        """
        try:
            # 1. Load or use provided context
            working_context = context or self.load_context() or {}
            
            # 2. Validate context
            is_valid, validation_errors = self.validate_context(working_context)
            if not is_valid:
                return self.handle_error(
                    Exception(f"Context validation failed: {validation_errors}"),
                    "execute_workflow"
                )
            
            # 3. Process input (delegated to subclass)
            self.workflow_state = "processing"
            result = self.process_user_input(user_input, working_context)
            
            # 4. Persist updated context if successful
            if result.get('success', False) and 'context' in result:
                self.persist_context(result['context'])
            
            # 5. Update workflow state
            self.workflow_state = "completed" if result.get('success') else "error"
            
            return result
            
        except Exception as e:
            self.workflow_state = "error"
            return self.handle_error(e, "execute_workflow")