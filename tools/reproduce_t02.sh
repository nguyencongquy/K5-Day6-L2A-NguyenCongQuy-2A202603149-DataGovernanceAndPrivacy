#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
TASK_PY=${TASK_PY:-.venv/bin/python}
"$TASK_PY" -m tools.preflight > reports/preflight.txt
"$TASK_PY" -m tools.verify_manifests > reports/manifest_check.txt
"$TASK_PY" -m src.main --config configs/baseline.yaml --output out/baseline --run-name baseline --offline --seed 42
"$TASK_PY" -m src.main --config configs/lab.yaml --output out/poc --run-name poc --offline --seed 42
"$TASK_PY" -m src.main --input data/ood_synthetic --output out/ood --offline --seed 42
"$TASK_PY" -m tools.evaluate_internal_t02
"$TASK_PY" -m tools.analyze_t02_requirements
"$TASK_PY" -m pytest -ra > reports/test_results.txt
"$TASK_PY" -m tools.write_t02_report
"$TASK_PY" -m tools.record_visual_review_t02
cat reports/test_results.txt
