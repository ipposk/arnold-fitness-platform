"""
Setup del contesto iniziale per i test locali
"""
from datetime import datetime
from .config import SCHEMA_PATH, CHECKLIST_PATH, DEFAULT_PT_TYPE, DEFAULT_GOAL, generate_test_id
import json

def create_initial_context(pt_type=None, goal=None):
    """
    Crea un contesto iniziale per la sessione di test
    """
    pt_type = pt_type or DEFAULT_PT_TYPE
    goal = goal or DEFAULT_GOAL
    test_id = generate_test_id()

    print(f"Creating initial context for test_id: {test_id}")

    # Carica la checklist direttamente dal file JSON
    with open(CHECKLIST_PATH, 'r', encoding='utf-8') as f:
        checklist = json.load(f)

    # Determina il primo phase_id
    current_phase_id = checklist[0]["phase_id"] if checklist else None

    # Imposta il primo check come in_progress
    if checklist and len(checklist) > 0:
        first_phase = checklist[0]
        if "tasks" in first_phase and len(first_phase["tasks"]) > 0:
            first_task = first_phase["tasks"][0]
            if "checks" in first_task and len(first_task["checks"]) > 0:
                first_check = first_task["checks"][0]
                first_check["state"] = "in_progress"
                first_check["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Crea il contesto iniziale
    initial_context = {
        "test_id": test_id,
        "pt_type": pt_type,
        "scope": {
            "targets": [],
            "domain": None
        },
        "credentials": {},
        "checklist": checklist,
        "current_phase_id": current_phase_id,
        "goal": goal,
        "findings": [],
        "evidence": [],
        "meta": {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "updated_by": "local_testing",
            "source": "local_testing"
        }
    }

    return initial_context


def get_context_summary(context):
    """
    Genera un riassunto del contesto corrente come dizionario
    """
    if not context:
        return {
            "test_id": "N/A",
            "pt_type": "N/A",
            "goal": "N/A",
            "current_phase_id": "N/A",
            "check_states": {"pending": 0, "in_progress": 0, "done": 0, "failed": 0, "skipped": 0},
            "total_checks": 0,
            "current_check": None,
            "findings_count": 0,
            "percentage_complete": 0.0
        }

    # Conta i check per stato
    check_states = {"pending": 0, "in_progress": 0, "done": 0, "failed": 0, "skipped": 0}
    total_checks = 0

    for phase in context.get("checklist", []):
        for task in phase.get("tasks", []):
            for check in task.get("checks", []):
                total_checks += 1
                state = check.get("state", "pending")
                if state in check_states:
                    check_states[state] += 1

    # Trova il check attualmente in progress
    current_check = None
    current_phase_title = "N/A"

    for phase in context.get("checklist", []):
        if phase["phase_id"] == context.get("current_phase_id"):
            current_phase_title = phase.get("title", "Unknown Phase")
            for task in phase.get("tasks", []):
                for check in task.get("checks", []):
                    if check.get("state") == "in_progress":
                        current_check = {
                            "phase": phase["title"],
                            "task": task["title"],
                            "check": check["description"]
                        }
                        break
                if current_check:
                    break
            break

    percentage_complete = (check_states['done'] / total_checks * 100) if total_checks > 0 else 0.0

    return {
        "test_id": context.get('test_id', 'N/A'),
        "pt_type": context.get('pt_type', 'N/A'),
        "goal": context.get('goal', 'N/A'),
        "current_phase": current_phase_title,
        "current_phase_id": context.get('current_phase_id', 'N/A'),
        "check_states": check_states,
        "total_checks": total_checks,
        "done_checks": check_states['done'],  # Aggiunto per ui.py
        "progress_percentage": percentage_complete,  # Rinominato per ui.py
        "current_check": current_check,
        "findings_count": len(context.get('findings', [])),
        "percentage_complete": percentage_complete  # Manteniamo anche il nome originale per compatibilità
    }