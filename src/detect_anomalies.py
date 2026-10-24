
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


project_root = Path(__file__).resolve().parent.parent
data_path = project_root / "data" / "ai4i2020.csv"
models_path = project_root / "models"

df = pd.read_csv(data_path)

sensor_features = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

X = df[sensor_features]
normal_readings = X[df["Machine failure"] == 0]

detector = Pipeline([
    ("scaler", StandardScaler()),
    ("isolation_forest", IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42,
    )),
])

print("Training anomaly detection model...")
detector.fit(normal_readings)

df["Anomaly"] = detector.predict(X) == -1

print("\n--- Anomaly Detection Results ---")
print(f"Total records: {len(df)}")
print(f"Anomalies detected: {df['Anomaly'].sum()}")
print(f"Normal-looking records: {(~df['Anomaly']).sum()}")

print("\n--- Anomalies vs Actual Failure Labels ---")
print(pd.crosstab(
    df["Machine failure"],
    df["Anomaly"],
    rownames=["Actual failure"],
    colnames=["Detected anomaly"],
))

models_path.mkdir(parents=True, exist_ok=True)
model_path = models_path / "anomaly_detector.joblib"
joblib.dump(detector, model_path)

print(f"\nModel saved to: {model_path}")
