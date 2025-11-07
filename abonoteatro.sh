#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit 1

# Cargar variables de entorno desde .env si existe
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

source venv/bin/activate
python abonoteatro.py
exit 0
