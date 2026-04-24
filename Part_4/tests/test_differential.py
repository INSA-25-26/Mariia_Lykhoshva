import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import pytest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from pipeline_project.pipeline import create_pipeline
from pipeline_project.data_processing import ColumnDropper, MeanImputer


class TestPipelineDeterminism:
    
    def test_same_input_same_output(self):
        X = pd.DataFrame({
            'feature1': [1.0, 2.0, 3.0, 4.0],
            'feature2': [2.0, 4.0, 6.0, 8.0],
        })
        y = pd.Series([0, 1, 0, 1])

        pipeline = create_pipeline()
        pipeline.fit(X, y)

        preds1 = pipeline.predict(X)
        
        preds2 = pipeline.predict(X)

        np.testing.assert_array_equal(preds1, preds2)

    def test_probabilities_consistency(self):
        X = pd.DataFrame({
            'feature1': np.arange(10, dtype=float),
            'feature2': np.arange(10, 20, dtype=float),
        })
        y = pd.Series([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

        pipeline = create_pipeline()
        pipeline.fit(X, y)

        probs1 = pipeline.predict_proba(X)
        probs2 = pipeline.predict_proba(X)

        np.testing.assert_array_almost_equal(probs1, probs2, decimal=10)


class TestPipelineConsistency:
    
    def test_pipeline_on_clean_data(self):
        X = pd.DataFrame({
            'feature1': [1.0, 2.0, 3.0, 4.0, 5.0],
            'feature2': [10.0, 20.0, 30.0, 40.0, 50.0],
        })
        y = pd.Series([0, 0, 1, 1, 1], dtype=int)

        pipeline = create_pipeline()
        pipeline.fit(X, y)
        
        preds = pipeline.predict(X)
        
        assert all(pred in [0, 1] for pred in preds)
        assert len(preds) == len(y)

    def test_pipeline_with_different_sizes(self):
        X_large = pd.DataFrame({
            'feature1': np.linspace(0, 10, 100),
            'feature2': np.linspace(0, 20, 100),
        })
        y_large = pd.Series([i % 2 for i in range(100)], dtype=int)

        pipeline = create_pipeline()
        pipeline.fit(X_large, y_large)
        
        X_small = pd.DataFrame({
            'feature1': [1.0, 5.0, 9.0],
            'feature2': [2.0, 10.0, 18.0],
        })
        
        preds = pipeline.predict(X_small)
        assert len(preds) == len(X_small)


class TestMeanImputerDifferential:
    
    def test_imputer_means_calculation(self):
        X = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [10, 20, 30, None, None],
        })
        
        imputer = MeanImputer()
        imputer.fit(X)
        
        assert imputer.means['a'] == 3.0
        assert imputer.means['b'] == 20.0

    def test_imputer_consistent_filling(self):
        X = pd.DataFrame({
            'a': [1, None, 3],
            'b': [None, 20, 30],
        })
        
        imputer = MeanImputer()
        imputer.fit(X)
        
        result1 = imputer.transform(X.copy())
        result2 = imputer.transform(X.copy())
        result3 = imputer.transform(X.copy())
        
        pd.testing.assert_frame_equal(result1, result2)
        pd.testing.assert_frame_equal(result2, result3)


class TestColumnDropperDifferential:
    
    def test_dropper_removes_specified_columns(self):
        X = pd.DataFrame({
            'keep_a': [1, 2, 3],
            'drop_b': [4, 5, 6],
            'keep_c': [7, 8, 9],
        })
        
        dropper = ColumnDropper(columns=['drop_b'])
        result = dropper.transform(X)
        
        assert 'keep_a' in result.columns
        assert 'drop_b' not in result.columns
        assert 'keep_c' in result.columns

    def test_dropper_handles_nonexistent_columns(self):
        X = pd.DataFrame({
            'a': [1, 2],
            'b': [3, 4],
        })
        
        dropper = ColumnDropper(columns=['nonexistent', 'a'])
        result = dropper.transform(X)
        
        assert 'a' not in result.columns
        assert 'b' in result.columns


class TestPipelineRobustness:
    
    def test_pipeline_with_all_zeros(self):
        X = pd.DataFrame({
            'feature1': [0.0, 0.0, 0.0],
            'feature2': [0.0, 0.0, 0.0],
        })
        y = pd.Series([0, 1, 0], dtype=int)
        
        pipeline = create_pipeline()
        pipeline.fit(X, y)
        
        preds = pipeline.predict(X)
        assert len(preds) == len(y)

    def test_pipeline_with_identical_features(self):
        X = pd.DataFrame({
            'feature1': [1.0] * 5,
            'feature2': [1.0] * 5,
        })
        y = pd.Series([0, 0, 1, 1, 1], dtype=int)
        
        pipeline = create_pipeline()
        pipeline.fit(X, y)
        
        preds = pipeline.predict(X)
        assert all(pred in [0, 1] for pred in preds)

    def test_pipeline_with_large_values(self):
        X = pd.DataFrame({
            'feature1': [1e6, 2e6, 3e6, 4e6],
            'feature2': [1e5, 2e5, 3e5, 4e5],
        })
        y = pd.Series([0, 0, 1, 1], dtype=int)
        
        pipeline = create_pipeline()
        pipeline.fit(X, y)
        
        preds = pipeline.predict(X)
        assert all(pred in [0, 1] for pred in preds)


class TestPredictVsActual:
    
    def test_model_performance_bounds(self):
        X = pd.DataFrame({
            'feature1': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'feature2': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
        })
        y = pd.Series([0, 0, 0, 0, 0, 1, 1, 1, 1, 1], dtype=int)
        
        pipeline = create_pipeline()
        pipeline.fit(X, y)
        
        preds = pipeline.predict(X)
        accuracy = (preds == y).mean()
        
        assert accuracy >= 0.5
