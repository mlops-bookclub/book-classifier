#!/bin/bash
set -e

cd ~/book-recommender

# Load environment variables
set -a
source .env
set +a

# Activate venv
source .venv/bin/activate

echo "[1/4] Running DVC pipeline (train)..."
dvc repro train_baseline

echo "[2/4] Pushing model artifact to DVC remote (GCS)..."
dvc push

echo "[3/4] Committing dvc.lock to git..."
git add dvc.lock dvc.yaml
git diff --cached --quiet || git commit -m "chore: update dvc.lock after training run"
git push

echo "[4/4] Done. Metrics:"
cat models/metrics/item_based_cf_baseline.json
