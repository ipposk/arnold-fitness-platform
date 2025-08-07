import json
import os
import boto3
import uuid
from datetime import datetime
import decimal
import traceback
from boto3.dynamodb.conditions import Key, Attr

# Debugging function as per user's instructions
def log_sets_in_obj(obj, path="root"):
    """
    Scansiona ricorsivamente obj e logga tutti i set che trova, mostrando il path.
    """
    import logging  # As per user's snippet
    if isinstance(obj, set):
        # Using user's specified advanced print format
        print(f"⚠️ Found set at {path}: {list(obj)[:10]}{'...' if len(obj) > 10 else ''}")
        # Using logging.warning as per user's snippet
        logging.warning(f"Found set at {path}: {obj}")  # Original obj for full details in logs if needed
        return True
    elif isinstance(obj, dict):
        found = False
        for k, v in obj.items():
            if log_sets_in_obj(v, path + f".{k}"):
                found = True
        return found
    elif isinstance(obj, list):
        found = False
        for i, v in enumerate(obj):
            if log_sets_in_obj(v, path + f"[{i}]"):
                found = True
        return found
    return False

# Recupera la tabella DynamoDB dalla variabile d'ambiente (serverless.yml)
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE_NAME", "ArnoldSessions")
CHECKLIST_BUCKET = os.environ.get("CHECKLIST_BUCKET_NAME", "serverless-framework-deployments-eu-west-1-0944404d-92d2")
VERSIONS_TABLE = os.environ.get("DYNAMODB_VERSIONS_TABLE_NAME", "ArnoldSessionVersions")
DYNAMODB_CLIENTS_TABLE = os.environ.get("DYNAMODB_CLIENTS_TABLE_NAME", "ArnoldClients")
DYNAMODB_ORGANIZATIONS_TABLE = os.environ.get("DYNAMODB_ORGANIZATIONS_TABLE", "Organizations")
DYNAMODB_ORG_MEMBERS_TABLE = os.environ.get("DYNAMODB_ORG_MEMBERS_TABLE", "OrganizationMembers")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)
versions_table = dynamodb.Table(VERSIONS_TABLE)
clients_table = dynamodb.Table(DYNAMODB_CLIENTS_TABLE)
messages_table = dynamodb.Table("ArnoldMessages")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Content-Type": "application/json"
}

def get_user_email(user_id):
    """Funzione helper per ottenere email da user_id"""
    # Per ora return semplice, da implementare lookup se necessario
    return f"user_{user_id}@demo.com"

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def json_response(data, status=200):
    # Log before any conversion attempt if sets_to_lists wasn't perfect or was bypassed
    if log_sets_in_obj(data, path="json_response_input_before_conversion_and_dump"):
        print(
            "‼️ ATTENZIONE (json_response): Trovato almeno un set nell'oggetto 'data' prima della conversione e serializzazione! Vedi log sopra.")

    processed_data = sets_to_lists(convert_decimal(data))
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(processed_data)
    }

def sets_to_lists(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: sets_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sets_to_lists(i) for i in obj]
    else:
        return obj

def load_checklist_from_s3(pt_type: str = "webapp") -> list:
    # Check if we're in local storage mode
    use_local_storage = os.environ.get("USE_LOCAL_STORAGE", "false").lower() == "true"
    
    if use_local_storage:
        # Load from local filesystem
        from pathlib import Path
        checklist_path = Path(__file__).parent.parent / "data" / "checklists" / f"{pt_type}_checklist.json"
        if not checklist_path.exists():
            raise FileNotFoundError(f"Local checklist file not found: {checklist_path}")
        with open(checklist_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Load from S3
        s3 = boto3.client("s3")
        key = f"checklists/{pt_type}_checklist.json"
        response = s3.get_object(Bucket=CHECKLIST_BUCKET, Key=key)
        return json.load(response["Body"])

def get_session_context_handler(event, context):
    test_id = event.get("pathParameters", {}).get("test_id")
    if not test_id:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "test_id mancante"})
        }
    try:
        response = table.get_item(Key={"test_id": test_id})
        item = response.get("Item")

        if item and isinstance(item.get("context"), str):
            try:
                item["context"] = json.loads(item["context"])
            except Exception:
                pass  # If parsing fails, it might be handled later or remain a string

        if not item:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Contesto non trovato per test_id: {test_id}"})
            }
        # json_response will call log_sets_in_obj on 'item'
        return json_response(item)

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Errore durante il recupero della sessione", "details": str(e)})
        }


def calculate_session_findings(context_obj):
    """Calcola i findings di una sessione dal context - gestisce sia liste che dizionari"""
    checklist = context_obj.get("checklist", {})
    findings = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "total": 0
    }

    # GESTISCI SIA LISTE CHE DIZIONARI
    if isinstance(checklist, list):
        # Se checklist è una lista, itera direttamente
        phases = checklist
    elif isinstance(checklist, dict):
        # Se checklist è un dizionario, usa .values()
        phases = checklist.values()
    else:
        # Se non è né lista né dizionario, ritorna findings vuoti
        print(f"Warning: checklist is neither list nor dict, type: {type(checklist)}")
        return findings

    for phase in phases:
        # Assicurati che phase sia un dizionario
        if not isinstance(phase, dict):
            continue

        tasks = phase.get("tasks", {})

        # Gestisci tasks sia come lista che come dizionario
        if isinstance(tasks, list):
            task_items = tasks
        elif isinstance(tasks, dict):
            task_items = tasks.values()
        else:
            continue

        for task in task_items:
            if not isinstance(task, dict):
                continue

            checks = task.get("checks", {})

            # Gestisci checks sia come lista che come dizionario
            if isinstance(checks, list):
                check_items = checks
            elif isinstance(checks, dict):
                check_items = checks.values()
            else:
                continue

            for check in check_items:
                if not isinstance(check, dict):
                    continue

                if check.get("status") == "completed":
                    severity = str(check.get("severity", "")).lower()
                    risk_level = str(check.get("risk_level", "")).lower()
                    finding_type = str(check.get("finding_type", "")).lower()

                    # Determina il livello di severity
                    if any(level in [severity, risk_level, finding_type] for level in ["critical", "critico"]):
                        findings["critical"] += 1
                    elif any(level in [severity, risk_level, finding_type] for level in ["high", "alto"]):
                        findings["high"] += 1
                    elif any(level in [severity, risk_level, finding_type] for level in ["medium", "medio"]):
                        findings["medium"] += 1
                    elif any(level in [severity, risk_level, finding_type] for level in ["low", "basso"]):
                        findings["low"] += 1

                    findings["total"] += 1

    return findings


