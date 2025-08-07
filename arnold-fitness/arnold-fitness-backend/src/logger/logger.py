import json
import sys
from datetime import datetime
from .config import LOG_LEVEL, LOG_FORMAT, LOG_TARGET, LOG_FILE_PATH


class Logger:
    LEVELS = {"DEBUG": 10, "INFO": 20, "DECISION": 25, "WARNING": 30, "ERROR": 40}

    def __init__(self, component_name: str, log_level=None, log_format=None, log_target=None, log_file_path=None):
        self.component = component_name
        self.log_level = self.LEVELS.get((log_level or LOG_LEVEL).upper(), 20)
        self.format = log_format or LOG_FORMAT
        self.target = log_target or LOG_TARGET
        self.file_path = log_file_path or LOG_FILE_PATH if self.target == "file" else None

    def log_debug(self, message: str, data=None):
        self._log("DEBUG", message, data)

    def log_info(self, message: str, data=None):
        self._log("INFO", message, data)

    def log_decision(self, decision: str, data=None):
        self._log("DECISION", decision, data)

    def log_warning(self, message: str, data=None):
        self._log("WARNING", message, data)

    def log_error(self, message: str, data=None):
        self._log("ERROR", message, data)

    def _log(self, level: str, message: str, data=None):
        if self.LEVELS[level] < self.log_level:
            return  # Ignora log con livello inferiore a quello impostato

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": self.component,
            "level": level,
            "message": message,
            "data": data,
        }

        formatted = json.dumps(entry) if self.format == "JSON" else self._format_text(entry)

        self._output(formatted)

    def _format_text(self, entry):
        data_str = f" | Data: {entry['data']}" if entry['data'] else ""
        return f"[{entry['timestamp']}] [{entry['component']}] [{entry['level']}]: {entry['message']}{data_str}"

    def _output(self, formatted_log):
        if self.target == "stdout":
            print(formatted_log, file=sys.stdout)
        elif self.target == "file":
            with open(self.file_path, "a") as log_file:
                log_file.write(formatted_log + "\n")
        elif self.target == "remote":
            self._send_remote(formatted_log)

    def _send_remote(self, log_entry):
        pass  # placeholder
