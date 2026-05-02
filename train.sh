#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Load environment variables
set -a
source .env
set +a

# Activate venv
source .venv/bin/activate

echo "[1/4] Running DVC pipeline (train)..."
dvc repro --force train_baseline

echo "[2/4] Pushing model artifact to DVC remote (GCS)..."
dvc push

echo "[3/4] Committing dvc.lock to git..."
git add dvc.lock dvc.yaml
git diff --cached --quiet || git commit -m "chore: update dvc.lock after training run"

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "${GIT_PUSH_AFTER_TRAIN:-0}" = "1" ]; then
  if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo "[3/4] Skipping git push: refusing to push from protected branch '$current_branch'."
  else
    echo "[3/4] Pushing git commit to branch '$current_branch'..."
    git push
  fi
else
  echo "[3/4] Skipping git push. Set GIT_PUSH_AFTER_TRAIN=1 to enable pushing."
fi

echo "[4/4] Done. Metrics:"
cat models/metrics/item_based_cf_baseline.json