def calculate_session_progress(checklist):
    """Calcola la percentuale di completamento di una sessione - gestisce sia liste che dizionari"""
    if not checklist:
        return 0

    total_checks = 0
    completed_checks = 0

    # GESTISCI SIA LISTE CHE DIZIONARI
    if isinstance(checklist, list):
        phases = checklist
    elif isinstance(checklist, dict):
        phases = checklist.values()
    else:
        return 0

    for phase in phases:
        if not isinstance(phase, dict):
            continue

        tasks = phase.get("tasks", {})

        # Gestisci tasks sia come lista che come dizionario
        if isinstance(tasks, list):
            task_items = tasks
        elif isinstance(tasks, dict):
            task_items = tasks.values()
        else:
            continue

        for task in task_items:
            if not isinstance(task, dict):
                continue

            checks = task.get("checks", {})

            # Gestisci checks sia come lista che come dizionario
            if isinstance(checks, list):
                check_items = checks
            elif isinstance(checks, dict):
                check_items = checks.values()
            else:
                continue

            for check in check_items:
                if not isinstance(check, dict):
                    continue

                total_checks += 1
                if check.get("status") == "completed":
                    completed_checks += 1

    return round((completed_checks / total_checks * 100), 1) if total_checks > 0 else 0

def get_session_deletion_preview_handler(event, context):
    """
    Fornisce un'anteprima di cosa verrà eliminato senza effettuare la cancellazione
    """
    try:
        test_id = event.get("pathParameters", {}).get("test_id")
        if not test_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing test_id in path"})
            }

        print(f"=== DELETION PREVIEW FOR SESSION: {test_id} ===")

        # Verifica che la sessione esista
        try:
            session_response = table.get_item(Key={"test_id": test_id})
            session_item = session_response.get("Item")

            if not session_item:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": f"Session {test_id} not found"})
                }

        except Exception as e:
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "error": "Error checking session existence",
                    "details": str(e)
                })
            }

        # Conta versioni
        versions_count = 0
        try:
            versions_response = versions_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('test_id').eq(test_id),
                Select='COUNT'  # Solo conta, non recupera items
            )
            versions_count = versions_response.get('Count', 0)
        except Exception as e:
            print(f"Error counting versions: {str(e)}")

        # Conta messaggi
        messages_count = 0
        try:
            messages_table = dynamodb.Table("ArnoldMessages")
            messages_response = messages_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('test_id').eq(test_id),
                Select='COUNT'  # Solo conta, non recupera items
            )
            messages_count = messages_response.get('Count', 0)
        except Exception as e:
            print(f"Error counting messages: {str(e)}")

        # Estrai dettagli sessione
        session_details = {
            "test_id": test_id,
            "user_email": session_item.get("user_email", "Unknown"),
            "client_id": session_item.get("client_id", "Unknown"),
            "client_name": session_item.get("client_name", "Unknown"),
            "category": session_item.get("category", "Unknown"),
            "date_created": session_item.get("date_created", "Unknown")
        }

        # Prova a estrarre nome sessione dal context
        session_name = test_id  # default
        try:
            context_str = session_item.get("context", "{}")
            if isinstance(context_str, str):
                context_dict = json.loads(context_str)
                session_name = context_dict.get("goal", test_id)
            elif isinstance(context_str, dict):
                session_name = context_str.get("goal", test_id)
        except:
            pass

        session_details["session_name"] = session_name

        preview_data = {
            "session_details": session_details,
            "deletion_impact": {
                "versions_count": versions_count,
                "messages_count": messages_count,
                "main_session": True,
                "total_items": 1 + versions_count + messages_count
            },
            "preview_generated_at": datetime.utcnow().isoformat() + "Z"
        }

        print(f"Deletion preview generated: {preview_data['deletion_impact']}")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(preview_data)
        }

    except Exception as e:
        print(f"Error in get_session_deletion_preview_handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error generating deletion preview",
                "details": str(e)
            })
        }

