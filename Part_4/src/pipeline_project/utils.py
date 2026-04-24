import joblib

def load_model(path="models/model.pkl"):
    return joblib.load(path)
