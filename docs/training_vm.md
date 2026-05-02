# Training on a Remote VM

This document describes how to run the baseline training pipeline on a remote Linux VM. It covers SSH access, GCP authentication, DVC data pulling, experiment tracking with Weights & Biases, and pushing trained artifacts back to DVC remote storage.

## VM Details

| Property | Value |
|----------|-------|
| Name | `instance-20260502-200611` |
| External IP | `34.65.157.169` |
| Zone | `europe-west6-c` |
| OS | Debian GNU/Linux 12 |
| User | `bookclub` |

## Project & IAM

All resources (VM, GCS bucket `gs://bookclub-bookdata`) live in the GCP project **`mlops-bookclub`**.

## Prerequisites

- SSH private key with a corresponding public key in `/home/bookclub/.ssh/authorized_keys` on the VM
- Weights & Biases API key (project: `mlops-bookclub`)

## 1. Connect to the VM

All team members connect as the shared `bookclub` user using their own SSH key:

```bash
ssh -i ~/.ssh/<your_key> bookclub@34.65.157.169
```

Your public key must be in `/home/bookclub/.ssh/authorized_keys` on the VM. Contact the project administrator to add it.

## 2. Verify GitHub SSH Authentication

The `bookclub` user has an SSH key registered with GitHub. Verify it is working:

```bash
ssh -T git@github.com
# Hi <username>! You've successfully authenticated...
```

If the above fails, check that `~/.ssh/private_key` exists on the VM and contact the project administrator.

Ensure the remote uses SSH (not HTTPS):

```bash
git -C ~/book-recommender remote set-url origin git@github.com:mlops-bookclub/book-recommender.git
```

## 3. Set Up Python Environment

The venv is already created at `~/book-recommender/.venv`. If it is missing or incomplete, recreate it:

```bash
cd ~/book-recommender
python3 -m venv .venv
/home/bookclub/book-recommender/.venv/bin/pip install -r requirements.txt
```

> **Note**: DVC is installed inside the venv. Use the `PATH` injection pattern below rather than `source .venv/bin/activate` — activation does not propagate reliably into non-interactive shells such as tmux.

## 4. Configure Credentials

The `.env` file at `~/book-recommender/.env` must contain:

| Variable | Value |
|----------|-------|
| `WANDB_API_KEY` | Weights & Biases API key for the `mlops-bookclub` project |
| `GOOGLE_APPLICATION_CREDENTIALS` | Absolute path to the GCP service account JSON — use `$HOME/.config/gcp/service-account.json` |

If you need to add or update a credential:

```bash
nano ~/book-recommender/.env
```

> **Security**: Never commit `.env` or the service account JSON to Git. Both are listed in `.gitignore`.
> The JSON is stored at `~/.config/gcp/service-account.json` — note this path varies by username (`lessf` via gcloud vs `kaloyan_georgiev99` via SSH key).

## 5. Pull Training Data

`train.sh` does **not** pull data automatically — this is a one-time manual step. If the `data/raw/` directory is empty or missing, run:

```bash
cd ~/book-recommender
PATH=/home/bookclub/book-recommender/.venv/bin:$PATH dvc pull data/raw.dvc
```

This fetches ~158 MB of raw GoodBooks-10k data from `gs://bookclub-bookdata`. Once pulled, the data is cached locally and does not need to be re-pulled for subsequent training runs unless the `data/raw.dvc` pointer changes.

## 6. Run a Training Job

Use the `train.sh` script at the repository root. It handles all steps end-to-end:

```bash
bash train.sh
```

### What `train.sh` does

| Step | Action |
|------|--------|
| 1 | Resolves the repo root dynamically (works from any working directory) |
| 2 | Loads `.env` (W&B key, GCP credentials) |
| 3 | Activates the virtual environment |
| 4 | Runs `dvc repro --force train_baseline` (trains the model, logs to W&B) |
| 5 | Runs `dvc push` (uploads the metrics artifact to GCS) |
| 6 | Commits updated `dvc.lock` to Git |
| 7 | Pushes the commit to GitHub — **only if `GIT_PUSH_AFTER_TRAIN=1` is set** and the current branch is not `main` |

### Controlling the git push

By default the script commits `dvc.lock` locally but does **not** push to GitHub. To enable pushing:

```bash
GIT_PUSH_AFTER_TRAIN=1 bash train.sh
```

Pushing is blocked on `main` to prevent accidental direct pushes to protected branches. Always run training from a feature branch.

### Running in the background (survives SSH disconnect)

Use `tmux` so the job keeps running after you close your terminal:

```bash
tmux new-session -d -s train 'cd /home/bookclub/book-recommender && PATH=/home/bookclub/book-recommender/.venv/bin:$PATH bash train.sh 2>&1 | tee train.log'
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
PATH=/home/bookclub/book-recommender/.venv/bin:$PATH dvc status   # should show nothing changed
cat models/metrics/item_based_cf_baseline.json
```

The `dvc.lock` file records the exact MD5 hash of the output. Any team member can retrieve it with:

```bash
PATH=/home/bookclub/book-recommender/.venv/bin:$PATH dvc pull
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