def create_session_handler(event, context):
    import traceback
    try:
        print("=== EVENT ===")
        print(json.dumps(event))
        print("=== BODY ===")
        print(event.get("body"))

        body = json.loads(event.get("body", "{}"))

        pt_type = body.get("pt_type", "webapp")
        pt_type_map = {
            "webapp": "webapplication",
            "infra": "infrastructure",
            "mobile": "mobileapp"
        }
        resolved_pt_type = pt_type_map.get(pt_type, pt_type)

        goal = body.get("goal", "")
        client_id = body.get("client_id", "")
        client_name = body.get("client_name", "")

        print("AUTHORIZER FULL:", json.dumps(event.get("requestContext", {}).get("authorizer", {})))

        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        print("CLAIMS KEYS:", list(claims.keys()))
        user_email = claims.get("email")
        user_id = claims.get("sub")

        if not user_email:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Email utente non trovata nel token JWT"})
            }

        if not goal:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing goal (session name)"})
            }

        org_id = f"ORG-{user_id[:8]}"

        test_id = f"PT-SESSION-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.utcnow().isoformat() + "Z"

        try:
            checklist = load_checklist_from_s3(resolved_pt_type)
        except Exception as e:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Checklist non trovata per tipo '{pt_type}'", "details": str(e)})
            }

        current_phase_id = checklist[0]["phase_id"] if checklist else None

        context_dict = {
            "test_id": test_id,
            "org_id": org_id,                     # aggiunto
            "assigned_to": user_id,               # aggiunto
            "created_by": user_id,                # aggiunto
            "pt_type": pt_type,
            "goal": goal,
            "client_id": client_id,
            "client_name": client_name,
            "scope": {"targets": []},
            "credentials": {},
            "checklist": checklist,
            "current_phase_id": current_phase_id,
            "findings": [],
            "evidence": [],
            "meta": {
                "created_at": now_iso,
                "updated_at": now_iso,
                "timestamp": now_iso,
                "version": "1.0",
                "updated_by": "create_session_handler",
                "source": "lambda"
            }
        }

        # Log sets in context_dict before serialization for DynamoDB
        if log_sets_in_obj(context_dict, path="create_session_handler.context_dict_for_dynamo_context_json"):
            print(
                "‼️ ATTENZIONE (create_session_handler): Trovato almeno un set in 'context_dict' destinato a context_json per DynamoDB! Vedi log sopra.")

        try:
            # Ensure context_dict is serializable (sets and decimals handled) before creating context_json
            context_json = json.dumps(sets_to_lists(convert_decimal(context_dict)))
        except Exception as e:
            return {
                "statusCode": 500,  # Internal error during serialization
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Context serializzazione fallita (pre-DynamoDB)", "details": str(e)})
            }

        item = {
            "test_id": test_id,
            "context": context_json,
            "user_email": user_email,
            "user_id": user_id,
            "client_id": client_id,
            "client_name": client_name,
            "category": pt_type,
            "date_created": now_iso,
            "date_updated": now_iso,
            "version": 1,
            "org_id": org_id,
            "assigned_to": user_id
        }

        print("SALVO SU DYNAMO:", {k: (v[:200] + '...' if isinstance(v, str) and len(v) > 200 else v) for k, v in
                                   item.items()})
        table.put_item(Item=item)

        response_payload = {
            "message": "Sessione creata",
            "test_id": test_id,
            "context": context_dict
        }

        if log_sets_in_obj(response_payload, path="create_session_handler.response_payload"):
            print(
                "‼️ ATTENZIONE (create_session_handler): Trovato almeno un set in 'response_payload' prima della serializzazione della risposta! Vedi log sopra.")

        return {
            "statusCode": 201,
            "headers": CORS_HEADERS,
            "body": json.dumps(sets_to_lists(convert_decimal(response_payload)))
        }

    except Exception as e:
        print("TRACEBACK:", traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Errore durante la creazione della sessione",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def get_sessions_by_user_handler(event, context):
    """Handler per recuperare le sessioni di un utente specifico"""
    try:
        # Debug completo dell'evento
        print("=== GET SESSIONS BY USER DEBUG ===")
        print("Full event:", json.dumps(event, default=str))

        # Estrai claims dal JWT
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        user_email = claims.get("email")
        user_id = claims.get("sub")

        print(f"Extracted user_email: {user_email}")
        print(f"Extracted user_id: {user_id}")
        print("All authorizer claims:", json.dumps(claims, default=str))

        # Validazione autenticazione
        if not user_email:
            print("ERROR: Email utente non trovata nel token JWT")
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Email utente non trovata nel token JWT"})
            }

        # Query DynamoDB con error handling robusto
        print(f"Querying DynamoDB table '{table.table_name}' with GSI 'user_email-index'")

        try:
            # FALLBACK: usa assigned_to-index con user_id invece di user_email-index
            print("Using assigned_to-index as fallback")
            response = table.query(
                IndexName='assigned_to-index',
                KeyConditionExpression=Key('assigned_to').eq(user_id)
            )
            print(f"DynamoDB query successful with assigned_to-index. Items count: {len(response.get('Items', []))}")

            # Se non trova nulla con user_id, prova con user_email
            if not response.get('Items'):
                print("No items found with user_id, trying with user_email")
                response = table.query(
                    IndexName='assigned_to-index',
                    KeyConditionExpression=Key('assigned_to').eq(user_email)
                )
                print(f"Retry with user_email found: {len(response.get('Items', []))}")

        except Exception as dynamodb_error:
            print(f"DynamoDB query failed: {str(dynamodb_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "error": "Errore nella query del database",
                    "details": str(dynamodb_error),
                    "hint": "Verifica che la GSI 'user_email-index' esista e sia attiva"
                })
            }

        # Processamento risultati
        items = response.get("Items", [])
        parsed_items = []

        for item_db in items:
            try:
                # Estrai i dati base
                test_id = item_db.get("test_id", "unknown")
                user_email_db = item_db.get("user_email", "unknown")
                context_raw = item_db.get("context")

                print(f"Processing session {test_id}, context type: {type(context_raw)}")

                # Parsing sicuro del context
                context_obj = {}
                if isinstance(context_raw, str):
                    try:
                        context_obj = json.loads(context_raw)
                        print(f"Successfully parsed JSON context for {test_id}")
                    except json.JSONDecodeError as parse_error:
                        print(f"JSON parsing failed for {test_id}: {str(parse_error)}")
                        context_obj = {"error": "Invalid JSON format", "raw": context_raw[:100]}
                elif isinstance(context_raw, dict):
                    context_obj = context_raw
                    print(f"Context already dict for {test_id}")
                else:
                    print(f"Unexpected context type for {test_id}: {type(context_raw)}")
                    context_obj = {"error": "Unexpected context type", "type": str(type(context_raw))}

                # Costruisci item finale
                parsed_item = {
                    "id": test_id,
                    "context": context_obj,
                    "user_email": user_email_db,
                    "raw_item_keys": list(item_db.keys())  # Debug info
                }

                parsed_items.append(parsed_item)
                print(f"Successfully processed session {test_id}")

            except Exception as item_error:
                print(f"Error processing item {item_db.get('test_id', 'unknown')}: {str(item_error)}")
                # Continua con gli altri item invece di fallire completamente
                continue

        print(f"Successfully processed {len(parsed_items)} sessions out of {len(items)} total")

        # Risposta finale con debug info
        response_data = {
            "sessions": parsed_items,
            "debug_info": {
                "user_email": user_email,
                "total_items_found": len(items),
                "successfully_parsed": len(parsed_items),
                "table_name": table.table_name,
                "gsi_used": "user_email-index"
            }
        }

        return json_response(response_data)

    except Exception as e:
        # Error handling completo
        error_details = {
            "error": "Errore durante il recupero delle sessioni",
            "details": str(e),
            "trace": traceback.format_exc(),
            "event_summary": {
                "method": event.get("httpMethod", "unknown"),
                "path": event.get("path", "unknown"),
                "has_auth": bool(event.get("requestContext", {}).get("authorizer", {}))
            }
        }

        print(f"FATAL ERROR in get_sessions_by_user_handler: {json.dumps(error_details, default=str)}")

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps(error_details)
        }

