<p align=right style="margin-bottom: -2rem">
  <a href="https://github.com/mlops-bookclub/book-recommender/actions/workflows/tests.yml">
    <img src="https://github.com/mlops-bookclub/book-recommender/actions/workflows/tests.yml/badge.svg?branch=main&event=push" alt="Test">
  </a>
</p>

# Book Recommender

Classifies books based on specific dataset features

## Branching Strategy

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the branching strategy used in this project.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the planned MLOps system architecture.

## Training

See [docs/training_vm.md](docs/training_vm.md) for instructions on running training on a remote VM, including DVC pipeline execution, Weights & Biases tracking, and pushing artifacts to GCS.

## Relevant Project Sources

- [MLFlow Tracking Quick Start](https://mlflow.org/docs/latest/ml/tracking/quickstart/)
- [GoodBooks dataset](https://github.com/zygmuntz/goodbooks-10k)
- [DVC Start](https://doc.dvc.org/start)
- [Docker Get Started](https://docs.docker.com/get-started/)
- [Pytest Get Started](https://docs.pytest.org/en/stable/getting-started.html)
- [Streamlit Docs](https://docs.streamlit.io)
- [Weights&Biases Get Started](https://docs.wandb.ai/get-started)
- [Pytorch Docs](https://docs.pytorch.org/docs/stable/index.html?_gl=1*xxz00o*_up*MQ..*_ga*ODY5MjEyMzA4LjE3NzYzMzI3MjY.*_ga_469Y0W5V62*czE3NzYzMzI3MjUkbzEkZzAkdDE3NzYzMzI3MjUkajYwJGwwJGgw)
- [Fast API](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [GitHub Actions QuickStart](https://docs.github.com/en/actions/get-started/quickstart)

## Repository Structure

```text
book-recommender/
|-- .dvc/                  # DVC configuration
|-- .github/workflows/     # CI/CD pipelines
|-- docs/                  # Documentation and submission material
|-- frontend/              # Frontend application
|   |-- src/               # Frontend source code
|   `-- tests/             # Frontend-specific tests
|-- backend/               # API and model serving
|   |-- src/               # Backend application source code
|   `-- tests/             # Backend-specific tests
|-- ml_pipeline/           # Data prep, training, evaluation, utilities
|   |-- src/               # Pipeline source code
|   |   |-- datasets/
|   |   |-- evaluation/
|   |   |-- features/
|   |   |-- models/
|   |   |-- trainers/
|   |   |-- transforms/
|   |   `-- utils/
|   `-- tests/             # Pipeline-specific tests
|-- experiments/           # EDA notebooks and prototyping
|-- infrastructure/        # Infra and deployment config
|-- integration_tests/     # Cross-service and repo structure tests
|-- models/                # Metrics and DVC-tracked model artifacts
`-- data/                  # DVC-tracked raw/processed data
```

## Weights and Biases Setup

Create a Weights & Biases Api Token and save it in the .env file in the root directory of the project as:
WANDB_API_KEY=....

## Data Setup: Git, DVC, and GCP

This project uses [Git](https://git-scm.com/) for source code version control and [DVC (Data Version Control)](https://dvc.org/) for managing large datasets and model files. Our DVC remote storage is hosted in a Google Cloud Platform (GCP) bucket.

## 1. Prerequisites

Before starting, ensure you have Python and Git installed on your machine. We use `requirements.txt` to manage DVC and analysis dependencies. It is recommended to use a virtual environment such as `venv` or `conda`.

Once your virtual environment is active, install the dependencies by running:

```bash
pip install -r requirements.txt
```

## 2. Setting Up GCP Authentication

The DVC remote is hosted on GCP (`gs://bookclub-bookdata`). Two authentication methods are supported:

### Option A: Application Default Credentials (local machine with browser)

Ensure the project administrator has granted your Google account IAM permissions for the bucket, then run:

```bash
gcloud auth application-default login
```

This opens a browser window. Once completed, DVC will detect and use your credentials automatically.

### Option B: Service Account JSON (headless / VM environments)

For remote VMs or CI environments without a browser, use a service account key:

1. Obtain the service account JSON from the project administrator.
2. Place it at a safe path (e.g. `~/.config/gcp/service-account.json`) with `chmod 600`.
3. Add the following to your `.env` file:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

DVC will pick up the credential automatically via the environment variable.

> See [docs/training_vm.md](docs/training_vm.md) for the complete VM setup walkthrough.

## 3. Pulling the Data

Once your credentials are set up and dependencies are installed, update the repository and then download the matching data files:

```bash
git pull
dvc pull
```

## First Recommendation Baseline

The current baseline is an item-item collaborative filtering recommender.

- [Baseline Recommender](docs/baseline_recommender.md)

Book-book similarity uses cosine similarity over binary user interaction vectors:

```text
sim(i, j) = co_likes(i, j) / sqrt(likes(i) * likes(j))
```

Where:

- `co_likes(i, j)` is the number of users who positively rated both books.
- `likes(i)` is the number of users who positively rated book `i`.
- `likes(j)` is the number of users who positively rated book `j`.

The implementation uses `scipy.sparse` to compute the item-item neighborhood graph efficiently.

The training pipeline is declared in `dvc.yaml` and run via `train.sh`. To reproduce the last committed run:

```bash
dvc repro train_baseline
```

Or to run it directly:

```bash
python -m ml_pipeline.src.trainers.run_baseline --ratings-path data/raw/goodbooks-10k/ratings.csv
```

The metrics artifact is written to `models/metrics/item_based_cf_baseline.json`, tracked by DVC, and pushed to `gs://bookclub-bookdata` after each training run. Experiment metrics are logged to [Weights & Biases](https://wandb.ai/mlops-bookclub/mlops-bookclub).