
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
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

# Reserve 20% for the final test.
X_train_val, X_test, y_train_val, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# Split the remaining data into 60% training and 20% validation.
X_train, X_val, y_train, y_val = train_test_split(
    X_train_val,
    y_train_val,
    test_size=0.25,
    random_state=42,
    stratify=y_train_val,
)

model_template = joblib.load(model_path)
model = clone(model_template)
model.fit(X_train, y_train)

validation_probabilities = model.predict_proba(X_val)[:, 1]

# Choose the threshold using validation data only.
thresholds = np.arange(0.10, 0.91, 0.05)
validation_results = []

for threshold in thresholds:
    predictions = (
        validation_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_val, predictions, zero_division=0
    )
    recall = recall_score(
        y_val, predictions, zero_division=0
    )
    f1 = f1_score(
        y_val, predictions, zero_division=0
    )

    validation_results.append(
        (f1, precision, threshold, recall)
    )

best_f1, best_precision, best_threshold, best_recall = max(
    validation_results
)

print("\n--- Validation Results ---")
print(f"Selected threshold: {best_threshold:.2f}")
print(f"Precision: {best_precision:.2%}")
print(f"Recall: {best_recall:.2%}")
print(f"F1-score: {best_f1:.3f}")

# Evaluate once on the separate test set.
test_probabilities = model.predict_proba(X_test)[:, 1]

print("\n--- Final Test Results ---")

for threshold in [0.50, best_threshold]:
    predictions = (test_probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    ).ravel()

    print(f"\nThreshold: {threshold:.2f}")
    print(
        f"Precision: "
        f"{precision_score(y_test, predictions, zero_division=0):.2%}"
    )
    print(
        f"Recall: "
        f"{recall_score(y_test, predictions, zero_division=0):.2%}"
    )
    print(
        f"F1-score: "
        f"{f1_score(y_test, predictions, zero_division=0):.3f}"
    )
    print(f"Failures caught: {tp}")
    print(f"Failures missed: {fn}")
    print(f"False alarms: {fp}")
    print(f"Correct normal predictions: {tn}")

print(
    "\nTest average precision: "
    f"{average_precision_score(y_test, test_probabilities):.4f}"
)

print("\nOriginal saved model was not modified.")