def process_chat_message_handler(event, context):
    os.environ["PENELOPE_NON_INTERACTIVE"] = "true"

    try:
        test_id = event.get("pathParameters", {}).get("test_id")
        body = json.loads(event.get("body", "{}"))
        user_input = body.get("user_input", "")

        if not test_id or not user_input:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Parametri test_id o user_input mancanti"})
            }

        from src.orchestrator.orchestrator import Orchestrator
        from src.db_context_manager.db_manager import DbContextManager
        from src.context_validator.context_validator import ContextValidator
        from src.llm_interfaces.clients.gemini_client import GeminiClient
        from src.llm_interfaces.user_input_interpreter_llm.user_input_interpreter_llm import UserInputInterpreterLLM
        from src.llm_interfaces.query_generator_llm.query_generator_llm import QueryGeneratorLLM
        from src.llm_interfaces.task_guidance_llm.task_guidance_llm import TaskGuidanceLLM
        from src.llm_interfaces.troubleshooting_llm.troubleshooting_llm import TroubleshootingLLM
        from src.llm_interfaces.error_classifier_llm.error_classifier_llm import ErrorClassifierLLM
        from src.db_fitness_interface.mock_fitness_retriever import MockFitnessRetriever as FitnessRetriever

        db_manager = DbContextManager()
        validator = ContextValidator(schema_path="src/context_validator/schemas/db_context_schema.json")

        gemini_client = GeminiClient()
        interpreter_llm = UserInputInterpreterLLM(llm_client=gemini_client,
                                                  prompt_templates_dir="src/llm_interfaces/user_input_interpreter_llm/prompt_templates")
        query_generator_llm = QueryGeneratorLLM(llm_client=gemini_client,
                                                prompt_templates_dir="src/llm_interfaces/query_generator_llm/prompt_templates")
        task_guidance_llm = TaskGuidanceLLM(llm_client=gemini_client, retriever=FitnessRetriever(),
                                            prompt_template_path="src/llm_interfaces/task_guidance_llm/prompt_templates/task_guidance.txt")
        troubleshooting_llm = TroubleshootingLLM(gemini_client,
                                                 prompt_template_path="src/llm_interfaces/troubleshooting_llm/prompt_templates/troubleshoot_command_issue.txt")
        error_classifier_llm = ErrorClassifierLLM(gemini_client,
                                                  prompt_template_path="src/llm_interfaces/error_classifier_llm/prompt_templates/classify_error_detection.txt")

        orchestrator = Orchestrator(
            db_manager=db_manager,
            validator=validator,
            interpreter=interpreter_llm,
            query_generator_llm=query_generator_llm,
            task_guidance_llm=task_guidance_llm,
            troubleshooter_llm=troubleshooting_llm,
            error_classifier_llm=error_classifier_llm,
            client=gemini_client
        )

        result_context = orchestrator.process_single_input(test_id, user_input)

        if log_sets_in_obj(result_context, path="process_chat_message_handler.result_context"):
            print(
                "‼️ ATTENZIONE (process_chat_message_handler): trovato almeno un set in result_context dall'orchestrator! Vedi log sopra.")

        if not result_context or not isinstance(result_context, dict):
            result_context = {
                "last_output": {
                    "guidance_markdown": "⚠️ Nessuna risposta generata o formato non valido. Controlla i log Lambda."
                }
            }

        if result_context and isinstance(result_context, dict):
            # Carica la sessione attuale
            response = table.get_item(Key={"test_id": test_id})
            item = response.get("Item")
            if item:
                old_version = item.get("version", 1)
                table.update_item(
                    Key={"test_id": test_id},
                    UpdateExpression="SET #ctx = :c, date_updated = :d, version = :v",
                    ExpressionAttributeNames={"#ctx": "context"},
                    ExpressionAttributeValues={
                        ":c": json.dumps(sets_to_lists(convert_decimal(result_context))),
                        ":d": datetime.utcnow().isoformat() + "Z",
                        ":v": old_version + 1
                    }
                )

        # Estrai token usage dal result_context se presente (skip o troubleshooting)
        token_usage = result_context.get("token_usage")

        # Se non presente nel result, prova a prenderlo dal client
        if not token_usage and hasattr(orchestrator.client, 'get_token_usage'):
            token_usage = orchestrator.client.get_token_usage()

        # Prepara la risposta
        response_body = {
            "test_id": test_id,
            "last_output": result_context.get("last_output", {}),
            "context_version": result_context.get("version", 0)
        }

        # Aggiungi token usage se disponibile
        if token_usage:
            response_body["token_usage"] = token_usage

        return json_response(response_body)

    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Errore durante l'elaborazione del messaggio",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def update_checklist_handler(event, context):
    import traceback  # For the except block

    test_id = event.get("pathParameters", {}).get("test_id")
    if not test_id:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "test_id mancante in pathParameters"})
        }
    try:
        body = json.loads(event.get("body", "{}"))
        updates = body.get("updates", [])
        if not isinstance(updates, list) or not updates:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "updates mancante o non valido nel body"})
            }

        response = table.get_item(Key={"test_id": test_id})
        item = response.get("Item")
        if not item:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Contesto non trovato per test_id: {test_id}"})
            }

        current_context_str = item["context"]
        context_dict = json.loads(current_context_str) if isinstance(current_context_str, str) else current_context_str
        # Ensure context_dict is a dict after parsing
        if not isinstance(context_dict, dict):
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Formato contesto non valido per test_id: {test_id}"})
            }

        old_version = item.get("version", 1)
        # old_context is context_dict before modifications. For versioning, it should be the state *before* this update.
        # The item["context"] is the string version, which is fine for Dynamo, but for logging sets, use the parsed dict.
        old_context_for_versioning = json.loads(current_context_str) if isinstance(current_context_str,
                                                                                   str) else current_context_str
        if not isinstance(old_context_for_versioning, dict):  # defensive check
            old_context_for_versioning = {}

        # Log sets in old_context_for_versioning before saving to versions_table
        if log_sets_in_obj(old_context_for_versioning, path="update_checklist_handler.old_context_for_versioning"):
            print(
                "‼️ ATTENZIONE (update_checklist_handler): Trovato almeno un set in 'old_context_for_versioning' prima del salvataggio della versione (pre-conversione)! Vedi log sopra.")

        versions_table.put_item(Item={
            "test_id": test_id,
            "version": old_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "context": json.dumps(sets_to_lists(convert_decimal(old_context_for_versioning)))
        })

        updated_flag = False  # Renamed to avoid conflict with 'updated' from loop
        for update_item in updates:  # Renamed to avoid conflict
            check_id = update_item.get("check_id")
            for phase in context_dict.get("checklist", []):
                for task in phase.get("tasks", []):
                    for check in task.get("checks", []):
                        if check["check_id"] == check_id:
                            if "state" in update_item:
                                check["state"] = update_item["state"]
                            if "notes" in update_item:
                                check["notes"] = update_item["notes"]
                            check["timestamp"] = update_item.get("timestamp") or datetime.utcnow().isoformat() + "Z"
                            updated_flag = True
        if not updated_flag:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                                       "message": "Nessun check corrispondente trovato per l'aggiornamento o nessun dato da aggiornare fornito."})
            }

        # Log sets in the modified context_dict before updating the main table
        if log_sets_in_obj(context_dict, path="update_checklist_handler.context_dict_for_update_item"):
            print(
                "‼️ ATTENZIONE (update_checklist_handler): Trovato almeno un set in 'context_dict' (modificato) prima dell'update_item (pre-conversione)! Vedi log sopra.")

        table.update_item(
            Key={"test_id": test_id},
            UpdateExpression="SET #ctx = :c, date_updated = :d, version = :v",
            ExpressionAttributeNames={
                "#ctx": "context"
            },
            ExpressionAttributeValues={
                ":c": json.dumps(sets_to_lists(convert_decimal(context_dict))),
                ":d": datetime.utcnow().isoformat() + "Z",
                ":v": old_version + 1
            }
        )

        # json_response will call log_sets_in_obj on its input
        return json_response({"message": "Checklist aggiornata", "context": context_dict})

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Errore durante l'aggiornamento della checklist",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def update_session_name_handler(event, context):
    import traceback

    test_id = event.get("pathParameters", {}).get("test_id")
    if not test_id:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "test_id mancante"})
        }

    try:
        body = json.loads(event.get("body", "{}"))
        new_goal = body.get("goal")

        if not new_goal:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "goal mancante"})
            }

        response = table.get_item(Key={"test_id": test_id})
        item = response.get("Item")
        if not item:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Sessione {test_id} non trovata"})
            }

        context_str = item.get("context", "{}")
        context_dict = json.loads(context_str) if isinstance(context_str, str) else context_str
        if not isinstance(context_dict, dict):
            context_dict = {}

        old_version = item.get("version", 1)

        # Salva la versione precedente
        versions_table.put_item(Item={
            "test_id": test_id,
            "version": old_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "context": json.dumps(sets_to_lists(convert_decimal(context_dict)))
        })

        # Aggiorna il goal nel contesto
        context_dict["goal"] = new_goal

        table.update_item(
            Key={"test_id": test_id},
            UpdateExpression="SET #ctx=:c, date_updated=:d, version=:v, goal=:g",
            ExpressionAttributeNames={"#ctx": "context"},
            ExpressionAttributeValues={
                ":c": json.dumps(sets_to_lists(convert_decimal(context_dict))),
                ":d": datetime.utcnow().isoformat() + "Z",
                ":v": old_version + 1,
                ":g": new_goal
            }
        )

        return json_response({"message": "Sessione rinominata", "context": context_dict})

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Errore durante l'aggiornamento del nome della sessione",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def add_message_handler(event, context):
    import json, uuid
    from datetime import datetime
    ddb = boto3.resource("dynamodb")
    table = ddb.Table("PentestMessages")

    test_id = event.get("pathParameters", {}).get("test_id")
    body = json.loads(event.get("body", "{}"))

    # Autenticazione utente (optional)
    user_id = event.get("requestContext", {}).get("authorizer", {}).get("claims", {}).get("sub")
    user_email = event.get("requestContext", {}).get("authorizer", {}).get("claims", {}).get("email")

    item = {
        "test_id": test_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message_id": str(uuid.uuid4()),
        "from": body.get("from"),   # "user" / "assistant" / "system"
        "text": body.get("text"),
        "check_id": body.get("check_id"),       # opzionale
        "msg_type": body.get("msg_type", "chat"),
        "user_id": user_id,
        "user_email": user_email,
    }
    table.put_item(Item=item)
    return {
        "statusCode": 201,
        "headers": CORS_HEADERS,
        "body": json.dumps({"message": "added", "item": item}),
    }

