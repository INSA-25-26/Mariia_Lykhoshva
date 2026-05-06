# Income Classification Pipeline - Part 4

This is the final part of the income prediction project. It combines everything from the previous parts and adds a REST API, Docker support, and deployment to AWS with monitoring.

## What's in Here?

The project takes data about people (age, education, job, etc.) and predicts whether their income is above or below 50k per year. We use a scikit-learn pipeline that handles data preprocessing, feature engineering, and model training automatically.

On top of the ML stuff, there's a FastAPI REST API so you can send prediction requests, everything is dockerized for easy deployment, and there's monitoring with Prometheus and Grafana when running on AWS.

## Quick Start

### Setup

```bash
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install
pip install -e .
```

### Train the Model

```bash
python -m pipeline_project.train
```

This loads `data.csv`, processes it, trains the model, and saves:
- `models/model.pkl` - the trained model
- `models/columns.pkl` - feature names (we need this for consistency)

### Run the API

```bash
python -m pipeline_project.main
```

The API runs on `http://localhost:8000`

You can:
- `POST /predict` - send data and get a prediction
- `GET /health` - check if it's running
- `GET /metrics` - get Prometheus metrics

Example request:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 39,
    "workclass": "State-gov",
    "fnlwgt": 77516,
    "education": "Bachelors",
    "marital_status": "Never-married",
    "occupation": "Adm-clerical",
    "relationship": "Not-in-family",
    "race": "White",
    "sex": "Male",
    "hours_per_week": 40
  }'
```

### Run Tests

```bash
pytest tests/ -v
```

We have three types of tests:
- Unit tests - check if functions work correctly
- Integration tests - check if everything works together
- Differential tests - make sure the model is stable and consistent

## Project Layout

```
Part_4/
├── src/pipeline_project/
│   ├── main.py              # FastAPI app entry point
│   ├── api.py               # API endpoints
│   ├── service.py           # Prediction logic
│   ├── schemas.py           # Request/response models
│   ├── train.py             # Training script
│   ├── predict.py           # Inference script
│   ├── pipeline.py          # ML pipeline assembly
│   ├── data_processing.py   # Custom transformers
│   ├── utils.py             # Helper functions
│   └── __init__.py
│
├── tests/
│   ├── test_pipeline.py     # Tests for ML pipeline
│   ├── test_api.py          # Tests for API endpoints
│   ├── test_main.py         # Tests for main logic
│   ├── test_processing.py   # Tests for data processing
│   └── test_differential.py # Differential/robustness tests
│
├── deploy/                  # Monitoring configuration
│   ├── grafana/             # Grafana dashboards
│   ├── prometheus/          # Prometheus config
│   ├── loki/                # Log aggregation
│   └── promtail/            # Log collector
│
├── infra/                   # Infrastructure code
│   ├── terraform/           # AWS provisioning
│   └── ansible/             # Server configuration
│
├── scripts/
│   └── test_client.py       # API test script
│
├── models/                  # Saved models go here
├── docker-compose.yml       # Local Docker
├── docker-compose.prod.yml  # Production Docker with monitoring
├── Dockerfile              # Container image
├── pyproject.toml          # Project config and dependencies
├── requirements.txt        # Python packages
└── data.csv                # Training data
```

## Docker

### Local Development

```bash
docker-compose up
```

Runs on `http://localhost:8000`

### Production with Monitoring

```bash
docker-compose -f docker-compose.prod.yml up
```

This starts:
- **API** - `http://localhost:8000`
- **Grafana** - `http://localhost:3000` (monitoring dashboard)
- **Prometheus** - `http://localhost:9090` (metrics)
- **Loki** - `http://localhost:3100` (logs)

## Infrastructure & Deployment

### Architecture Overview

The project is deployed as a containerized application with a complete monitoring stack:

- **Application (FastAPI)** – ML inference service
- **Grafana** – visualization dashboard
- **Prometheus** – metrics collection  
- **Loki** – log aggregation

Deployment is fully automated using:

- **Terraform** → provisions EC2 instance and security groups
- **Ansible** → installs Docker and configures services
- **Docker Compose** → orchestrates all containers

### Deployment Flow

1. Build and push Docker image (GitHub Actions or manually)
2. Provision EC2 instance using Terraform
3. Run Ansible playbook to:
   - Install Docker and Docker Compose
   - Pull the application image
   - Start all services
