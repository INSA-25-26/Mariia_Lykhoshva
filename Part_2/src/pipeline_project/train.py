import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


def load_data():
    candidates = [Path("data.csv"), *Path.cwd().glob("**/data.csv")]
    data_path = next((p for p in candidates if p.exists()), None)
    
    if data_path is None:
        raise FileNotFoundError("data.csv not found")
    
    return pd.read_csv(data_path)


def preprocess(df):
    df["income"] = df["income"].str.strip() == ">50K"

    df["capital.gain.log"] = np.log1p(df["capital.gain"])
    df["capital.loss.log"] = np.log1p(df["capital.loss"])
    df["work_hours_age_ratio"] = df["hours.per.week"] / df["age"]

    df["native.country_US"] = df["native.country"] == "United-States"
    df["is_male"] = df["sex"] == "Male"

    df.drop(["native.country", "sex"], axis=1, inplace=True)

    df = df.replace(r"^\s*\?\s*$", np.nan, regex=True)


    for col in df.select_dtypes(include=["object", "string"]):
        df[col] = df[col].fillna(df[col].mode()[0])

    for col in df.select_dtypes(include=np.number):
        df[col] = df[col].fillna(df[col].median())

    df.drop(
        ["fnlwgt", "relationship", "education.num", "capital.gain", "capital.loss"],
        axis=1,
        inplace=True
    )

    df = pd.get_dummies(
        df,
        columns=["workclass", "education", "occupation", "marital.status", "race"],
        drop_first=True
    )

    return df


def train():
    df = load_data()
    df = preprocess(df)

    X = df.drop("income", axis=1)
    y = df["income"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000))
    ])


    pipeline.fit(X_train, y_train)
    Path("models").mkdir(exist_ok=True)

    joblib.dump(pipeline, "models/model.pkl")
    joblib.dump(X_train.columns, "models/columns.pkl")


if __name__ == "__main__":
    train()