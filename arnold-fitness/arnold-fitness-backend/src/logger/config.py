import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # DEBUG, INFO, ERROR
LOG_FORMAT = os.getenv("LOG_FORMAT", "JSON")  # JSON o TEXT
LOG_TARGET = os.getenv("LOG_TARGET", "stdout")  # stdout, file, remote
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/system_logs.json")
