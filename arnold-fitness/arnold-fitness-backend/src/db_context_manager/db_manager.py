from datetime import datetime
from typing import Dict
from .dynamodb_storage import DynamoDBContextStorage

# Puoi rimuovere o personalizzare il Logger secondo le tue preferenze.
class Logger:
    def __init__(self, name): self.name = name
    def log_info(self, msg, extra=None): print(f"[INFO][{self.name}] {msg} {extra or ''}")
    def log_error(self, msg, extra=None): print(f"[ERROR][{self.name}] {msg} {extra or ''}")

class DbContextManager:
    def __init__(self, component_name="DbContextManager"):
        self.storage = DynamoDBContextStorage()
        self.logger = Logger(component_name)

    def get_current(self, test_id: str) -> Dict:
        item = self.storage.get_context(test_id)
        if not item or "context" not in item:
            self.logger.log_error("Nessun contesto trovato", {"test_id": test_id})
            return None
        return item["context"]

    def update_context_and_version(self, test_id: str, new_context: Dict) -> bool:
        now_iso = datetime.utcnow().isoformat() + "Z"
        context_to_save = new_context.copy()
        meta = context_to_save.get("meta", {})
        meta["updated_at"] = now_iso
        meta["timestamp"] = now_iso
        meta.setdefault("created_at", now_iso)
        meta.setdefault("version", "1.0")
        meta.setdefault("updated_by", "DbContextManager")
        meta.setdefault("source", "update_context_and_version")
        context_to_save["meta"] = meta

        try:
            self.storage.save_context(test_id, context_to_save)
            self.logger.log_info(f"Contesto per test_id {test_id} aggiornato/salvato su DynamoDB.")
            return True
        except Exception as e:
            self.logger.log_error("Errore durante salvataggio su DynamoDB", {"test_id": test_id, "error": str(e)})
            return False

    def delete_context(self, test_id: str):
        try:
            self.storage.delete_context(test_id)
            self.logger.log_info(f"Sessione {test_id} eliminata da DynamoDB.")
            return True
        except Exception as e:
            self.logger.log_error("Errore durante eliminazione da DynamoDB", {"test_id": test_id, "error": str(e)})
            return False
