from pathlib import Path

from fastapi.testclient import TestClient

from pipeline_project.api import app
from pipeline_project.train import train


def _ensure_artifacts() -> None:
    model_path = Path("models/model.pkl")
    columns_path = Path("models/columns.pkl")
    if not model_path.exists() or not columns_path.exists():
        train()


def _payload() -> dict:
    return {
        "age": 39,
        "workclass": "Private",
        "fnlwgt": 77516,
        "education": "Bachelors",
        "education.num": 13,
        "marital.status": "Never-married",
        "occupation": "Adm-clerical",
        "relationship": "Not-in-family",
        "race": "White",
        "sex": "Male",
        "capital.gain": 2174,
        "capital.loss": 0,
        "hours.per.week": 40,
        "native.country": "United-States",
    }


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_success():
    _ensure_artifacts()
    client = TestClient(app)
    response = client.post("/predict", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert "prediction" in body
    assert "probability" in body
    assert isinstance(body["prediction"], bool)
    assert 0.0 <= body["probability"] <= 1.0


def test_predict_endpoint_validation_error():
    _ensure_artifacts()
    client = TestClient(app)
    bad_payload = _payload()
    bad_payload.pop("age")

    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
