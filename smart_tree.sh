#!/bin/bash

# Configura i parametri
MAX_FILES=20
INDENT=""
EXCLUDE_DIRS="node_modules|.venv|.git|.serverless|.qdrant|__pycache__|.pytest_cache|dist|build"

# Funzione ricorsiva
print_tree() {
    local DIR="$1"
    local PREFIX="$2"

    shopt -s nullglob
    for entry in "$DIR"/*; do
        local name=$(basename "$entry")
        # Salta directory escluse
        if [[ "$entry" =~ $EXCLUDE_DIRS ]]; then
            continue
        fi
        if [ -d "$entry" ]; then
            echo "${PREFIX}├── $name/"
            print_tree "$entry" "${PREFIX}│   "
        elif [ -f "$entry" ]; then
            files=("$DIR"/*)
            if (( ${#files[@]} > MAX_FILES )); then
                echo "${PREFIX}└── [${#files[@]} files] Troppi file, non mostrati"
                break
            else
                echo "${PREFIX}├── $name"
            fi
        fi
    done
    shopt -u nullglob
}

# Esecuzione dallo script
START_DIR=${1:-.}
print_tree "$START_DIR" ""
