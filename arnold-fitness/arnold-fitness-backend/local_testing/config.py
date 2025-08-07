import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carica il file .env dalla directory corrente O dalla directory parent
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Definisci i percorsi base
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOCAL_TEST_DIR = BASE_DIR / "local_testing"

# === PERCORSI RICHIESTI DA components.py ===
SCHEMA_PATH = str(SRC_DIR / "context_validator" / "schemas" / "db_context_schema.json")
GENERATOR_PROMPTS_DIR = str(SRC_DIR / "llm_interfaces" / "query_generator_llm" / "prompt_templates")
TASK_GUIDANCE_PROMPT_PATH = str(
    SRC_DIR / "llm_interfaces" / "task_guidance_llm" / "prompt_templates" / "task_guidance.txt")

# === PERCORSI RICHIESTI DA context_setup.py ===
CHECKLIST_PATH = str(DATA_DIR / "checklists" / "webapplication_checklist.json")  # Default checklist
CHECKLISTS_DIR = str(DATA_DIR / "checklists")

# === ALTRI PERCORSI CHE POTREBBERO SERVIRE ===
INTERPRETER_PROMPTS_DIR = str(SRC_DIR / "llm_interfaces" / "user_input_interpreter_llm" / "prompt_templates")
TROUBLESHOOTER_PROMPT_PATH = str(
    SRC_DIR / "llm_interfaces" / "troubleshooting_llm" / "prompt_templates" / "troubleshoot_command_issue.txt")
ERROR_CLASSIFIER_PROMPT_PATH = str(
    SRC_DIR / "llm_interfaces" / "error_classifier_llm" / "prompt_templates" / "classify_error_detection.txt")

# === DEFAULTS RICHIESTI DA context_setup.py ===
DEFAULT_PT_TYPE = "webapp"
DEFAULT_GOAL = "Local penetration test session"

# === DIRECTORY PER I TEST LOCALI ===
TEST_SESSIONS_DIR = str(LOCAL_TEST_DIR / "test_sessions")
TEST_LOGS_DIR = str(LOCAL_TEST_DIR / "test_logs")
TOKEN_REPORTS_DIR = str(LOCAL_TEST_DIR / "token_reports")

# Crea le directory se non esistono
Path(TEST_SESSIONS_DIR).mkdir(exist_ok=True, parents=True)
Path(TEST_LOGS_DIR).mkdir(exist_ok=True, parents=True)
Path(TOKEN_REPORTS_DIR).mkdir(exist_ok=True, parents=True)


# === FUNZIONI RICHIESTE DA context_setup.py ===
def generate_test_id():
    """Genera un ID univoco per la sessione di test"""
    return f"LOCAL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def check_environment():
    """Verifica che tutte le variabili d'ambiente necessarie siano presenti"""
    required_vars = [
        'GEMINI_API_KEY',
        'QDRANT_URL',
        'QDRANT_API_KEY'
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print(f"\nChecked .env file at: {env_path}")
        print("\nMake sure your .env file contains:")
        for var in missing:
            print(f"{var}=your_value_here")
        return False

    # Verifica che i file critici esistano
    critical_paths = {
        "Schema": SCHEMA_PATH,
        "Default checklist": CHECKLIST_PATH,
        "Checklists directory": CHECKLISTS_DIR,
        "Generator prompts": GENERATOR_PROMPTS_DIR,
        "Task guidance prompt": TASK_GUIDANCE_PROMPT_PATH
    }

    for name, path in critical_paths.items():
        if not Path(path).exists():
            print(f"ERROR: {name} not found at {path}")
            return False

    print("✓ Environment check passed!")
    return True