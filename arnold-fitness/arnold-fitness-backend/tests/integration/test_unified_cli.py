"""
Integration tests for Unified CLI System
Tests the consolidated CLI interface and mode selection
"""

import pytest
import subprocess
import sys
from pathlib import Path

class TestUnifiedCLI:
    """Integration tests for unified CLI"""
    
    def setup_method(self):
        """Setup test environment"""
        self.cli_path = Path("arnold-fitness/arnold-fitness-backend/cli/main.py")
        self.python_cmd = sys.executable
    
    def test_cli_help_output(self):
        """Test CLI help command output"""
        result = subprocess.run(
            [self.python_cmd, str(self.cli_path), "--help"],
            capture_output=True,
            text=True,
            cwd="arnold-fitness/arnold-fitness-backend"
        )
        
        assert result.returncode == 0
        assert "Arnold Fitness Platform CLI" in result.stdout
        assert "checklist" in result.stdout
        assert "debug" in result.stdout
        assert "demo" in result.stdout
    
    def test_cli_invalid_mode(self):
        """Test error handling for invalid modes"""
        result = subprocess.run(
            [self.python_cmd, str(self.cli_path), "invalid_mode"],
            capture_output=True,
            text=True,
            cwd="arnold-fitness/arnold-fitness-backend"
        )
        
        assert result.returncode == 2  # argparse error code
        assert "invalid choice" in result.stderr.lower()
    
    def test_cli_color_system_import(self):
        """Test that color system can be imported correctly"""
        try:
            from cli.ui.colors import ArnoldColors
            
            # Test that basic methods exist
            assert hasattr(ArnoldColors, 'print_logo')
            assert hasattr(ArnoldColors, 'format_progress')
            
            # Test basic functionality
            progress_formatted = ArnoldColors.format_progress(75)
            assert isinstance(progress_formatted, str)
            assert "75%" in progress_formatted
            
        except ImportError as e:
            pytest.fail(f"Failed to import ArnoldColors: {e}")
    
    def test_cli_mode_imports(self):
        """Test that CLI mode modules can be imported"""
        try:
            from cli.modes.checklist_mode import run_checklist_mode
            from cli.modes.debug_mode import run_debug_mode
            from cli.modes.demo_mode import run_demo_mode
            
            # Test that functions exist and are callable
            assert callable(run_checklist_mode)
            assert callable(run_debug_mode)
            assert callable(run_demo_mode)
            
        except ImportError as e:
            pytest.fail(f"Failed to import CLI modes: {e}")
    
    def test_orchestrator_selector_import(self):
        """Test orchestrator selector functionality"""
        try:
            from cli.ui.orchestrator_selector import OrchestratorSelector
            
            # Test recommendation functionality
            recommendations = OrchestratorSelector.get_recommendations("beginner")
            assert isinstance(recommendations, dict)
            assert 'recommended' in recommendations
            assert 'reason' in recommendations
            
        except ImportError as e:
            pytest.fail(f"Failed to import OrchestratorSelector: {e}")