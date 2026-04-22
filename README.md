# Book Recommender
Classifies books based on specific dataset features

## Branching Strategy

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for the branching strategy used in this project.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the planned MLOps system architecture.

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
# Data Setup: Git, DVC, and GCP

This project uses [Git](https://git-scm.com/) for source code version control and [DVC (Data Version Control)](https://dvc.org/) for managing large datasets and model files. Our DVC remote storage is hosted in a Google Cloud Platform (GCP) bucket.

---

## 1. Prerequisites

Before starting, ensure you have Python and Git installed on your machine.
We use a `requirements.txt` file to manage DVC and its Google Cloud Storage dependencies. It is highly recommended to use a virtual environment (like `venv` or `conda`). 

Once your virtual environment is active, install the dependencies by running:
```bash
pip install -r requirements.txt
```
## 2. Setting Up GCP Authentication

Instead of managing shared keys, we use Application Default Credentials (ADC). This allows DVC to automatically securely use your personal Google account to access the cloud storage.
### Step 1: Ensure you have bucket access

Ensure that the project administrator has granted your Google account the necessary IAM permissions (e.g., Storage Object Admin or Storage Object Viewer) for the project's GCP bucket.
### Step 2: Authenticate via the gcloud CLI

Open your terminal and run the following command to log in:
```bash
gcloud auth application-default login
```
This command will open a browser window. Log in using the Google account associated with your GCP permissions. Once completed, gcloud will save your credentials locally, and DVC will automatically detect and use them.

## 3. Pulling the Data
Once your credentials are set up and dependencies are installed, getting the data is as simple as running standard Git and DVC commands.

1. First, make sure your Git repository is up to date:
```bash
    git pull
```

2. Then, download the corresponding data files from the GCP bucket:
```bash
    dvc pull
```
If authentication is successful, DVC will connect to GCP and download the data into your workspace.