def list_messages_handler(event, context):
    import json
    from boto3.dynamodb.conditions import Key
    ddb = boto3.resource("dynamodb")
    table = ddb.Table("PentestMessages")

    test_id = event.get("pathParameters", {}).get("test_id")
    limit = int(event.get("queryStringParameters", {}).get("limit", 50))
    last_evaluated_key = event.get("queryStringParameters", {}).get("lastKey")

    query_args = {
        "KeyConditionExpression": Key("test_id").eq(test_id),
        "Limit": limit,
        "ScanIndexForward": True  # True = ordine crescente di timestamp
    }
    if last_evaluated_key:
        query_args["ExclusiveStartKey"] = json.loads(last_evaluated_key)
    response = table.query(**query_args)
    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "messages": response["Items"],
            "lastKey": response.get("LastEvaluatedKey"),
        }),
    }

def create_client_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        # Richiedi sempre autenticazione
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        owner_user_id = claims.get("sub")
        created_by_email = claims.get("email")
        if not owner_user_id:
            return {
                "statusCode": 401,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Authentication required"})
            }
        client_id = f"CLIENT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.utcnow().isoformat() + "Z"
        item = {
            "client_id": client_id,
            "owner_user_id": owner_user_id,
            "created_by_email": created_by_email,
            "name": body.get("name", ""),
            "logoUrl": body.get("logoUrl", ""),
            "contactPerson": body.get("contactPerson", ""),
            "contactEmail": body.get("contactEmail", ""),
            "companyAddress": body.get("companyAddress", ""),
            "companyWebsite": body.get("companyWebsite", ""),
            "industry": body.get("industry", ""),
            "notes": body.get("notes", ""),
            "tenant_id": body.get("tenant_id", owner_user_id),  # Pronto per multi-tenant
            "created_at": now,
            "updated_at": now,
        }
        clients_table.put_item(Item=item)
        return {
            "statusCode": 201,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Client created", "client": item})
        }
    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error creating client",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def get_clients_handler(event, context):
    try:
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        owner_user_id = claims.get("sub")
        if not owner_user_id:
            return {
                "statusCode": 401,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Authentication required"})
            }
        response = clients_table.query(
            IndexName="owner_user_id-index",  # Assicurati di avere una GSI su owner_user_id!
            KeyConditionExpression=boto3.dynamodb.conditions.Key('owner_user_id').eq(owner_user_id)
        )
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"clients": response.get("Items", [])})
        }
    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error fetching clients",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def update_client_handler(event, context):
    try:
        client_id = event.get("pathParameters", {}).get("client_id")
        if not client_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing client_id in path"})
            }
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        owner_user_id = claims.get("sub")
        if not owner_user_id:
            return {
                "statusCode": 401,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Authentication required"})
            }
        body = json.loads(event.get("body", "{}"))
        update_expr = "SET " + ", ".join([f"{k} = :{k}" for k in body.keys()])
        expr_attrs = {f":{k}": v for k, v in body.items()}
        expr_attrs[":updated_at"] = datetime.utcnow().isoformat() + "Z"
        update_expr += ", updated_at = :updated_at"
        clients_table.update_item(
            Key={"client_id": client_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attrs
        )
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Client updated"})
        }
    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error updating client",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def delete_client_handler(event, context):
    import traceback
    try:
        print("=== DELETE CLIENT WITH CASCADE EVENT (OPTIMIZED) ===")
        print(json.dumps(event, default=str))

        client_id = event.get("pathParameters", {}).get("client_id")
        if not client_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing client_id in path"})
            }

        print(f"Attempting to delete client and all associated data: {client_id}")

        # Verifica autenticazione
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        owner_user_id = claims.get("sub")

        deleted_sessions = []
        deleted_messages_count = 0
        deleted_versions_count = 0

        if owner_user_id:
            print(f"Authenticated user: {owner_user_id}")

            # Verifica che il client esista e appartenga all'utente
            response = clients_table.get_item(Key={"client_id": client_id})
            client_item = response.get("Item")

            if not client_item:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "Client not found"})
                }

            # Verifica ownership
            if "owner_user_id" in client_item and client_item["owner_user_id"] != owner_user_id:
                return {
                    "statusCode": 403,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "Forbidden: You don't own this client"})
                }

        # STEP 1: Trova tutte le sessioni associate al client
        print(f"Finding all sessions for client: {client_id}")

        try:
            # VERSIONE OTTIMIZZATA: Usa GSI se disponibile, altrimenti fallback a Scan
            try:
                # Tenta di usare il GSI client_id-index se esiste
                sessions_response = table.query(
                    IndexName='client_id-index',
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('client_id').eq(client_id)
                )
                print("Using optimized GSI query for client_id")
            except Exception as gsi_error:
                print(f"GSI not available, falling back to Scan: {gsi_error}")
                # Fallback a Scan se il GSI non esiste ancora
                sessions_response = table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr('client_id').eq(client_id)
                )
                print("Using Scan as fallback (consider adding GSI for better performance)")

        except Exception as e:
            print(f"Error querying sessions: {str(e)}")
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "error": "Error finding associated sessions",
                    "details": str(e)
                })
            }

        associated_sessions = sessions_response.get('Items', [])
        print(f"Found {len(associated_sessions)} sessions to delete")

        # STEP 2: Elimina in batch per migliori performance
        messages_table = dynamodb.Table("ArnoldMessages")

        # Process sessions in batches per evitare timeout
        session_batch_size = 5  # Processa max 5 sessioni alla volta

        for i in range(0, len(associated_sessions), session_batch_size):
            batch = associated_sessions[i:i + session_batch_size]
            print(f"Processing session batch {i // session_batch_size + 1} ({len(batch)} sessions)")

            for session in batch:
                session_id = session['test_id']
                print(f"Processing session: {session_id}")

                try:
                    # Elimina messaggi in batch
                    messages_response = messages_table.query(
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('test_id').eq(session_id)
                    )

                    messages_to_delete = messages_response.get('Items', [])
                    print(f"Found {len(messages_to_delete)} messages to delete for session {session_id}")

                    # Batch delete ottimizzato per messaggi
                    if messages_to_delete:
                        # DynamoDB batch_writer gestisce automaticamente i batch da 25 items
                        with messages_table.batch_writer() as batch_writer:
                            for message in messages_to_delete:
                                batch_writer.delete_item(
                                    Key={
                                        'test_id': message['test_id'],
                                        'timestamp': message['timestamp']
                                    }
                                )
                                deleted_messages_count += 1

                    # Elimina versioni in batch
                    versions_response = versions_table.query(
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('test_id').eq(session_id)
                    )

                    versions_to_delete = versions_response.get('Items', [])
                    print(f"Found {len(versions_to_delete)} versions to delete for session {session_id}")

                    # Batch delete ottimizzato per versioni
                    if versions_to_delete:
                        with versions_table.batch_writer() as batch_writer:
                            for version in versions_to_delete:
                                batch_writer.delete_item(
                                    Key={
                                        'test_id': version['test_id'],
                                        'version': version['version']
                                    }
                                )
                                deleted_versions_count += 1

                    # Elimina la sessione principale
                    table.delete_item(Key={"test_id": session_id})

                    # Estrai info per il summary
                    session_context = session.get('context')
                    session_name = 'Unknown'

                    if isinstance(session_context, str):
                        try:
                            context_dict = json.loads(session_context)
                            session_name = context_dict.get('goal', 'Unknown')
                        except:
                            pass
                    elif isinstance(session_context, dict):
                        session_name = session_context.get('goal', 'Unknown')

                    deleted_sessions.append({
                        'session_id': session_id,
                        'session_name': session_name,
                        'messages_deleted': len(messages_to_delete),
                        'versions_deleted': len(versions_to_delete)
                    })

                    print(f"Successfully deleted session {session_id} with all associated data")

                except Exception as e:
                    print(f"Error deleting session {session_id}: {str(e)}")
                    # Log error ma continua con altre sessioni
                    deleted_sessions.append({
                        'session_id': session_id,
                        'session_name': 'Error during deletion',
                        'error': str(e)
                    })
                    continue

        # STEP 3: Elimina il client
        print(f"Deleting client: {client_id}")
        delete_response = clients_table.delete_item(
            Key={"client_id": client_id},
            ReturnValues="ALL_OLD"
        )

        deleted_client = delete_response.get("Attributes")

        # STEP 4: Prepara response dettagliata
        response_data = {
            "message": "Client and all associated data deleted successfully",
            "deleted_client_id": client_id,
            "deleted_client_name": deleted_client.get('name') if deleted_client else 'Unknown',
            "cascade_deletion_summary": {
                "sessions_deleted": len([s for s in deleted_sessions if 'error' not in s]),
                "sessions_with_errors": len([s for s in deleted_sessions if 'error' in s]),
                "total_messages_deleted": deleted_messages_count,
                "total_versions_deleted": deleted_versions_count,
                "session_details": deleted_sessions
            },
            "performance_info": {
                "used_optimized_gsi": 'client_id-index' in str(sessions_response),
                "total_sessions_processed": len(associated_sessions)
            }
        }

        print(f"Cascade deletion completed: {response_data['cascade_deletion_summary']}")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response_data)
        }

    except Exception as e:
        print(f"Error in delete_client_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error deleting client and associated data",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def delete_session_handler(event, context):
    import traceback
    try:
        test_id = event.get("pathParameters", {}).get("test_id")
        if not test_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing test_id in path"})
            }

        print(f"=== DELETE SESSION WITH CASCADE CLEANUP: {test_id} ===")

        # Verifica autenticazione (opzionale - dipende se vuoi proteggere questo endpoint)
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        user_email = claims.get("email")

        if user_email:
            print(f"Authenticated deletion request from: {user_email}")
        else:
            print("Anonymous deletion request")

        deleted_versions_count = 0
        deleted_messages_count = 0

        # STEP 1: Verifica che la sessione esista prima di procedere
        try:
            session_response = table.get_item(Key={"test_id": test_id})
            session_item = session_response.get("Item")

            if not session_item:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": f"Session {test_id} not found"})
                }

            print(f"Session found: {session_item.get('user_email', 'Unknown user')}")

        except Exception as e:
            print(f"Error checking session existence: {str(e)}")
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "error": "Error checking session existence",
                    "details": str(e)
                })
            }

        # STEP 2: Elimina tutte le versioni associate
        print(f"Cleaning up versions for session: {test_id}")
        try:
            # Query tutte le versioni per questa sessione
            versions_response = versions_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('test_id').eq(test_id)
            )

            versions_to_delete = versions_response.get('Items', [])
            print(f"Found {len(versions_to_delete)} versions to delete")

            if versions_to_delete:
                # Batch delete delle versioni per performance migliori
                with versions_table.batch_writer() as batch:
                    for version in versions_to_delete:
                        batch.delete_item(
                            Key={
                                'test_id': version['test_id'],
                                'version': version['version']
                            }
                        )
                        deleted_versions_count += 1

                print(f"Successfully deleted {deleted_versions_count} versions")

        except Exception as e:
            print(f"Error deleting versions: {str(e)}")
            # Non blocchiamo la cancellazione della sessione se fallisce la pulizia versioni
            # ma logghiamo l'errore
            print(f"WARNING: Failed to clean up versions, continuing with session deletion")

        # STEP 3: Elimina messaggi associati (se esistono)
        print(f"Cleaning up messages for session: {test_id}")
        try:
            messages_table = dynamodb.Table("ArnoldMessages")

            # Query tutti i messaggi per questa sessione
            messages_response = messages_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('test_id').eq(test_id)
            )

            messages_to_delete = messages_response.get('Items', [])
            print(f"Found {len(messages_to_delete)} messages to delete")

            if messages_to_delete:
                # Batch delete dei messaggi
                with messages_table.batch_writer() as batch:
                    for message in messages_to_delete:
                        batch.delete_item(
                            Key={
                                'test_id': message['test_id'],
                                'timestamp': message['timestamp']
                            }
                        )
                        deleted_messages_count += 1

                print(f"Successfully deleted {deleted_messages_count} messages")

        except Exception as e:
            print(f"Error deleting messages: {str(e)}")
            # Anche qui, non blocchiamo ma logghiamo
            print(f"WARNING: Failed to clean up messages, continuing with session deletion")

        # STEP 4: Elimina la sessione principale
        print(f"Deleting main session: {test_id}")
        try:
            delete_response = table.delete_item(
                Key={"test_id": test_id},
                ReturnValues="ALL_OLD"
            )

            deleted_session = delete_response.get("Attributes")
            session_name = "Unknown"

            if deleted_session:
                # Prova a estrarre il nome della sessione
                context_str = deleted_session.get("context", "{}")
                try:
                    if isinstance(context_str, str):
                        context_dict = json.loads(context_str)
                        session_name = context_dict.get("goal", "Unknown")
                    elif isinstance(context_str, dict):
                        session_name = context_str.get("goal", "Unknown")
                except:
                    pass

            print(f"Successfully deleted main session: {test_id} ({session_name})")

        except Exception as e:
            print(f"Error deleting main session: {str(e)}")
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "error": "Error deleting main session",
                    "details": str(e)
                })
            }

        # STEP 5: Prepara response dettagliata
        response_data = {
            "message": "Session and all associated data deleted successfully",
            "deleted_session_id": test_id,
            "deleted_session_name": session_name,
            "cleanup_summary": {
                "versions_deleted": deleted_versions_count,
                "messages_deleted": deleted_messages_count,
                "main_session_deleted": True
            },
            "deleted_by": user_email if user_email else "anonymous"
        }

        print(f"Cascade deletion completed successfully: {response_data['cleanup_summary']}")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response_data)
        }

    except Exception as e:
        print(f"Unexpected error in delete_session_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Unexpected error during session deletion",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }


