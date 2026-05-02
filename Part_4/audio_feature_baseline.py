import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


NON_FEATURE_COLUMNS = ["id_EXIST", "video", "wav_path"]
LABEL_COLUMNS = ["label_task3_1", "label_task3_2", "label_task3_3"]


def load_csv(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)


def find_columns(columns, keywords):
    keywords = [keyword.lower() for keyword in keywords]
    return [
        column
        for column in columns
        if any(keyword in column.lower() for keyword in keywords)
    ]


def inspect_feature_completeness(features_df):
    print("=" * 80)
    print("PART 1 - FEATURE COMPLETENESS")
    print("=" * 80)
    print(f"Dataset shape: {features_df.shape}")
    print("\nColumn names:")
    for column in features_df.columns:
        print(f"- {column}")

    columns = features_df.columns
    groups = {
        "MFCC": find_columns(columns, ["mfcc"]),
        "Delta MFCC": find_columns(columns, ["delta"]),
        "Delta-Delta": find_columns(columns, ["delta2", "delta_delta"]),
        "Spectral": find_columns(
            columns,
            ["spectral_centroid", "spectral_bandwidth", "spectral_rolloff"],
        ),
        "Temporal": find_columns(columns, ["zero_crossing_rate", "zcr"]),
        "Energy": find_columns(columns, ["rms", "energy"]),
        "Pitch": find_columns(columns, ["f0", "pitch"]),
    }

    print("\nDetected feature groups:")
    for group_name, group_columns in groups.items():
        present = len(group_columns) > 0
        print(f"- {group_name}: present={present}, columns_found={len(group_columns)}")

    required_groups = ["MFCC", "Spectral", "Energy"]
    missing_required = [
        group_name for group_name in required_groups if len(groups[group_name]) == 0
    ]
    for group_name in missing_required:
        print(f"WARNING: Missing required feature group: {group_name}")


def merge_features_and_labels(features_df, labels_df):
    missing_feature_keys = {"id_EXIST"} - set(features_df.columns)
    missing_label_columns = set(["id_EXIST"] + LABEL_COLUMNS) - set(labels_df.columns)

    if missing_feature_keys:
        raise ValueError(f"Feature CSV is missing columns: {sorted(missing_feature_keys)}")
    if missing_label_columns:
        raise ValueError(f"Labels CSV is missing columns: {sorted(missing_label_columns)}")

    merged_df = features_df.merge(
        labels_df[["id_EXIST"] + LABEL_COLUMNS],
        on="id_EXIST",
        how="inner",
    )

    print("\n" + "=" * 80)
    print("PART 3 - LABELS")
    print("=" * 80)
    print(f"Merged dataset shape: {merged_df.shape}")

    if len(merged_df) == 0:
        raise ValueError("Merge produced 0 rows. Check that id_EXIST values match.")

    for label_column in LABEL_COLUMNS:
        print(f"\nClass distribution for {label_column}:")
        print(merged_df[label_column].value_counts(dropna=False).to_string())

    return merged_df


def build_feature_matrix(merged_df):
    feature_df = merged_df.drop(
        columns=[
            column
            for column in NON_FEATURE_COLUMNS + LABEL_COLUMNS
            if column in merged_df.columns
        ],
        errors="ignore",
    )
    feature_df = feature_df.select_dtypes(include=[np.number])

    if feature_df.shape[1] == 0:
        raise ValueError("No numeric feature columns remain after cleaning.")

    print("\n" + "=" * 80)
    print("PART 2 - DATA CLEANING")
    print("=" * 80)
    print(f"Numeric feature matrix shape before split-time cleaning: {feature_df.shape}")
    print("Non-feature columns removed:", ", ".join(NON_FEATURE_COLUMNS))
    print("Missing values will be imputed with train-set means inside each split.")
    print("Constant features will be removed with train-set variance inside each split.")

    return feature_df


def make_models():
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        ),
        "SVM_RBF": SVC(
            kernel="rbf",
            class_weight="balanced",
            random_state=42,
        ),
    }


def train_and_evaluate_task(X, y, task_name, label_column):
    print("\n" + "=" * 80)
    print(f"PART 4/5 - {task_name}: {label_column}")
    print("=" * 80)

    valid_mask = y.notna()
    X = X.loc[valid_mask]
    y = y.loc[valid_mask].astype(str)

    class_counts = y.value_counts()
    if len(class_counts) < 2:
        print(f"Skipping {task_name}: fewer than 2 classes after dropping missing labels.")
        return []
    if class_counts.min() < 2:
        print(
            f"Skipping {task_name}: stratified split requires at least 2 samples per class."
        )
        print(class_counts.to_string())
        return []

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    average = "binary" if label_column == "label_task3_1" else "macro"
    positive_label = "YES" if label_column == "label_task3_1" else None
    results = []

    for model_name, model in make_models().items():
        pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="mean")),
                ("variance_threshold", VarianceThreshold()),
                ("scaler", StandardScaler()),
                ("model", model),
            ]
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        if average == "binary":
            f1 = f1_score(y_test, y_pred, average=average, pos_label=positive_label)
        else:
            f1 = f1_score(y_test, y_pred, average=average)

        print(f"\nModel: {model_name}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 ({average}): {f1:.4f}")
        print("Classification report:")
        print(classification_report(y_test, y_pred, zero_division=0))

        results.append(
            {
                "task": task_name,
                "label": label_column,
                "model": model_name,
                "accuracy": accuracy,
                "f1": f1,
            }
        )

    return results


def print_summary(all_results):
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if not all_results:
        print("No task results available.")
        return

    results_df = pd.DataFrame(all_results)
    print("\nAll results:")
    print(
        results_df.sort_values(["task", "model"])[
            ["task", "model", "accuracy", "f1"]
        ].to_string(index=False)
    )

    task_summary = (
        results_df.groupby("task", as_index=False)["f1"]
        .max()
        .sort_values("f1", ascending=False)
    )
    best_task = task_summary.iloc[0]
    worst_task = task_summary.iloc[-1]

    print(
        f"\nBest audio task by best model F1: {best_task['task']} "
        f"(F1={best_task['f1']:.4f})"
    )
    print(
        f"Worst audio task by best model F1: {worst_task['task']} "
        f"(F1={worst_task['f1']:.4f})"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train classical ML baselines on clip-level audio features."
    )
    parser.add_argument(
        "--features",
        default="clip_level_features.csv",
        help="Path to clip-level audio feature CSV.",
    )
    parser.add_argument(
        "--labels",
        required=True,
        help="Path to labels CSV containing id_EXIST and task labels.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    features_df = load_csv(args.features)
    labels_df = load_csv(args.labels)

    inspect_feature_completeness(features_df)
    merged_df = merge_features_and_labels(features_df, labels_df)
    X = build_feature_matrix(merged_df)

    tasks = {
        "Task 3.1": "label_task3_1",
        "Task 3.2": "label_task3_2",
        "Task 3.3": "label_task3_3",
    }

    all_results = []
    for task_name, label_column in tasks.items():
        all_results.extend(
            train_and_evaluate_task(
                X=X,
                y=merged_df[label_column],
                task_name=task_name,
                label_column=label_column,
            )
        )

    print_summary(all_results)


if __name__ == "__main__":
    main()
