#!/usr/bin/env python3
"""
Arnold Main Local - Main locale che usa ESATTAMENTE i lambda handlers AWS
Solo mock di DynamoDB e interfaccia CLI per Arnold Fitness Coach
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import io
from contextlib import redirect_stdout, redirect_stderr
import re
from colorama import init, Fore, Style

# Inizializza colorama per Windows
init()

# Imposta modalita non-interattiva per troubleshooting  
# os.environ["PENELOPE_NON_INTERACTIVE"] = "true"

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Carica env
from dotenv import load_dotenv

load_dotenv()

# Debug: mostra checklist disponibili (solo se non chiamato come modulo)
if __name__ == "__main__":
    print(f"DEBUG: PENELOPE_NON_INTERACTIVE = {os.environ.get('PENELOPE_NON_INTERACTIVE')}")
    print("Available checklists:")
    checklist_dir = Path("data/checklists")
    if checklist_dir.exists():
        for f in checklist_dir.glob("*.json"):
            print(f"  - {f.name}")
    else:
        print(f"  ERROR: Directory not found: {checklist_dir.absolute()}")
    print()
else:
    checklist_dir = Path("data/checklists")


# ===== MOCK SOLO DYNAMODB =====
class MockDynamoDBResource:
    def __init__(self):
        self.tables = {}

    def Table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = MockDynamoDBTable(table_name)
        return self.tables[table_name]


class MockDynamoDBTable:
    def __init__(self, name):
        self.name = name
        self.items = {}

    def get_item(self, Key):
        key_value = list(Key.values())[0]
        if key_value in self.items:
            item = self.items[key_value].copy()
            if "context" in item and isinstance(item["context"], dict):
                item["context"] = json.dumps(item["context"])
            return {"Item": item}
        return {}

    def put_item(self, Item):
        if "test_id" in Item:
            self.items[Item["test_id"]] = Item
        elif "client_id" in Item:
            self.items[Item["client_id"]] = Item
        return {}

    def update_item(self, **kwargs):
        key_value = list(kwargs["Key"].values())[0]
        if key_value in self.items:
            for attr, value in kwargs.get("ExpressionAttributeValues", {}).items():
                if attr == ":c":
                    self.items[key_value]["context"] = value
                elif attr == ":d":
                    self.items[key_value]["date_updated"] = value
                elif attr == ":v":
                    self.items[key_value]["version"] = value
        return {}

    def delete_item(self, Key):
        key_value = list(Key.values())[0]
        if key_value in self.items:
            del self.items[key_value]
        return {}

    def query(self, **kwargs):
        return {"Items": list(self.items.values())}


# Mock S3
class MockS3Client:
    def get_object(self, Bucket, Key):
        filename = Key.split('/')[-1]
        local_path = Path("data/checklists") / filename

        if not local_path.exists():
            local_path = Path(Key)
        if not local_path.exists():
            local_path = Path("data") / filename

        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {Key}")

        print(f"[SUCCESS] Found file at: {local_path.absolute()}")

        class MockBody:
            def __init__(self, filepath):
                self.filepath = filepath

            def read(self):
                with open(self.filepath, 'rb') as f:
                    return f.read()

            def __enter__(self):
                self._file = open(self.filepath, 'rb')
                return self._file

            def __exit__(self, *args):
                self._file.close()

        return {"Body": MockBody(str(local_path))}


# ===== TROUBLESHOOTING MOCK =====
# Override input() per evitare il blocco durante troubleshooting
import builtins

original_input = builtins.input
troubleshooting_counter = 0


def mock_input(prompt=""):
    global troubleshooting_counter

    # Se siamo nel troubleshooting e ci chiedono input utente
    if "-> Utente:" in prompt or "Utente:" in prompt:
        troubleshooting_counter += 1
        print(f"\n[AUTO] Auto-skip troubleshooting (iteration {troubleshooting_counter})")
        # Dopo 1 iterazione, skippiamo
        if troubleshooting_counter >= 1:
            troubleshooting_counter = 0  # Reset per prossima volta
            return ""  # Input vuoto forza l'uscita
        else:
            return "skip"  # Prima iterazione proviamo skip

    # Altrimenti usa input normale
    return original_input(prompt)


# Applica il mock
# builtins.input = mock_input


# ===== INTERCETTORE OUTPUT =====
class OutputInterceptor:
    def __init__(self):
        self.templates_shown = set()

    def intercept(self, func, *args, **kwargs):
        """Intercetta l'output di una funzione e filtra i print"""
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            result = func(*args, **kwargs)

        output = f.getvalue()

        # Cattura i prompt template usati
        template_matches = re.findall(r'Prompt template caricato da: (.+\.txt)', output)
        for match in template_matches:
            template_name = Path(match).name
            if template_name not in self.templates_shown:
                self.templates_shown.add(template_name)
                print(f"[TEMPLATE] Using prompt template: {template_name}")

        # Filtra output
        lines = output.split('\n')
        for line in lines:
            # Mostra solo output importanti
            if any(keyword in line for keyword in [
                '[SUCCESS]', '[ERROR]', 'QUERY GENERATA:', 'Avvio assistente troubleshooting',
                'ERROR', 'WARNING', 'Session created'
            ]):
                if 'Prompt costruito' not in line:
                    print(line)

        return result


