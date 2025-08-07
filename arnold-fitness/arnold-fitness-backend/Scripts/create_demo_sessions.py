# scripts/create_demo_sessions.py

import boto3
import json
import uuid
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table('PentestSessions')

# Sessioni mock per riempire la dashboard
demo_sessions = [
    {
        "test_id": f"DEMO-{uuid.uuid4().hex[:8].upper()}",
        "user_email": "tester1@demo.penelope.com",
        "context": json.dumps({
            "session_name": "Web App Security Assessment - Acme Corp",
            "client": {"name": "Acme Corporation"},
            "checklist": {
                "reconnaissance": {
                    "tasks": {
                        "subdomain_enum": {
                            "checks": {
                                "check1": {"status": "completed"},
                                "check2": {"status": "completed"},
                                "check3": {"status": "in_progress"}
                            }
                        }
                    }
                }
            }
        }),
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z"
    },
    {
        "test_id": f"DEMO-{uuid.uuid4().hex[:8].upper()}",
        "user_email": "tester2@demo.penelope.com",
        "context": json.dumps({
            "session_name": "API Security Testing - TechStart",
            "client": {"name": "TechStart Inc"},
            "checklist": {
                "api_testing": {
                    "tasks": {
                        "auth_bypass": {
                            "checks": {
                                "check1": {"status": "completed"},
                                "check2": {"status": "pending"}
                            }
                        }
                    }
                }
            }
        }),
        "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat() + "Z"
    }
]

# Inserisci sessioni mock
for session in demo_sessions:
    table.put_item(Item=session)
    print(f"Created session: {session['test_id']}")