import pandas as pd
import joblib
from pipeline_project.utils import load_model
from pipeline_project.train import preprocess


def predict():
    model = load_model()
    columns = joblib.load("models/columns.pkl")

    df = pd.read_csv("data.csv").head(5)

    df = preprocess(df)

    if "income" in df.columns:
        df = df.drop("income", axis=1)

    df = df.reindex(columns=columns, fill_value=0)

    preds = model.predict(df)
    probs = model.predict_proba(df)

    print("Predictions:", preds)
    print("Probabilities:", probs)
    


if __name__ == "__main__":
    predict()