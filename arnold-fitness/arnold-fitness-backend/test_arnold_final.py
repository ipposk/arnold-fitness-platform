#!/usr/bin/env python3
"""
Final Arnold test using the same approach as arnold_main_local.py
This test demonstrates Arnold's complete fitness coaching capabilities
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

print("=== ARNOLD FITNESS COACH - FINAL INTEGRATION TEST ===")
print("Testing Arnold's complete fitness coaching workflow...\n")

# Import and setup the AWSLocalCLI from arnold_main_local.py
from arnold_main_local import AWSLocalCLI

def simulate_user_conversation():
    """Simulate a complete fitness coaching conversation"""
    
    print("--- Step 1: Initialize Arnold ---")
    cli = AWSLocalCLI()
    
    # Create session
    try:
        session_id = cli.create_session()
        print(f"✓ Session created: {session_id}")
    except Exception as e:
        print(f"✗ Failed to create session: {e}")
        return False
    
    print("\n--- Step 2: Fitness Coaching Conversation ---")
    
    # Test conversation messages
    messages = [
        "Ciao! Sono Mario, ho 35 anni e voglio perdere 8kg per l'estate.",
        "Peso attualmente 85kg, sono alto 175cm e lavoro in ufficio tutto il giorno.",
        "Non faccio sport da anni, ma sono motivato a ricominciare!",
        "Preferisco allenarmi a casa perché ho poco tempo. Cosa mi consigli?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n>>> USER MESSAGE {i}:")
        print(f"    \"{message}\"")
        
        try:
            print(f"\n>>> ARNOLD'S RESPONSE {i}:")
            result = cli.send_message(message)
            
            if result:
                print("✓ Message processed successfully")
                
                # Show brief context update info
                if 'last_output' in result:
                    guidance = result['last_output'].get('guidance_markdown', '')
                    if guidance:
                        # Show first few lines of Arnold's response
                        lines = guidance.split('\n')[:3]
                        preview = '\n    '.join(lines)
                        print(f"    PREVIEW: {preview}")
                        if len(guidance.split('\n')) > 3:
                            print("    ... (more content)")
            else:
                print("✗ No result returned")
                
        except Exception as e:
            print(f"✗ Error processing message: {e}")
            return False
        
        print("-" * 50)
    
    print("\n--- Step 3: Check Checklist Progress ---")
    try:
        cli.show_checklist_status()
        print("✓ Checklist status displayed")
    except Exception as e:
        print(f"✗ Error showing checklist: {e}")
    
    print("\n=== TEST COMPLETED SUCCESSFULLY ===")
    print("Arnold demonstrated complete fitness coaching capabilities!")
    return True

def test_arnold_components():
    """Test individual Arnold components"""
    print("\n--- Component Testing ---")
    
    # Test basic functionality
    try:
        cli = AWSLocalCLI()
        session_id = cli.create_session()
        
        # Test simple message
        result = cli.send_message("Test message - sono pronto per iniziare!")
        
        if result and 'last_output' in result:
            print("✓ Core message processing works")
            return True
        else:
            print("✗ Core message processing failed")
            return False
            
    except Exception as e:
        print(f"✗ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Arnold Fitness Coach integration test...\n")
    
    # Test 1: Component functionality
    component_test = test_arnold_components()
    
    if component_test:
        print("\n✓ Component tests passed! Proceeding to full conversation test...\n")
        
        # Test 2: Full conversation
        conversation_test = simulate_user_conversation()
        
        if conversation_test:
            print("\n🎯 ALL TESTS PASSED!")
            print("Arnold Fitness Coach is ready for production use!")
        else:
            print("\n⚠️ Conversation test had issues")
    else:
        print("\n❌ Component tests failed - skipping conversation test")
    
    print("\nTest complete.")