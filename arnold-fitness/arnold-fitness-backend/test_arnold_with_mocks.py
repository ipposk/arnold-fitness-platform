#!/usr/bin/env python3
"""
Arnold test with mock DynamoDB and S3 - uses the same mock system as arnold_main_local.py
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Setup path and environment
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
load_dotenv()

# Import the mock classes from arnold_main_local.py
from arnold_main_local import MockDynamoDBResource, MockS3Client

# Setup boto3 mocks before importing handlers
import boto3

# Store originals
original_resource = boto3.resource
original_client = boto3.client

# Create mock instances
mock_dynamodb = MockDynamoDBResource()
mock_s3 = MockS3Client()

def mock_resource(service_name, *args, **kwargs):
    if service_name == 'dynamodb':
        return mock_dynamodb
    return original_resource(service_name, *args, **kwargs)

def mock_client(service_name, *args, **kwargs):
    if service_name == 's3':
        return mock_s3
    return original_client(service_name, *args, **kwargs)

# Apply mocks
boto3.resource = mock_resource
boto3.client = mock_client

# Now import the lambda handlers (they will use our mocks)
try:
    from backend.lambda_handlers import (
        create_session_handler,
        process_chat_message_handler
    )
    print("[SUCCESS] Lambda handlers imported with mocks")
except Exception as e:
    print(f"[ERROR] Error importing Lambda handlers: {e}")
    sys.exit(1)

def test_arnold_conversation():
    """Test a complete Arnold conversation with mocks"""
    print("\n=== ARNOLD FITNESS COACH - MOCK TEST ===")
    print("Testing complete conversation workflow...")
    
    # Test 1: Create session
    print("\n--- Step 1: Create Session ---")
    
    create_event = {
        'body': json.dumps({
            'goal': 'Weight Loss Coaching Session',
            'pt_type': 'initial_assessment',
            'client_id': 'client-test-123',
            'client_name': 'Mario Rossi'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'mario.rossi@example.com',
                    'sub': 'user-test-456'
                }
            }
        }
    }
    
    class MockContext:
        aws_request_id = 'mock-request-123'
    
    try:
        result = create_session_handler(create_event, MockContext())
        print(f"Session creation status: {result.get('statusCode')}")
        
        if result.get('statusCode') in [200, 201]:  # Both 200 and 201 are success
            body = json.loads(result['body'])
            session_id = body.get('test_id') or body.get('session_id')  # Handle both field names
            print(f"[SUCCESS] Session created: {session_id}")
        else:
            print(f"[ERROR] Session creation failed: {json.loads(result['body'])}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during session creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Send fitness coaching messages
    test_messages = [
        "Ciao! Sono Mario, ho 35 anni e voglio perdere 8kg per l'estate.",
        "Peso attualmente 85kg, sono alto 175cm e faccio un lavoro sedentario.",
        "Non faccio sport da 3 anni, ma vorrei ricominciare con qualcosa di semplice.",
        "Preferisco allenarmi a casa, ho poco tempo durante la settimana."
    ]
    
    print(f"\n--- Step 2: Process Messages ---")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n>> Message {i}: {message}")
        
        message_event = {
            'pathParameters': {
                'test_id': session_id
            },
            'body': json.dumps({
                'user_input': message
            }),
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'email': 'mario.rossi@example.com',
                        'sub': 'user-test-456'
                    }
                }
            }
        }
        
        try:
            result = process_chat_message_handler(message_event, MockContext())
            print(f"Message processing status: {result.get('statusCode')}")
            
            if result.get('statusCode') == 200:
                body = json.loads(result['body'])
                guidance = body.get('guidance_markdown', '')
                
                print(f"\n<< ARNOLD'S RESPONSE:")
                # Display first 300 characters of response
                display_text = guidance[:300] + "..." if len(guidance) > 300 else guidance
                print(display_text)
                print("---")
                
                # Show context changes if any
                context_changes = body.get('context_changes', [])
                if context_changes:
                    print("CONTEXT UPDATES:")
                    for change in context_changes[:3]:  # Show first 3 changes
                        print(f"  - {change}")
                
            else:
                error_body = json.loads(result['body'])
                print(f"[ERROR] Message processing failed: {error_body.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Exception during message processing: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Small pause between messages
        import time
        time.sleep(0.5)
    
    print("\n=== TEST COMPLETED SUCCESSFULLY ===")
    print("Arnold successfully processed all messages!")
    return True

if __name__ == "__main__":
    success = test_arnold_conversation()
    if success:
        print("\n[SUCCESS] All tests passed! Arnold is working correctly.")
    else:
        print("\n[ERROR] Some tests failed. Check the errors above.")