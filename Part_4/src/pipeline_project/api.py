from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from pipeline_project.train import preprocess
from pipeline_project.utils import load_model


class PredictionInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    age: int
    workclass: str
    fnlwgt: int
    education: str
    education_num: int = Field(alias="education.num")
    marital_status: str = Field(alias="marital.status")
    occupation: str
    relationship: str
    race: str
    sex: str
    capital_gain: int = Field(alias="capital.gain")
    capital_loss: int = Field(alias="capital.loss")
    hours_per_week: int = Field(alias="hours.per.week")
    native_country: str = Field(alias="native.country")


class PredictionOutput(BaseModel):
    prediction: bool
    probability: float


@lru_cache(maxsize=1)
def _artifacts() -> tuple:
    model_path = Path("models/model.pkl")
    columns_path = Path("models/columns.pkl")

    if not model_path.exists() or not columns_path.exists():
        raise FileNotFoundError("Model artifacts are missing. Run training first.")

    model = load_model(str(model_path))
    columns = joblib.load(columns_path)
    return model, columns


app = FastAPI(title="Pipeline Project API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput) -> PredictionOutput:
    try:
        model, columns = _artifacts()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    raw_df = pd.DataFrame([payload.model_dump(by_alias=True)])
    processed_df = preprocess(raw_df)
    features = processed_df.reindex(columns=columns, fill_value=0)

    prediction = bool(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])

    return PredictionOutput(prediction=prediction, probability=probability)
