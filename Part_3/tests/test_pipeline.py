import pandas as pd
from pipeline_project.pipeline import create_pipeline

def test_pipeline_runs():
    df = pd.DataFrame({
        "feature1": [1, 2, 3],
        "feature2": [4, 5, 6],
        "target": [0, 1, 0]
    })

    X = df.drop("target", axis=1)
    y = df["target"]

    pipeline = create_pipeline()
    pipeline.fit(X, y)

    preds = pipeline.predict(X)

    assert len(preds) == len(y)