# ===== CONTEXT DIFFER =====
class ContextDiffer:
    def __init__(self):
        self.previous_context = None

    def _extract_all_checks(self, checklist):
        """Estrae tutti i check dalla checklist in un dizionario"""
        checks = {}
        for phase in checklist:
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    checks[check["check_id"]] = check
        return checks

    def display_context_changes(self, before: dict, after: dict):
        """Display context changes in a more beautiful format"""
        changes = []

        # Check goal changes
        if before.get("goal") != after.get("goal"):
            changes.append(("GOAL", before.get("goal", "N/A"), after.get("goal", "N/A")))

        # Check checklist state changes
        before_checks = self._extract_all_checks(before.get("checklist", []))
        after_checks = self._extract_all_checks(after.get("checklist", []))

        for check_id, after_check in after_checks.items():
            before_check = before_checks.get(check_id, {})

            # State changes
            if before_check.get("state") != after_check.get("state"):
                changes.append((
                    f"CHECK {check_id}",
                    f"{before_check.get('state', 'N/A')}",
                    f"{after_check.get('state')}"
                ))

            # Notes changes
            if before_check.get("notes") != after_check.get("notes"):
                before_notes = before_check.get("notes", "")
                after_notes = after_check.get("notes", "")
                if len(after_notes) > 60:
                    after_notes = after_notes[:60] + "..."
                changes.append((f"NOTES {check_id}", before_notes or "Empty", after_notes))

        # New guidance
        if (not before.get("last_output") and after.get("last_output")) or \
                (before.get("last_output", {}).get("guidance_markdown") !=
                 after.get("last_output", {}).get("guidance_markdown")):
            changes.append(("GUIDANCE", "None", "New guidance generated"))

        if changes:
            print("\n" + "=" * 60)
            print("CONTEXT UPDATES:")
            print("=" * 60)
            for field, old_val, new_val in changes:
                if "->" in f"{old_val} -> {new_val}":
                    print(f"  {field}:")
                    print(f"    {old_val} -> {new_val}")
                else:
                    print(f"  {field}: {new_val}")
            print("=" * 60)

    def show_diff(self, new_context):
        """Mostra le differenze tra il contesto precedente e quello nuovo"""
        if self.previous_context is None:
            self.previous_context = new_context
            return

        try:
            from deepdiff import DeepDiff
            diff = DeepDiff(self.previous_context, new_context, ignore_order=True, verbose_level=2)

            if diff:
                print("\n[CONTEXT] Context Changes:")

                # Mostra solo cambiamenti importanti
                if 'values_changed' in diff:
                    for path, change in diff['values_changed'].items():
                        clean_path = path.replace("root['", "").replace("']", "").replace("['", ".")

                        if any(field in clean_path for field in ['state', 'notes', 'goal', 'targets']):
                            old_val = change.get('old_value', 'N/A')
                            new_val = change.get('new_value', 'N/A')

                            if 'state' in clean_path:
                                print(f"  [OK] State changed: {clean_path}")
                                print(f"    {old_val} -> {new_val}")
                            elif 'notes' in clean_path:
                                print(f"  [OK] Notes updated: {clean_path}")
                                if isinstance(new_val, str):
                                    print(f"    {new_val[:100]}...")
                            elif 'goal' in clean_path:
                                print(f"  [OK] Goal updated: {new_val}")
                            elif 'targets' in clean_path:
                                print(f"  [OK] Target set: {new_val}")

                # Mostra elementi aggiunti
                if 'dictionary_item_added' in diff:
                    for item in diff['dictionary_item_added']:
                        if 'last_output' in str(item):
                            print(f"  + Guidance generated")

                print()
        except ImportError:
            pass  # Se deepdiff non e installato, skip silenzioso

        self.previous_context = new_context


