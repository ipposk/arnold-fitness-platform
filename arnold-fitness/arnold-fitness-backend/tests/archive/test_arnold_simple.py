#!/usr/bin/env python3
"""
Simple Arnold test script that simulates user input without interactive mode
"""
import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

# Import the lambda handlers directly
try:
    from backend.lambda_handlers import (
        create_session_handler,
        process_chat_message_handler,
        get_session_context_handler,
    )
    print("[SUCCESS] Lambda handlers imported successfully")
except Exception as e:
    print(f"[ERROR] Error importing Lambda handlers: {e}")
    sys.exit(1)

def test_create_session():
    """Test session creation"""
    print("\n=== Testing Session Creation ===")
    
    # Create test event with proper authorization
    event = {
        'body': json.dumps({
            'goal': 'Arnold Test Session',
            'pt_type': 'initial_assessment',
            'client_id': 'test-client-id',
            'client_name': 'Test Client'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'test@example.com',
                    'sub': 'test-user-id-123'
                }
            }
        }
    }
    
    # Mock context
    class MockContext:
        aws_request_id = 'test-request-id'
    
    context = MockContext()
    
    try:
        result = create_session_handler(event, context)
        print(f"[SUCCESS] Session creation result: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result['body'])
            session_id = body.get('session_id')
            print(f"[SUCCESS] Session ID: {session_id}")
            return session_id
        else:
            print(f"[ERROR] Session creation failed: {result}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Session creation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_process_message(session_id, message):
    """Test processing a chat message"""
    print(f"\n=== Testing Message Processing ===")
    print(f"Message: {message}")
    
    # Create test event with proper authorization
    event = {
        'body': json.dumps({
            'session_id': session_id,
            'message': message
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'test@example.com',
                    'sub': 'test-user-id-123'
                }
            }
        }
    }
    
    # Mock context
    class MockContext:
        aws_request_id = 'test-request-id'
    
    context = MockContext()
    
    try:
        result = process_chat_message_handler(event, context)
        print(f"[SUCCESS] Message processing result: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result['body'])
            guidance = body.get('guidance_markdown', '')
            print(f"\n--- ARNOLD'S RESPONSE ---")
            print(guidance[:500] + "..." if len(guidance) > 500 else guidance)
            print("--- END RESPONSE ---\n")
            return True
        else:
            print(f"[ERROR] Message processing failed: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Message processing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== ARNOLD FITNESS COACH - SIMPLE TEST ===")
    print("Testing core Arnold functionality...")
    
    # Test 1: Create session
    session_id = test_create_session()
    if not session_id:
        print("[ERROR] Cannot continue without session")
        return
    
    # Test 2: New user assessment
    test_messages = [
        "Ciao, sono nuovo qui. Voglio perdere 5kg per l'estate",
        "Ho 30 anni, peso 80kg e sono alto 175cm",
        "Non faccio sport da molto tempo",
        "Preferisco allenarmi a casa senza attrezzi"
    ]
    
    print(f"\n=== Testing Arnold's Coaching Responses ===")
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test Message {i} ---")
        success = test_process_message(session_id, message)
        if not success:
            print(f"[ERROR] Failed at test message {i}")
            break
        
        # Small pause between messages
        import time
        time.sleep(1)
    
    print("\n=== Test Complete ===")
    print("Arnold fitness coaching test completed!")

if __name__ == "__main__":
    main()