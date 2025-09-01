"""
Unit tests for OrchestratorFactory
Tests the Strategy pattern implementation for orchestrator creation
"""

import pytest
from unittest.mock import Mock, patch
from src.orchestrator.orchestrator_factory import OrchestratorFactory, OrchestratorType
from src.db_context_manager.db_manager import DbContextManager
from src.context_validator.context_validator import ContextValidator
from src.logger.logger import Logger


class TestOrchestratorFactory:
    """Test cases for OrchestratorFactory"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.db_manager = Mock(spec=DbContextManager)
        self.validator = Mock(spec=ContextValidator)
        self.logger = Mock(spec=Logger)
        self.session_id = "test_session_123"
    
    def test_create_orchestrator_checklist_type(self):
        """Test creating checklist orchestrator"""
        with patch('src.orchestrator.orchestrator_factory.ChecklistDrivenOrchestrator') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = OrchestratorFactory.create_orchestrator(
                orchestrator_type="checklist",
                db_manager=self.db_manager,
                validator=self.validator,
                session_id=self.session_id,
                logger=self.logger
            )
            
            assert result == mock_instance
            mock_class.assert_called_once_with(
                db_manager=self.db_manager,
                validator=self.validator,
                session_id=self.session_id,
                logger=self.logger
            )
    
    def test_create_orchestrator_auto_selection(self):
        """Test auto orchestrator selection"""
        context = {
            'checklist_progress': {
                'current_checklist': 'onboarding',
                'completed': False
            }
        }
        
        with patch('src.orchestrator.orchestrator_factory.ChecklistDrivenOrchestrator') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = OrchestratorFactory.create_orchestrator(
                orchestrator_type="auto",
                db_manager=self.db_manager,
                validator=self.validator,
                session_id=self.session_id,
                logger=self.logger,
                context=context
            )
            
            assert result == mock_instance
    
    def test_invalid_orchestrator_type(self):
        """Test error handling for invalid orchestrator type"""
        with pytest.raises(ValueError, match="Invalid orchestrator type"):
            OrchestratorFactory.create_orchestrator(
                orchestrator_type="invalid_type",
                db_manager=self.db_manager,
                validator=self.validator
            )
    
    def test_list_available_orchestrators(self):
        """Test listing available orchestrator types"""
        orchestrators = OrchestratorFactory.list_available_orchestrators()
        
        assert isinstance(orchestrators, dict)
        assert "checklist" in orchestrators
        assert "conversational" in orchestrators  
        assert "legacy" in orchestrators
        assert "auto" in orchestrators
    
    def test_get_recommended_orchestrator(self):
        """Test orchestrator recommendations"""
        beginner_rec = OrchestratorFactory.get_recommended_orchestrator("beginner")
        assert beginner_rec == OrchestratorType.CHECKLIST
        
        trainer_rec = OrchestratorFactory.get_recommended_orchestrator("trainer")
        assert trainer_rec == OrchestratorType.CONVERSATIONAL
        
        debug_rec = OrchestratorFactory.get_recommended_orchestrator("debug")
        assert debug_rec == OrchestratorType.LEGACY
    
    def test_auto_select_with_preference(self):
        """Test auto selection respects user preferences"""
        context = {
            'user_preferences': {
                'interface_mode': 'conversational'
            }
        }
        
        result_type = OrchestratorFactory._auto_select_orchestrator(
            context=context,
            logger=self.logger
        )
        
        assert result_type == OrchestratorType.CONVERSATIONAL
    
    def test_auto_select_extensive_conversation(self):
        """Test auto selection with extensive conversation history"""
        context = {
            'conversation_history': [{'message': f'test {i}'} for i in range(15)]
        }
        
        result_type = OrchestratorFactory._auto_select_orchestrator(
            context=context,
            logger=self.logger
        )
        
        assert result_type == OrchestratorType.CONVERSATIONAL