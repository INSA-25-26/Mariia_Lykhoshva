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