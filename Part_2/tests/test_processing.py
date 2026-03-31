import pandas as pd
from pipeline_project.data_processing import ColumnDropper, MeanImputer

def test_column_dropper():
    df = pd.DataFrame({"a": [1], "b": [2]})
    transformer = ColumnDropper(columns=["b"])
    result = transformer.transform(df)
    assert "b" not in result.columns

def test_mean_imputer():
    df = pd.DataFrame({"a": [1, None, 3]})
    imputer = MeanImputer()
    imputer.fit(df)
    result = imputer.transform(df)
    assert result.isna().sum().sum() == 0
