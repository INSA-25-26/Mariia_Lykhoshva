# Income Classification Project - Complete Overview

This is a machine learning course project where we build a pipeline to predict income levels. The project is split into 4 parts, each building on the previous one.

## Project Parts

### Part 1: Data Exploration
- **Goal**: Understand the dataset
- **Location**: `Part_1/`
- **What's done here**: 
  - Load and explore the adult income dataset
  - Check data types, missing values, distributions
  - Basic statistical analysis
  - Jupyter notebook with visualizations

### Part 2: Basic Pipeline
- **Goal**: Build a working ML pipeline
- **Location**: `Part_2/`
- **What's done here**:
  - Data preprocessing (handling missing values, encoding categories)
  - Feature engineering
  - Model training with scikit-learn
  - Save/load trained models
  - Basic unit tests and differential tests

### Part 3: API and Testing
- **Goal**: Make the pipeline accessible through an API
- **Location**: `Part_3/`
- **What's done here**:
  - Add FastAPI REST API
  - Create endpoints for predictions and health checks
  - Add more comprehensive tests (unit + integration)
  - Better project structure with separate modules

### Part 4: Production Deployment
- **Goal**: Deploy to production on AWS with monitoring
- **Location**: `Part_4/`
- **What's done here**:
  - Docker containerization
  - Docker Compose for local and production setups
  - Terraform for AWS infrastructure
  - Ansible for server configuration
  - Prometheus + Grafana for monitoring
  - Complete test suite

## Quick Access

### I Want to...

**...understand the data**
```bash
cd Part_1
jupyter notebook zad.ipynb
```

**...run the basic pipeline**
```bash
cd Part_2
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -e .
python -m pipeline_project.train
python -m pipeline_project.predict
```

**...test the API locally**
```bash
cd Part_3
pip install -e .
python -m pipeline_project.main
# In another terminal:
curl http://localhost:8000/health
```

**...deploy to AWS**
```bash
cd Part_4
# See Part_4/README.md for detailed instructions
```

**...run tests**
```bash
cd Part_4  # or any part that has tests
pytest tests/ -v
```

## General Project Structure

Each part has a similar structure:

```
Part_X/
├── src/pipeline_project/
│   ├── train.py
│   ├── predict.py
│   ├── pipeline.py
│   ├── data_processing.py
│   ├── utils.py
│   └── [additional modules in later parts]
├── tests/
│   ├── test_pipeline.py
│   ├── test_processing.py
│   └── test_differential.py
├── models/
├── data.csv
├── pyproject.toml
└── README.md
```

Part 4 has extra folders for infrastructure and monitoring:
```
Part_4/
├── [basic structure above]
├── deploy/          # Monitoring configs
├── infra/           # Infrastructure as Code
├── scripts/         # Utility scripts
├── docker-compose.yml
├── Dockerfile
└── [more deployment files]
```

## Technologies Used

- **Python 3.11+** - Main language
- **scikit-learn** - Machine learning
- **pandas** - Data handling
- **FastAPI** - REST API (Part 3+)
- **Pytest** - Testing
- **Docker** - Containerization (Part 4)
- **Terraform** - Infrastructure (Part 4)
- **Ansible** - Configuration management (Part 4)
- **Prometheus & Grafana** - Monitoring (Part 4)

## Development Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Virtual environment tool (venv)

### Common Steps

1. Navigate to the part you want to work with:
   ```bash
   cd Part_4  # or whichever part
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. For development with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Testing Strategy

The project uses three types of tests:

1. **Unit Tests** - Check individual components work correctly
   ```bash
   pytest tests/test_processing.py -v
   ```

2. **Integration Tests** - Check components work together
   ```bash
   pytest tests/test_pipeline.py -v
   ```

3. **Differential Tests** - Verify model is stable and robust
   ```bash
   pytest tests/test_differential.py -v
   ```

Run all tests:
```bash
pytest tests/ -v
```

## The ML Model

- **Task**: Binary classification (income > 50k or ≤ 50k)
- **Algorithm**: Logistic Regression (through scikit-learn pipeline)
- **Input Features**: Demographic data (age, education, occupation, etc.)
- **Data Source**: Adult Income Dataset

The pipeline automatically:
1. Handles categorical variables (encoding)
2. Handles numerical variables (imputation, scaling)
3. Trains the classifier
4. Saves everything needed for production

## Notes

- Each part has its own `pyproject.toml` with dependencies
- Each part can run independently
- The data file is `data.csv` in each directory
- Models are saved in `models/` folder as `.pkl` files
- All parts use the same package name `pipeline_project`

## For More Details

- **Part 2 specifics**: See `Part_2/README.md`
- **Part 3 specifics**: See `Part_3/README.md`
- **Part 4 with deployment**: See `Part_4/README.md`

## Troubleshooting

**Import errors after pip install?**
```bash
pip install -e . --force-reinstall --no-cache-dir
```

**Tests failing?**
```bash
# Make sure you're in the right directory
cd Part_4
# Make sure virtual env is activated
pytest tests/ -v
```

**Docker issues?**
```bash
# In Part_4
docker-compose down  # Stop everything
docker-compose up --build  # Rebuild and start
```

## Live Demo (Part 4 Deployment)

The complete project is deployed on AWS and publicly available:

- **Income Predictor API**: http://16.171.78.151:8000/
- **Health Status**: http://16.171.78.151:8000/health
- **Prometheus Metrics**: http://16.171.78.151:8000/metrics
- **Grafana Dashboard**: http://16.171.78.151:3000
  - Username: `admin`
  - Password: `MyStrongPass_2026!`
- **Prometheus UI**: http://16.171.78.151:9090/
- **Loki Logs**: http://16.171.78.151:3100/ready

---

**Course**: INSA 2025-2026  
**Project Author**: Mariia Lykhoshva