def get_all_sessions_handler(event, context):
    """Handler per Team Leader - recupera tutte le sessioni con statistiche complete - VERSIONE FISSATA"""
    try:
        # Verifica che l'utente sia autenticato
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        user_email = claims.get("email")
        user_id = claims.get("sub")

        print(f"Team leader access attempt by: {user_email} (ID: {user_id})")

        # RIMUOVI LA RESTRIZIONE HARD-CODED - permetti a qualsiasi utente autenticato
        # In futuro, implementa un sistema di ruoli dal database
        if not user_email or not user_id:
            return {
                "statusCode": 401,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "error": "Unauthorized. Authentication required.",
                    "user_email": user_email
                })
            }

        print("=== TEAM LEADER DASHBOARD: FETCHING ALL SESSIONS ===")

        # FALLBACK SICURO - Se il scan principale fallisce, usa query per org
        sessions = []
        try:
            # Prova prima un scan completo
            response = table.scan()
            sessions = response.get("Items", [])
            print(f"Found {len(sessions)} sessions via scan")
        except Exception as scan_error:
            print(f"Scan failed, trying organization-based query: {scan_error}")
            # Fallback: cerca sessioni per organizzazione dell'utente
            try:
                org_id = f"ORG-{user_id[:8]}"
                response = table.query(
                    IndexName='org_id-index',
                    KeyConditionExpression=Key("org_id").eq(org_id)
                )
                sessions = response.get("Items", [])
                print(f"Found {len(sessions)} sessions via org query")
            except Exception as org_error:
                print(f"Organization query also failed: {org_error}")
                # Ultimo fallback: sessioni assegnate all'utente
                try:
                    response = table.query(
                        IndexName='assigned_to-index',
                        KeyConditionExpression=Key("assigned_to").eq(user_id)
                    )
                    sessions = response.get("Items", [])
                    print(f"Found {len(sessions)} sessions via assigned_to query")
                except Exception as assigned_error:
                    print(f"All queries failed: {assigned_error}")
                    sessions = []

        if not sessions:
            print("No sessions found, returning empty result")
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "sessions": [],
                    "total_count": 0,
                    "global_findings": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
                    "dashboard_stats": {"total_sessions": 0, "active_sessions": 0, "completed_sessions": 0,
                                        "in_progress_sessions": 0, "critical_findings": 0},
                    "generated_at": datetime.utcnow().isoformat() + "Z"
                })
            }

        # Arricchisci ogni sessione con statistiche dettagliate
        enriched_sessions = []
        total_findings = {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}

        for session in sessions:
            test_id = session.get("test_id")
            print(f"Processing session: {test_id}")

            # Conta messaggi per questa sessione (con error handling)
            message_count = 0
            messages = []
            try:
                messages_response = messages_table.query(
                    KeyConditionExpression=Key("test_id").eq(test_id)
                )
                message_count = messages_response.get("Count", 0)
                messages = messages_response.get("Items", [])
            except Exception as e:
                print(f"Warning: Could not count messages for {test_id}: {str(e)}")
                message_count = 0
                messages = []

            # Parsing context con error handling migliorato
            context_raw = session.get("context", "{}")
            context_obj = {}
            try:
                if isinstance(context_raw, str):
                    context_obj = json.loads(context_raw)
                else:
                    context_obj = context_raw or {}
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Invalid context for session {test_id}: {str(e)}")
                context_obj = {}

            # Calcola findings per questa sessione (con fallback sicuro)
            try:
                session_findings = calculate_session_findings(context_obj)
                for key in total_findings.keys():
                    total_findings[key] += session_findings[key]
            except Exception as e:
                print(f"Warning: Could not calculate findings for {test_id}: {str(e)}")
                session_findings = {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}

            # Calcola progresso sessione (con fallback sicuro)
            try:
                progress = calculate_session_progress(context_obj.get("checklist", {}))
            except Exception as e:
                print(f"Warning: Could not calculate progress for {test_id}: {str(e)}")
                progress = 0

            # Determina status sessione
            if progress >= 99:
                status = "completed"
            elif message_count > 0 and progress > 0:
                status = "active"
            elif progress > 0:
                status = "paused"
            else:
                status = "idle"

            # Estrai informazioni di base con fallback sicuri
            session_client_name = (
                    session.get("client_name") or
                    context_obj.get("client_name") or
                    f"Client-{test_id[:8]}"
            )

            session_client_id = (
                    session.get("client_id") or
                    context_obj.get("client_id") or
                    "unknown"
            )

            session_category = (
                    session.get("category") or
                    context_obj.get("pt_type") or
                    "webapp"
            )

            session_created_at = (
                    session.get("date_created") or
                    session.get("created_at") or
                    context_obj.get("meta", {}).get("created_at") or
                    datetime.utcnow().isoformat() + "Z"
            )

            session_user_email = (
                    session.get("user_email") or
                    claims.get("email") or
                    "unknown@unknown.com"
            )

            current_tester = (
                    session.get("assigned_to") or
                    session.get("user_id") or
                    user_id
            )

            # Determina il nome della sessione
            session_name = (
                    context_obj.get("session_name") or
                    context_obj.get("goal") or
                    session.get("session_name") or
                    f"Session {test_id[:8]}"
            )

            # Gestisci le date con fallback
            last_activity_date = session_created_at
            if messages:
                try:
                    sorted_messages = sorted(messages, key=lambda x: x.get("timestamp", ""), reverse=True)
                    if sorted_messages:
                        last_activity_date = sorted_messages[0].get("timestamp", session_created_at)
                except Exception as e:
                    print(f"Warning: Could not sort messages for {test_id}: {str(e)}")

            # Migliora la categoria per display
            display_category_map = {
                "webapp": "Web Application",
                "mobile": "Mobile App",
                "infra": "Infrastructure",
                "desktop": "Desktop App"
            }
            display_category = display_category_map.get(session_category, session_category.title())

            print(
                f"Session {test_id} processed - client: {session_client_name}, tester: {current_tester}, category: {display_category}")

            enriched_session = {
                "test_id": test_id,
                "session_name": session_name,
                "client_name": session_client_name,
                "client_id": session_client_id,
                "category": display_category,
                "created_at": session_created_at,
                "last_activity": last_activity_date,
                "status": status,
                "progress": progress,
                "current_tester": current_tester,
                "tester_email": session_user_email,  # Mostra l'email del creatore
                "user_email": session_user_email,
                "assigned_to": current_tester,
                "message_count": message_count,
                "findings": session_findings,
                "context": context_obj
            }

            enriched_sessions.append(enriched_session)

        # Ordina per ultima attività (più recenti prima)
        try:
            enriched_sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        except Exception as e:
            print(f"Warning: Could not sort sessions: {str(e)}")

        # Calcola statistiche globali per il dashboard
        total_sessions = len(enriched_sessions)
        active_sessions = len([s for s in enriched_sessions if s["status"] == "active"])
        completed_sessions = len([s for s in enriched_sessions if s["status"] == "completed"])
        in_progress_sessions = len([s for s in enriched_sessions if s["progress"] > 0 and s["progress"] < 100])

        dashboard_stats = {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "in_progress_sessions": in_progress_sessions,
            "critical_findings": total_findings["critical"] + total_findings["high"]
        }

        print(f"Dashboard stats calculated: {dashboard_stats}")
        print(f"Total findings breakdown: {total_findings}")

        response_data = {
            "sessions": enriched_sessions,
            "total_count": len(enriched_sessions),
            "global_findings": total_findings,
            "dashboard_stats": dashboard_stats,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response_data, default=str)
        }

    except Exception as e:
        print(f"Error in get_all_sessions_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error fetching all sessions",
                "details": str(e),
                "trace": traceback.format_exc()
            })
        }

