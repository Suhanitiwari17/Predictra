
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split


project_root = Path(__file__).resolve().parents[1]

data_path = project_root / "data" / "ai4i2020.csv"
model_path = project_root / "models" / "failure_model.joblib"

df = pd.read_csv(data_path)

feature_columns = [
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

X = df[feature_columns]
y = df["Machine failure"]

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

model = joblib.load(model_path)
probabilities = model.predict_proba(X_test)[:, 1]

print("\n--- Threshold Experiment ---")

for threshold in [0.5, 0.4, 0.3, 0.2, 0.1]:
    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    precision = precision_score(
        y_test, predictions, zero_division=0
    )
    recall = recall_score(
        y_test, predictions, zero_division=0
    )
    f1 = f1_score(
        y_test, predictions, zero_division=0
    )

    print(f"\nThreshold: {threshold:.1f}")
    print(f"Failure precision: {precision:.2%}")
    print(f"Failure recall:    {recall:.2%}")
    print(f"Failure F1-score:  {f1:.3f}")
    print(f"Actual failures caught: {tp}/68")
    print(f"Actual failures missed: {fn}")
    print(f"False alarms: {fp}")
    print(f"Correct normal predictions: {tn}")
