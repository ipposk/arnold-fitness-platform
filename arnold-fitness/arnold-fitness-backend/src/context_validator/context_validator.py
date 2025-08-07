import json
import os
from jsonschema import validate, ValidationError, Draft202012Validator
from src.logger.logger import Logger


class ContextValidator:
    def __init__(self, schema_path: str, component_name="ContextValidator"):
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        self.logger = Logger(component_name)
        self.validator = Draft202012Validator(self.schema)

    def validate(self, context_update: dict) -> bool:
        """Validazione semplice: ritorna True/False, loggando in caso di errore."""
        errors = sorted(self.validator.iter_errors(context_update), key=lambda e: e.path)
        if not errors:
            return True

        for error in errors:
            self.logger.log_error("Validazione fallita", {
                "path": list(error.path),
                "message": error.message
            })

        return False

    def validate_strict(self, context_update: dict) -> (bool, list):
        """Validazione con raccolta dettagliata di errori."""
        errors = sorted(self.validator.iter_errors(context_update), key=lambda e: e.path)
        if not errors:
            return True, []

        error_list = []
        for error in errors:
            error_detail = f"Path: {'/'.join(str(p) for p in error.path)} - Error: {error.message}"
            error_list.append(error_detail)

        return False, error_list