def reassign_session_handler(event, context):
    """Permette al Team Leader di riassegnare una sessione a un altro tester"""
    try:
        test_id = event.get("pathParameters", {}).get("test_id")
        body = json.loads(event.get("body", "{}"))
        new_tester_email = body.get("new_tester_email")

        # Verifica autorizzazione team leader
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        user_email = claims.get("email")

        if user_email != "teamleader@demo.penelope.com":
            return {
                "statusCode": 403,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Only Team Leader can reassign sessions"})
            }

        # Aggiorna il context della sessione
        response = table.get_item(Key={"test_id": test_id})
        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Session not found"})
            }

        # Aggiungi messaggio di sistema nel log chat
        system_message = {
            "test_id": test_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_id": str(uuid.uuid4()),
            "from": "system",
            "text": f"Session reassigned from {response['Item'].get('user_email', 'unknown')} to {new_tester_email} by Team Leader",
            "msg_type": "system"
        }
        messages_table.put_item(Item=system_message)

        # Aggiorna proprietario sessione
        table.update_item(
            Key={"test_id": test_id},
            UpdateExpression="SET user_email = :email, updated_at = :now",
            ExpressionAttributeValues={
                ":email": new_tester_email,
                ":now": datetime.utcnow().isoformat() + "Z"
            }
        )

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": "Session reassigned successfully",
                "new_tester": new_tester_email
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Error reassigning session",
                "details": str(e)
            })
        }

