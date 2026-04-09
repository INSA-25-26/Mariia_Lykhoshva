from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd

class ColumnDropper(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.columns, errors="ignore")

class MeanImputer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.means = None

    def fit(self, X, y=None):
        self.means = X.mean()
        return self

    def transform(self, X):
        return X.fillna(self.means)
