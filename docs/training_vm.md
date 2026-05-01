# Training on a Remote VM

This document describes how to run the baseline training pipeline on a remote Linux VM. It covers SSH access, GCP authentication, DVC data pulling, experiment tracking with Weights & Biases, and pushing trained artifacts back to DVC remote storage.

## Prerequisites

- SSH key with access to the VM
- GCP service account JSON key with read/write access to `gs://bookclub-bookdata`
- Weights & Biases API key (project: `mlops-bookclub`)

## 1. Connect to the VM

```bash
ssh -i ~/.ssh/<your_key> ubuntu@<vm_ip>
```

## 2. Verify GitHub SSH Authentication

The VM already has an SSH key registered with GitHub. Verify it is working:

```bash
ssh -T git@github.com
# Hi <username>! You've successfully authenticated...
```

If the above fails, check that `~/.ssh/id_ed25519` exists and contact the project administrator for assistance.

## 3. Update the Repository

The repository is already cloned at `~/book-recommender`. Pull the latest changes before running training:

```bash
cd ~/book-recommender
git pull
```

## 4. Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Configure Credentials

The required credentials are already configured on the VM. The `.env` file at `~/book-recommender/.env` contains:

| Variable | Purpose |
|----------|---------|
| `WANDB_API_KEY` | Weights & Biases experiment tracking |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to the GCP service account JSON for DVC remote access |

If you need to add or update a credential, edit the file directly:

```bash
nano ~/book-recommender/.env
```

> **Security**: Never commit `.env` or the service account JSON to Git. Both are listed in `.gitignore`.

## 6. Pull Training Data

`train.sh` does **not** pull data automatically — this is a one-time manual step. If the `data/raw/` directory is empty or missing, run:

```bash
cd ~/book-recommender
source .venv/bin/activate
dvc pull data/raw.dvc
```

This fetches ~158 MB of raw GoodBooks-10k data from `gs://bookclub-bookdata`. Once pulled, the data is cached locally and does not need to be re-pulled for subsequent training runs unless the `data/raw.dvc` pointer changes.

## 7. Run a Training Job

Use the `train.sh` script at the repository root. It handles all steps end-to-end:

```bash
bash train.sh
```

### What `train.sh` does

| Step | Action |
|------|--------|
| 1 | Loads `.env` (W&B key, GCP credentials) |
| 2 | Activates the virtual environment |
| 3 | Runs `dvc repro --force train_baseline` (trains the model, logs to W&B) |
| 4 | Runs `dvc push` (uploads the metrics artifact to GCS) |
| 5 | Commits updated `dvc.lock` to Git and pushes to GitHub |

### Running in the background (survives SSH disconnect)

Use `tmux` so the job keeps running after you close your terminal:

```bash
tmux new-session -d -s train 'bash ~/book-recommender/train.sh 2>&1 | tee ~/book-recommender/train.log'
```

Reattach at any time:

```bash
tmux attach -t train
```

Monitor the log without attaching:

```bash
tail -f ~/book-recommender/train.log
```

## 8. Monitor Training

- **Live log**: `tail -f ~/book-recommender/train.log`
- **Weights & Biases**: [wandb.ai/mlops-bookclub/mlops-bookclub](https://wandb.ai/mlops-bookclub/mlops-bookclub)

Each run creates a W&B entry named `item-based-cf-baseline` with the following tracked values:

| Field | Description |
|-------|-------------|
| `train_interactions` | Number of training interactions |
| `test_interactions` | Number of test interactions |
| `num_users` | Total users evaluated |
| `hit_rate_at_k` | Hit rate @ top-K |
| `recall_at_k` | Recall @ top-K |

## 9. Verify the Artifact Was Pushed

After the job completes, confirm the artifact is in GCS:

```bash
cd ~/book-recommender
source .venv/bin/activate
dvc status   # should show nothing changed
cat models/metrics/item_based_cf_baseline.json
```

The `dvc.lock` file records the exact MD5 hash of the output. Any team member can retrieve it with:

```bash
dvc pull
```

## DVC Pipeline Definition

The training stage is declared in `dvc.yaml` at the repository root:

```yaml
stages:
  train_baseline:
    cmd: python -m ml_pipeline.src.trainers.run_baseline --ratings-path data/raw/goodbooks-10k/ratings.csv
    deps:
      - data/raw
      - ml_pipeline/src/trainers/run_baseline.py
      - ml_pipeline/src/models/item_based_cf.py
      - ml_pipeline/src/datasets/goodbooks.py
      - ml_pipeline/src/evaluation/ranking_metrics.py
    outs:
      - models/metrics/item_based_cf_baseline.json
```

DVC will skip the stage if none of the deps have changed. Use `--force` to re-run regardless:

```bash
dvc repro --force train_baseline
```

## Related Documentation

- [Baseline Recommender](baseline_recommender.md) — model design and metrics
- [Architecture](architecture.md) — full system overview
- [README](../README.md) — project setup and GCP authentication
