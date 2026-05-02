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

The repo now includes an AWS-oriented deployment stack:

- `.github/workflows/ci.yml` - CI on push to `main` (tests + Docker build + Docker Hub push)
- `docker-compose.yml` - local stack with image build
- `docker-compose.prod.yml` - production stack for VM deployment (pulls app image from registry)
- `deploy/prometheus/` - Prometheus scrape configuration
- `deploy/loki/` - Loki storage and log aggregation configuration
- `deploy/promtail/` - Promtail config for shipping container logs to Loki
- `deploy/grafana/` - Grafana datasource and dashboard provisioning for metrics and logs
- `infra/terraform/` - AWS EC2 provisioning (security group, public IP/DNS outputs)
- `infra/ansible/` - Docker installation and service deployment on EC2

### CI and deployment flow (AWS)

1. Push to `main` to run CI (`.github/workflows/ci.yml`): tests, Docker build, Docker Hub push.
2. Use Terraform to create an Ubuntu EC2 VM.
3. Use Ansible to install Docker, pull the published image, and run the app + monitoring stack.
4. Open:
  - `http://<public-ip>/health` (port 80 -> app)
  - `http://<public-ip>:8000/health`
  - `http://<public-ip>:3000` (Grafana)
  - `http://<public-ip>:9090` (Prometheus)
  - `http://<public-ip>:3100` (Loki)

### Important rule for this repository

Deployment to VM is intentionally not done from GitHub Actions.
Terraform + Ansible are run manually from your workstation.

### Required GitHub repository secrets

Add these in GitHub repository settings under Actions secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### What you need to register/configure first

Before running CI/CD and infra workflows, configure these accounts/services:

1. GitHub account + repository
2. Docker Hub account/repository
3. AWS account with IAM permissions for EC2 provisioning

### Terraform variables

The AWS Terraform stack expects:

- `aws_region` - AWS region (example: `eu-north-1`)
- `instance_name` - EC2 instance name
- `instance_type` - EC2 type (example: `t3.micro`)
- `key_name` - existing AWS key pair name (example: `telco-key`)
- `allowed_cidr_blocks` - source CIDRs for 22/80/8000/3000/9090/3100

### End-to-end deployment steps

1. Push code to `main` and wait for `.github/workflows/ci.yml` to publish image:
  - image: `docker.io/<DOCKERHUB_USERNAME>/pipeline-project:latest`
2. Provision EC2 with Terraform:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply -var-file=terraform.tfvars
terraform output -raw public_ip
```

3. Prepare Ansible inventory:

```bash
cd ../ansible
cp inventory.ini.example inventory.ini
# set ansible_host to terraform output public_ip
```

4. Deploy via Ansible (no GitHub Actions deployment):

```bash
export APP_IMAGE=docker.io/<DOCKERHUB_USERNAME>/pipeline-project:latest
export GRAFANA_ADMIN_PASSWORD=<strong-password>
ansible-playbook -i inventory.ini playbook.yml
```

5. Validate endpoints:
  - `http://<public-ip>/health`
  - `http://<public-ip>:8000/health`
  - `http://<public-ip>:3000`
  - `http://<public-ip>:9090`
  - `http://<public-ip>:3100`

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