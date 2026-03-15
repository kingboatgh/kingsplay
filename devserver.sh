#!/bin/sh
source .venv/bin/activate
PORT=${PORT:-8080}
python -u -m flask --app main run --port "$PORT" --debug
