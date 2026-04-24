from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from .data_processing import ColumnDropper, MeanImputer

def create_pipeline():
    pipeline = Pipeline([
        ("drop", ColumnDropper(columns=["unnecessary_column"])),
        ("impute", MeanImputer()),
        ("model", LogisticRegression())
    ])
    return pipeline