# ===== SOSTITUISCI BOTO3 =====
import boto3

original_resource = boto3.resource
original_client = boto3.client
mock_dynamodb = MockDynamoDBResource()


def mock_resource(service_name, *args, **kwargs):
    if service_name == 'dynamodb':
        return mock_dynamodb
    return original_resource(service_name, *args, **kwargs)


def mock_client(service_name, *args, **kwargs):
    if service_name == 's3':
        return MockS3Client()
    return original_client(service_name, *args, **kwargs)


boto3.resource = mock_resource
boto3.client = mock_client

# ===== IMPORTA HANDLERS =====
if __name__ == "__main__":
    print("[IMPORT] Importing AWS Lambda handlers...")

try:
    from backend.lambda_handlers import (
        create_session_handler,
        process_chat_message_handler,
        get_session_context_handler
    )

    if __name__ == "__main__":
        print("[SUCCESS] Lambda handlers imported successfully\n")
except Exception as e:
    if __name__ == "__main__":
        print(f"[ERROR] Error importing Lambda handlers: {e}\n")
    raise


# ===== CLI INTERFACE =====
class AWSLocalCLI:
    def __init__(self, silent=False):
        self.current_session_id = None
        self.interceptor = OutputInterceptor()
        self.differ = ContextDiffer()
        self.silent = silent

    def create_session(self, pt_type="webapp"):
        """Crea sessione usando il vero handler AWS"""
        event = {
            "body": json.dumps({
                "pt_type": pt_type,
                "goal": f"Local Test Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "client_id": "LOCAL-CLIENT",
                "client_name": "Local Test Client"
            }),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "test@local.com",
                        "sub": "local-test-user"
                    }
                }
            }
        }

        response = self.interceptor.intercept(create_session_handler, event, {})

        if response["statusCode"] == 201:
            body = json.loads(response["body"])
            self.current_session_id = body["test_id"]
            self.differ.show_diff(body.get("context", {}))
            return body["test_id"]
        else:
            raise Exception(f"Failed to create session: {response}")

    def get_test_context(self):
        """Recupera il contesto attuale per confronti"""
        if not self.current_session_id:
            return {}

        event = {
            "pathParameters": {"test_id": self.current_session_id}
        }

        response = get_session_context_handler(event, {})

        if response["statusCode"] == 200:
            body = json.loads(response["body"])
            context = body.get("context")
            if isinstance(context, str):
                context = json.loads(context)
            return context
        return {}

    def send_message(self, message: str) -> dict:
        """Send a message and get response"""
        if not self.silent:
            print(f"\n{Fore.YELLOW}[PROCESSING] Processing...{Style.RESET_ALL}")

        # Salva contesto prima
        before_context = self.get_test_context() if not self.silent else None

        # Prepare request
        request_body = {
            "test_id": self.current_session_id,
            "user_input": message
        }

        # Call the real Lambda handler
        event = {
            "pathParameters": {"test_id": self.current_session_id},
            "body": json.dumps(request_body)
        }

        try:
            response = self.interceptor.intercept(process_chat_message_handler, event, {})

            if response["statusCode"] == 200:
                body = json.loads(response["body"])

                if not self.silent:
                    # Mostra i cambiamenti del contesto
                    after_context = self.get_test_context()
                    self.differ.display_context_changes(before_context, after_context)

                    # NUOVO: Mostra info sui token se disponibili
                    if "token_usage" in body:
                        token_info = body["token_usage"]
                        print(f"\n[TOKENS] Token Usage:")

                        # Ciclo corrente
                        print(f"   === Ciclo Corrente ===")
                        print(f"   Input tokens: {token_info.get('prompt_tokens', 0):,}")
                        print(f"   Output tokens: {token_info.get('completion_tokens', 0):,}")
                        print(f"   Total tokens: {token_info.get('total_tokens', 0):,}")
                        print(f"   Costo ciclo: ${token_info.get('estimated_cost', 0):.4f}")

                        # Totale sessione
                        if 'session_total_tokens' in token_info:
                            print(f"\n   === TOTALE SESSIONE ===")
                            print(f"   Input tokens totali: {token_info.get('session_input_tokens', 0):,}")
                            print(f"   Output tokens totali: {token_info.get('session_output_tokens', 0):,}")
                            print(f"   [TOTAL] TOTAL TOKENS: {token_info.get('session_total_tokens', 0):,}")
                            print(f"   [COST] COSTO TOTALE: ${token_info.get('session_total_cost_usd', 0):.4f}")

                        # Statistiche sessione
                        if 'session_stats' in token_info:
                            stats = token_info['session_stats']
                            print(f"\n   === Statistiche Sessione ===")
                            print(f"   Durata: {stats.get('duration_minutes', 0):.1f} minuti")
                            print(f"   Token/minuto: {stats.get('average_tokens_per_minute', 0):.1f}")
                            print(f"   Costo/minuto: ${stats.get('cost_per_minute_usd', 0):.4f}")

                        # Breakdown per operazione
                        if 'operation_breakdown' in token_info:
                            print(f"\n   === Breakdown per Operazione ===")
                            breakdown = token_info['operation_breakdown']
                            for op_type, data in breakdown.items():
                                print(
                                    f"   {op_type}: {data['total_tokens']:,} tokens (${data['cost_usd']:.4f}) - {data['calls']} chiamate")

                    # Mostra la guidance
                    guidance = body.get("last_output", {}).get("guidance_markdown", "")
                    if guidance:
                        print(f"\n{Fore.GREEN}{Style.BRIGHT}")
                        print("=" * 60)
                        print("Assistant:")
                        print("=" * 60)
                        print(f"{Style.RESET_ALL}{guidance}")
                        print("=" * 60)

                return body
            else:
                raise Exception(f"Chat processing failed: {response}")

        except Exception as e:
            if not self.silent:
                print(f"\n{Fore.RED}[ERROR] Error processing message: {str(e)}{Style.RESET_ALL}")
            raise

    def get_context(self):
        """Recupera context usando il vero handler AWS"""
        if not self.current_session_id:
            return None

        event = {
            "pathParameters": {"test_id": self.current_session_id}
        }

        response = self.interceptor.intercept(get_session_context_handler, event, {})

        if response["statusCode"] == 200:
            return json.loads(response["body"])
        return None

    def get_current_context(self):
        """Alias for get_context for compatibility with clean CLI"""
        return self.get_context()

    def show_checklist_status(self):
        """Mostra lo stato attuale della checklist in modo compatto"""
        context = self.get_context()
        if not context or "context" not in context:
            print("No context available")
            return

        checklist = json.loads(context["context"]) if isinstance(context["context"], str) else context["context"]
        checklist_data = checklist.get("checklist", [])

        print("\n[CHECKLIST] Checklist Status:")
        for phase in checklist_data:
            all_checks = []
            for task in phase.get("tasks", []):
                all_checks.extend(task.get("checks", []))

            total = len(all_checks)
            done = len([c for c in all_checks if c.get("state") == "done"])
            in_progress = len([c for c in all_checks if c.get("state") == "in_progress"])

            print(f"  {phase['title']}: {done}/{total} done", end="")
            if in_progress > 0:
                print(f" ({in_progress} in progress)")
                # Mostra il check corrente
                for task in phase.get("tasks", []):
                    for check in task.get("checks", []):
                        if check.get("state") == "in_progress":
                            print(f"    -> Current: {check['check_id']} - {check['description'][:60]}...")
            else:
                print()
        print()


