# Pipeline Project

Production-ready ML pipeline for binary classification using scikit-learn with data preprocessing and model management.

## Features

- **Reproducible training**: Fixed random seed for deterministic results
- **Data processing**: Stateful (with statistics) and stateless transformers
- **Pipeline management**: Save/load trained models with `joblib`
- **Comprehensive tests**: Unit tests, integration tests, and differential tests
- **Production-ready**: Proper project structure with `pyproject.toml` configuration

## Installation

```bash
pip install -e .
```

## Project Structure

```
├── src/pipeline_project/
│   ├── train.py              # Training script with data loading & preprocessing
│   ├── predict.py            # Inference script
│   ├── pipeline.py           # Pipeline assembly
│   ├── data_processing.py    # Custom transformers
│   ├── utils.py              # Utility functions
│   └── __init__.py
├── tests/
│   ├── test_pipeline.py      # Unit tests for pipeline
│   ├── test_processing.py    # Unit tests for transformers
│   └── test_differential.py  # Differential tests
├── models/                   # Saved models directory
└── data.csv                  # Training data
```

## Usage

### Training

```bash
python -m pipeline_project.train
```

Trains the model on `data.csv` and saves:
- `models/model.pkl` - Trained sklearn Pipeline
- `models/columns.pkl` - Feature column names (for consistency)

### Prediction

```bash
python -m pipeline_project.predict
```

Loads the trained model and makes predictions on first 5 rows of `data.csv`.

## Data Processing

### Stateless Transformer: ColumnDropper
Removes specified columns without learning anything from the data.

```python
from pipeline_project.data_processing import ColumnDropper

dropper = ColumnDropper(columns=['col1', 'col2'])
dropper.fit(X)  # Does nothing
X_transformed = dropper.transform(X)
```

### Stateful Transformer: MeanImputer
Learns mean values during `fit()` and uses them to impute missing values during `transform()`.

```python
from pipeline_project.data_processing import MeanImputer

imputer = MeanImputer()
imputer.fit(X)  # Learns means
X_transformed = imputer.transform(X)
print(imputer.means)  # Access learned statistics
```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

### Test Coverage

- **Unit tests** (`test_pipeline.py`, `test_processing.py`): Test individual components
- **Differential tests** (`test_differential.py`): Test consistency, determinism, and robustness
  - Determinism: Same input → Same output
  - Consistency: Pipeline generalizes across different dataset sizes
  - Robustness: Handles edge cases (zeros, identical features, large values)
  - Performance: Model achieves minimum accuracy thresholds

## Configuration

Project dependencies are defined in `pyproject.toml`:
- scikit-learn
- pandas
- joblib
- pytest

## Web Service (Part III/IV)

Run API locally:

```bash
uvicorn pipeline_project.main:app --reload
```

Important endpoints:
- `GET /` - HTML interface
- `GET /docs` - Swagger UI
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /predict` - Prediction endpoint

### Test Client

```bash
python scripts/test_client.py --base-url http://localhost:8000
```

### Docker

```bash
docker build -t pipeline-project:local .
docker run --rm -p 8000:8000 pipeline-project:local
```

## Part IV deployment stack

The repo now includes an Azure-oriented deployment stack:

- `docker-compose.yml` - runs the API, Prometheus, Grafana, Loki, and Promtail together
- `deploy/prometheus/` - Prometheus scrape configuration
- `deploy/loki/` - Loki storage and log aggregation configuration
- `deploy/promtail/` - Promtail config for shipping container logs to Loki
- `deploy/grafana/` - Grafana datasource and dashboard provisioning for metrics and logs
- `infra/terraform/` - Azure VM provisioning (VNet, subnet, NSG, public IP)
- `infra/ansible/` - Docker installation and service deployment on the VM

### Azure flow

1. Build and publish the Docker image with GitHub Actions.
2. Use Terraform to create an Azure Linux VM and network/security resources.
3. Use Ansible to install Docker, clone the repository, and start the stack with `docker compose`.
4. Open the app at `http://<vm-public-ip>:8000`, Grafana at `http://<vm-public-ip>:3000`, Prometheus at `http://<vm-public-ip>:9090`, and Loki at `http://<vm-public-ip>:3100`.

### Fully automated deploy with GitHub Actions

You can provision the VM and deploy the stack from GitHub Actions using:

- `.github/workflows/infra-deploy.yml`

This workflow runs on `workflow_dispatch` and executes:

1. Terraform apply (creates VM + security group)
2. Ansible playbook (installs Docker + deploys service)

### What you need to register/configure first

Before running CI/CD and infra workflows, configure these accounts/services:

1. GitHub account + repository (required for Actions and GHCR)
2. Container registry (GHCR is already used in `.github/workflows/docker-publish.yml`)
3. Azure account with an active subscription (for VM provisioning)

### Required GitHub repository secrets

Add these in GitHub repository settings: `Settings -> Secrets and variables -> Actions`.

- `AZURE_CREDENTIALS` (service principal JSON for `azure/login`)
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_SSH_PRIVATE_KEY` (full private key text)
- `AZURE_SSH_PUBLIC_KEY` (matching public key text)
- `GRAFANA_ADMIN_PASSWORD`

Optional:

- `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` if you later publish to Docker Hub as well.

### Terraform variables

The Azure Terraform stack expects:

- `subscription_id` - Azure subscription ID
- `azure_location` - Azure region for resources
- `vm_size` - VM size, for example `Standard_B1s`
- `public_key_path` - local path to the SSH public key used for VM login
- `private_key_path` - local path to the matching private key for SSH access

### Local monitoring stack

You can also run the full stack locally:

```bash
docker compose up --build
```

Then open:

- `http://localhost:8000/`
- `http://localhost:8000/docs`
- `http://localhost:8000/metrics`
- `http://localhost:3000/`
- `http://localhost:9090/`
- `http://localhost:3100/`