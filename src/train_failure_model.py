
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


project_root = Path(__file__).resolve().parent.parent
data_path = project_root / "data" / "ai4i2020.csv"
models_path = project_root / "models"

df = pd.read_csv(data_path)

numeric_features = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

categorical_features = ["Type"]
feature_columns = categorical_features + numeric_features
target_column = "Machine failure"

X = df[feature_columns]
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", "passthrough", numeric_features),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
    ]
)

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=300,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)

print("Training the machine failure prediction model...")
model.fit(X_train, y_train)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("\n--- Model Evaluation ---")
print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")

print("\n--- Classification Report ---")
print(classification_report(y_test, predictions, zero_division=0))

print("\n--- Confusion Matrix ---")
print(confusion_matrix(y_test, predictions))

print(
    "\nAverage Precision Score: "
    f"{average_precision_score(y_test, probabilities):.4f}"
)

models_path.mkdir(parents=True, exist_ok=True)
model_path = models_path / "failure_model.joblib"
joblib.dump(model, model_path)

print(f"\nModel saved to: {model_path}")
