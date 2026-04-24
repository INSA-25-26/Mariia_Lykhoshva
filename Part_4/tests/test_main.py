from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pipeline_project.main import app


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def require_model_artifacts() -> None:
    model_path = Path("models/model.pkl")
    columns_path = Path("models/columns.pkl")
    if not model_path.exists() or not columns_path.exists():
        pytest.skip("Model artifacts are missing. Run training before integration tests.")


def payload() -> dict:
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


def test_predict_valid_request_returns_200() -> None:
    response = client.post("/predict", json=payload())

    assert response.status_code == 200


def test_root_returns_html_interface() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "prediction-form" in response.text


def test_metrics_endpoint_returns_prometheus_text() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "pipeline_http_requests_total" in response.text


def test_predict_invalid_request_returns_422() -> None:
    bad = payload()
    bad.pop("age")

    response = client.post("/predict", json=bad)

    assert response.status_code == 422


def test_predict_negative_age_returns_422() -> None:
    bad = payload()
    bad["age"] = -5

    response = client.post("/predict", json=bad)

    assert response.status_code == 422


def test_predict_response_structure() -> None:
    response = client.post("/predict", json=payload())

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"prediction", "probability"}
    assert isinstance(body["prediction"], bool)
    assert isinstance(body["probability"], float)
    assert 0.0 <= body["probability"] <= 1.0
