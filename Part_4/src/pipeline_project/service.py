from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from pipeline_project.schemas import PredictionRequest, PredictionResponse
from pipeline_project.train import preprocess
from pipeline_project.train import train
from pipeline_project.utils import load_model


def _candidate_roots() -> list[Path]:
    cwd = Path.cwd().resolve()
    file_path = Path(__file__).resolve()
    candidates = [
        cwd,
        cwd.parent,
        file_path.parents[2],
        file_path.parents[1],
    ]

    seen = set()
    unique_candidates = []
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)

    return unique_candidates


def _project_root() -> Path:
    for root in _candidate_roots():
        if (root / "models" / "model.pkl").exists() and (root / "models" / "columns.pkl").exists():
            return root
    return Path.cwd().resolve()


@lru_cache(maxsize=1)
def _load_artifacts() -> tuple:
    project_root = _project_root()
    model_path = project_root / "models" / "model.pkl"
    columns_path = project_root / "models" / "columns.pkl"

    if not model_path.exists() or not columns_path.exists():
        train(project_root)

    try:
        model = load_model(str(model_path))
        columns = joblib.load(columns_path)
    except Exception:
        train(project_root)
        model = load_model(str(model_path))
        columns = joblib.load(columns_path)
    return model, columns


def predict_from_request(payload: PredictionRequest) -> PredictionResponse:
    model, columns = _load_artifacts()

    raw_df = pd.DataFrame([payload.model_dump(by_alias=True)])
    processed_df = preprocess(raw_df)
    features = processed_df.reindex(columns=columns, fill_value=0)

    try:
        prediction = bool(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
    except Exception:
        train(_project_root())
        _load_artifacts.cache_clear()
        model, columns = _load_artifacts.__wrapped__()
        features = processed_df.reindex(columns=columns, fill_value=0)
        prediction = bool(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
    return PredictionResponse(prediction=prediction, probability=probability)