4. Access services via the public EC2 IP

### Infrastructure Directory Structure

```
infra/
├── terraform/           # EC2 provisioning
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ansible/            # Deployment automation
│   ├── playbook.yml
│   └── inventory.ini
└── README.md           # Detailed infrastructure docs
```

---

## Deploying to AWS

### What You Need

- AWS account
- Terraform >= 1.6.0
- Ansible >= 2.12
- SSH key: `telco-key.pem`
- Docker Hub account with a repo called `pipeline-project`

### How to Deploy

1. **Build and Push Docker Image**

   Push code to GitHub `main` branch. GitHub Actions automatically builds and pushes the image.

   ```bash
   git add .
   git commit -m "Deploy"
   git push origin main
   ```

2. **Create AWS Infrastructure**

   ```bash
   cd infra/terraform
   terraform init
   terraform apply \
     -var aws_region="eu-north-1" \
     -var instance_type="t3.micro" \
     -var key_name="telco-key"
   ```

   This gives you an EC2 instance with a public IP.

3. **Update Ansible**

   Edit `infra/ansible/inventory.ini`:
   ```ini
   [app]
   16.171.78.151 ansible_user=ubuntu ansible_ssh_private_key_file=~/telco-key.pem
   ```

   Replace the IP with your actual EC2 IP.

4. **Deploy the Application**

   ```bash
   cd ../ansible
   export APP_IMAGE="docker.io/YOUR_USERNAME/pipeline-project:latest"
   export GRAFANA_ADMIN_PASSWORD="your-password"
   ansible-playbook -i inventory.ini playbook.yml
   ```

5. **Verify It Works**

   ```bash
   curl http://<YOUR_IP>:8000/health
   ```

### Access Your Deployment

- API: `http://16.171.78.151:8000`
- Grafana: `http://16.171.78.151:3000` (admin / your-password)
- Prometheus: `http://16.171.78.151:9090`
- Loki: `http://16.171.78.151:3100`

## Live Deployment (Demo)

The application is currently deployed and available at:

- **Application**: http://16.171.78.151:8000/
- **Health Check**: http://16.171.78.151:8000/health
- **Metrics**: http://16.171.78.151:8000/metrics
- **Grafana Dashboard**: http://16.171.78.151:3000 (admin / MyStrongPass_2026!)
- **Prometheus**: http://16.171.78.151:9090/
- **Loki Logs**: http://16.171.78.151:3100/ready

### SSH to the Server

```bash
ssh -i ~/telco-key.pem ubuntu@16.171.78.151

# Check containers
docker ps

# View logs
docker-compose -f /opt/pipeline-project/repo/docker-compose.prod.yml logs -f

# Restart services
docker-compose -f /opt/pipeline-project/repo/docker-compose.prod.yml restart
```

## Data Processing

### ColumnDropper
Removes columns without learning anything:
```python
from pipeline_project.data_processing import ColumnDropper

dropper = ColumnDropper(columns=['col1', 'col2'])
X_clean = dropper.fit_transform(X)
```

### MeanImputer
Learns means during training, then fills missing values:
```python
from pipeline_project.data_processing import MeanImputer

imputer = MeanImputer()
X_clean = imputer.fit_transform(X)
print(imputer.means)  # Check the learned values
```

## Monitoring

After deploying to AWS, you can check metrics and logs in Grafana:

- Request rate: `sum(rate(pipeline_http_requests_total[5m]))`
- Error rate: `sum(rate(pipeline_http_requests_total{status=~"5.."}[5m]))`
- Response time (95th percentile): `histogram_quantile(0.95, rate(pipeline_http_request_duration_seconds_bucket[5m]))`

### Deployment Results

The deployment creates a fully working cloud-based system with:

- ML inference API for income predictions
- Real-time monitoring (metrics collection + log aggregation)
- Visualization dashboard (Grafana)
- Scalable infrastructure on AWS EC2

This completes the full production deployment of the income classification pipeline with monitoring and observability.

## Dependencies

- `scikit-learn` - machine learning
- `pandas` - data manipulation
- `fastapi` - web framework
- `uvicorn` - ASGI server
- `prometheus-client` - metrics
- `pytest` - testing

See `pyproject.toml` for complete list.

## License

INSA Project 2025-2026

---

**Author:** Mariia Lykhoshva

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