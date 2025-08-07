import json
import os
from datetime import datetime
import copy


def load_json_file(path: str) -> dict:
    """Carica un file JSON da disco."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File JSON non trovato: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_initial_context_from_schema(schema_path: str) -> dict:
    """
    Crea un initial context vuoto basato su uno schema JSON.
    Riempe i campi richiesti con valori neutri.
    """
    schema = load_json_file(schema_path)
    context = {}

    for key, value in schema.get("properties", {}).items():
        if "default" in value:
            context[key] = value["default"]
        else:
            t = value.get("type")
            if t == "string":
                context[key] = ""
            elif t == "array":
                context[key] = []
            elif t == "object":
                context[key] = {}
            elif t == "integer":
                context[key] = 0
            elif isinstance(t, list) and "null" in t:
                context[key] = None
            else:
                context[key] = None

    # Popoliamo i meta campi obbligatori (created_at, updated_at, version)
    now = datetime.utcnow().isoformat() + "Z"
    if "meta" in context:
        context["meta"] = {
            "created_at": now,
            "updated_at": now,
            "version": "v1",
            "updated_by": None
        }

    return context


def parse_checklist_template(checklist_path: str) -> list:
    """
    Parsea un file checklist template (come web_app_checklist.json)
    nel formato richiesto dal nuovo db_context_schema.
    """
    raw_checklist = load_json_file(checklist_path)

    parsed_checklist = []
    for phase in raw_checklist:
        phase_obj = {
            "phase_id": phase["id_prefix"],
            "title": phase["phase"],
            "tasks": []
        }
        for category in phase["categories"]:
            task_obj = {
                "task_id": category["category"],
                "title": category["category"],
                "checks": []
            }
            for check in category["checks"]:
                check_obj = {
                    "check_id": check["id"],
                    "description": check["name"],
                    "state": "pending",
                    "notes": None,
                    "timestamp": None,
                    "related_finding_ids": []
                }
                task_obj["checks"].append(check_obj)
            phase_obj["tasks"].append(task_obj)

        parsed_checklist.append(phase_obj)

    return parsed_checklist