def create_organization_handler(event, context):
    """Crea una nuova organizzazione"""
    try:
        body = json.loads(event.get("body", "{}"))
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        creator_id = claims.get("sub")
        creator_email = claims.get("email")

        org_id = f"ORG-{uuid.uuid4().hex[:8].upper()}"

        # Crea organizzazione
        org_item = {
            "org_id": org_id,
            "name": body.get("name"),
            "created_by": creator_id,
            "created_by_email": creator_email,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "settings": {
                "allow_member_create_sessions": body.get("allow_member_create_sessions", True),
                "require_approval": body.get("require_approval", False)
            }
        }

        orgs_table.put_item(Item=org_item)

        # Aggiungi il creatore come admin
        member_item = {
            "org_id": org_id,
            "user_id": creator_id,
            "user_email": creator_email,
            "role": "admin",  # admin, team_leader, tester
            "joined_at": datetime.utcnow().isoformat() + "Z"
        }

        members_table.put_item(Item=member_item)

        return {
            "statusCode": 201,
            "headers": CORS_HEADERS,
            "body": json.dumps({"org": org_item, "message": "Organization created"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }

def add_member_to_organization_handler(event, context):
    """Team Leader aggiunge membri all'organizzazione"""
    try:
        body = json.loads(event.get("body", "{}"))
        org_id = event.get("pathParameters", {}).get("org_id")

        # Verifica che chi fa la richiesta sia admin/team_leader
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        requester_id = claims.get("sub")

        # Check permessi
        requester_membership = members_table.get_item(
            Key={"org_id": org_id, "user_id": requester_id}
        )

        if not requester_membership.get("Item") or requester_membership["Item"]["role"] not in ["admin", "team_leader"]:
            return {
                "statusCode": 403,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Not authorized to add members"})
            }

        # Aggiungi nuovo membro
        member_item = {
            "org_id": org_id,
            "user_id": body.get("user_id"),
            "user_email": body.get("user_email"),
            "role": body.get("role", "tester"),
            "joined_at": datetime.utcnow().isoformat() + "Z"
        }

        members_table.put_item(Item=member_item)

        return {
            "statusCode": 201,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Member added successfully"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }

def get_organization_sessions_handler(event, context):
    """Ottieni tutte le sessioni dell'organizzazione (per Team Leader)"""
    try:
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        user_id = claims.get("sub")

        # Trova l'organizzazione dell'utente
        user_orgs = members_table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key("user_id").eq(user_id)
        )

        if not user_orgs.get("Items"):
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "User not in any organization"})
            }

        # Per ora prendiamo la prima org (in futuro supportare multi-org)
        org_id = user_orgs["Items"][0]["org_id"]
        user_role = user_orgs["Items"][0]["role"]

        # Se è team_leader/admin, mostra tutte le sessioni dell'org
        if user_role in ["admin", "team_leader"]:
            sessions = sessions_table.query(
                IndexName="org_id-index",
                KeyConditionExpression=Key("org_id").eq(org_id)
            )

            # Arricchisci con info sui tester
            enriched_sessions = []
            for session in sessions.get("Items", []):
                # Conta messaggi
                messages = messages_table.query(
                    KeyConditionExpression=Key("test_id").eq(session["test_id"])
                )

                enriched_session = {
                    **session,
                    "message_count": messages.get("Count", 0),
                    "assigned_to_email": get_user_email(session.get("assigned_to"))
                }
                enriched_sessions.append(enriched_session)

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"sessions": enriched_sessions})
            }
        else:
            # Tester normale: solo sessioni assegnate a lui
            sessions = sessions_table.query(
                IndexName="assigned_to-index",
                KeyConditionExpression=Key("assigned_to").eq(user_id),
                FilterExpression=Attr("org_id").eq(org_id)
            )

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"sessions": sessions.get("Items", [])})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }

def assign_session_handler(event, context):
    """Team Leader assegna/riassegna una sessione"""
    try:
        test_id = event.get("pathParameters", {}).get("test_id")
        body = json.loads(event.get("body", "{}"))
        new_assignee = body.get("assigned_to")

        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        user_id = claims.get("sub")

        # Verifica permessi (deve essere team_leader o admin)
        session = sessions_table.get_item(Key={"test_id": test_id})
        if not session.get("Item"):
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Session not found"})
            }

        org_id = session["Item"]["org_id"]

        # Verifica ruolo
        membership = members_table.get_item(
            Key={"org_id": org_id, "user_id": user_id}
        )

        if not membership.get("Item") or membership["Item"]["role"] not in ["admin", "team_leader"]:
            return {
                "statusCode": 403,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Not authorized to assign sessions"})
            }

        # Aggiorna sessione
        sessions_table.update_item(
            Key={"test_id": test_id},
            UpdateExpression="SET assigned_to = :assignee, updated_at = :now",
            ExpressionAttributeValues={
                ":assignee": new_assignee,
                ":now": datetime.utcnow().isoformat() + "Z"
            }
        )

        # Log nel sistema di messaggi
        log_message = {
            "test_id": test_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_id": str(uuid.uuid4()),
            "from": "system",
            "text": f"Session reassigned to {get_user_email(new_assignee)} by {claims.get('email')}",
            "msg_type": "system"
        }
        messages_table.put_item(Item=log_message)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Session assigned successfully"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }