#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
PY=.venv/bin/python
"$PY" -m tools.preflight
"$PY" -m tools.verify_manifests
"$PY" -m src.main --config configs/baseline.yaml --output out/baseline --offline --seed 42
"$PY" -m src.main --config configs/lab.yaml --output out/poc --offline --seed 42
"$PY" -m tools.evaluate_internal_t02
"$PY" -m pytest -ra