def format_guidance_output(guidance_markdown):
    """Formatta l'output della guidance in modo piu leggibile"""
    # Controllo di sicurezza per evitare errori con dizionari
    if not isinstance(guidance_markdown, str):
        print(f"[ERROR] format_guidance_output ricevuto {type(guidance_markdown)} invece di str")
        if isinstance(guidance_markdown, dict):
            # Prova a estrarre markdown dal dict
            guidance_markdown = guidance_markdown.get('guidance_markdown', str(guidance_markdown))
        else:
            guidance_markdown = str(guidance_markdown)
    
    lines = guidance_markdown.split('\n')
    formatted_lines = []

    for line in lines:
        # Evidenzia i comandi reali vs n/a
        if "Comando: `" in line:
            if "Comando: `n/a`" in line:
                # Sostituisci n/a con un messaggio piu chiaro
                line = line.replace("Comando: `n/a`", "Comando: [INFO] *Analisi manuale richiesta*")
            else:
                # Evidenzia i comandi veri
                line = line.replace("Comando: `", "Comando: [OK] `")
        formatted_lines.append(line)

    return '\n'.join(formatted_lines)


def main():
    """Main loop"""
    print("[START] AWS Local Tester - CLEAN VERSION")
    print("=" * 60)
    print("Using REAL AWS Lambda handlers with mocked DynamoDB")
    print("\n[INFO] Features:")
    print("  - Clean output")
    print("  - Auto-skip troubleshooting")
    print("  - Context change tracking")
    print("  - Commands: exit, context, status\n")

    cli = AWSLocalCLI()

    # Crea sessione
    print("Creating session...")
    try:
        session_id = cli.create_session()
        print(f"[SUCCESS] Session created: {session_id}")
    except Exception as e:
        print(f"[ERROR] Failed to create session: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\nType 'exit' to quit, 'context' for full context, 'status' for checklist status\n")

    while True:
        try:
            user_input = original_input("You: ").strip()

            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'context':
                context = cli.get_context()
                print("\n[CONTEXT] Current Context:")
                print(json.dumps(context, indent=2)[:1000] + "...")
                continue
            elif user_input.lower() == 'status':
                cli.show_checklist_status()
                continue

            if not user_input:
                continue

            # Processa messaggio
            try:
                result = cli.send_message(user_input)
            except Exception as e:
                print(f"\n[ERROR] Error: {e}")
                continue

        except KeyboardInterrupt:
            print("\n\n[EXIT] Bye!")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()


# Alias for compatibility with arnold_chat_clean.py
ArnoldCLI = AWSLocalCLI

if __name__ == "__main__":
    # Verifica environment
    required_env = [
        "GEMINI_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "QDRANT_COLLECTION"
    ]

    missing = [e for e in required_env if not os.getenv(e)]
    if missing:
        print(f"[ERROR] Missing environment variables: {missing}")
        print("\nRequired .env file content:")
        for env in required_env:
            print(f"{env}=your_value_here")
        sys.exit(1)

    # Verifica checklist directory
    if not checklist_dir.exists():
        print(f"[ERROR] Checklist directory not found: {checklist_dir.absolute()}")
        sys.exit(1)

    # Installa deepdiff se non presente (opzionale)
    try:
        import deepdiff
    except ImportError:
        print("[TIP] Tip: Install 'deepdiff' for better context change tracking")
        print("   pip install deepdiff\n")

    # Installa colorama se non presente
    try:
        import colorama
    except ImportError:
        print("[TIP] Tip: Install 'colorama' for colored output")
        print("   pip install colorama\n")

    try:
        main()
    except Exception as e:
        print(f"\n[FATAL] Fatal error: {e}")
        import traceback

        traceback.print_exc()