#!/usr/bin/env python3
"""
Core Arnold test - tests the essential components directly
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Setup
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

print("=== ARNOLD CORE COMPONENT TEST ===\n")

def test_schema_validation():
    """Test the updated schema validation"""
    print("1. Testing schema validation...")
    
    try:
        from src.context_validator.context_validator import ContextValidator
        from pathlib import Path
        schema_path = Path(__file__).parent / "src" / "context_validator" / "schemas" / "db_context_schema.json"
        validator = ContextValidator(str(schema_path))
        
        # Test data with fitness-focused fields
        test_context = {
            "session_id": "test-session-123",
            "fitness_type": "initial_assessment", 
            "scope": {"targets": ["weight_loss", "muscle_gain"]},
            "checklist": [],
            "current_phase_id": "ASS",
            "goal": "Test fitness goal",
            "findings": [],
            "evidence": [],
            "meta": {
                "timestamp": "2025-08-06T12:00:00.000Z",
                "created_at": "2025-08-06T12:00:00.000Z",
                "updated_at": "2025-08-06T12:00:00.000Z",
                "updated_by": "test",
                "source": "test",
                "version": "1.0"
            }
        }
        
        validation_result = validator.validate(test_context)
        if isinstance(validation_result, tuple):
            is_valid, errors = validation_result
        else:
            is_valid = validation_result
            errors = None
        
        if is_valid:
            print("   SUCCESS Schema validation PASSED - fitness fields accepted")
            return True
        else:
            print(f"   ERROR Schema validation FAILED: {errors}")
            return False
            
    except Exception as e:
        print(f"   ERROR Schema validation ERROR: {e}")
        return False

def test_checklist_loading():
    """Test checklist loading from local files"""
    print("2. Testing checklist loading...")
    
    try:
        # Test local checklist loading
        from backend.lambda_handlers import load_checklist_from_s3
        
        checklist = load_checklist_from_s3("initial_assessment")
        
        if checklist and isinstance(checklist, list) and len(checklist) > 0:
            print(f"   [OK] Checklist loaded successfully - {len(checklist)} phases")
            
            # Check if it has fitness content
            first_phase = checklist[0]
            if 'ASS' in first_phase.get('phase_id', ''):
                print("   [OK] Fitness assessment phase detected")
                return True
            else:
                print("   [WARNING] Checklist loaded but doesn't look like fitness content")
                return False
        else:
            print("   [FAIL] Checklist loading failed - empty or invalid")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Checklist loading ERROR: {e}")
        return False

def test_gemini_client():
    """Test Gemini LLM client connectivity"""
    print("3. Testing Gemini LLM client...")
    
    try:
        from src.llm_interfaces.clients.gemini_client import GeminiClient
        
        client = GeminiClient()
        
        # Simple test request
        response = client.generate_response("Rispondi con una sola parola: 'test'")
        
        if response and len(response) > 0:
            print(f"   [OK] Gemini client working - response: '{response[:50]}...'")
            return True
        else:
            print("   [FAIL] Gemini client failed - no response")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Gemini client ERROR: {e}")
        return False

def test_orchestrator_import():
    """Test Orchestrator and related imports"""
    print("4. Testing component imports...")
    
    try:
        from src.orchestrator.orchestrator import Orchestrator
        from src.db_context_manager.db_manager import DbContextManager
        from src.llm_interfaces.user_input_interpreter_llm.user_input_interpreter_llm import UserInputInterpreterLLM
        from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM
        from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM
        
        print("   [OK] All core components imported successfully")
        return True
        
    except Exception as e:
        print(f"   [ERROR] Component import ERROR: {e}")
        return False

def run_all_tests():
    """Run all core component tests"""
    print("Running Arnold core component tests...\n")
    
    tests = [
        ("Schema Validation", test_schema_validation),
        ("Checklist Loading", test_checklist_loading), 
        ("Gemini Client", test_gemini_client),
        ("Component Imports", test_orchestrator_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
        print()
    
    print(f"=== RESULTS ===")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("[SUCCESS] ALL CORE COMPONENTS WORKING!")
        print("Arnold is ready for full integration testing.")
        return True
    else:
        print(f"[WARNING] {total - passed} tests failed")
        print("Some components need fixing before full testing.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)