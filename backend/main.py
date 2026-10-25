
import os
from pathlib import Path

import sqlite3
from datetime import datetime, timezone

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware


project_root = Path(__file__).resolve().parent.parent
models_path = project_root / "models"

database_path = project_root / "data" / "predictions.db"


def initialize_database():
    with sqlite3.connect(database_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                machine_type TEXT NOT NULL,
                air_temperature REAL NOT NULL,
                process_temperature REAL NOT NULL,
                rotational_speed REAL NOT NULL,
                torque REAL NOT NULL,
                tool_wear REAL NOT NULL,
                failure_prediction INTEGER NOT NULL,
                failure_probability REAL NOT NULL,
                is_anomaly INTEGER NOT NULL
            )
        """)


initialize_database()

def save_prediction(readings, failure_prediction,
                   failure_probability, is_anomaly):
    with sqlite3.connect(database_path) as connection:
        connection.execute("""
            INSERT INTO prediction_history (
                timestamp, machine_type, air_temperature,
                process_temperature, rotational_speed, torque,
                tool_wear, failure_prediction,
                failure_probability, is_anomaly
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            readings.type,
            readings.air_temperature,
            readings.process_temperature,
            readings.rotational_speed,
            readings.torque,
            readings.tool_wear,
            failure_prediction,
            failure_probability,
            int(is_anomaly),
        ))

failure_model = joblib.load(models_path / "failure_model.joblib")
anomaly_detector = joblib.load(models_path / "anomaly_detector.joblib")

app = FastAPI(
    title="Predictra API",
    description="Machine failure prediction and anomaly detection",
    version="1.0.0",
)

frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class SensorReadings(BaseModel):
    type: str = Field(pattern="^[LMH]$")
    air_temperature: float = Field(ge=250, le=350)
    process_temperature: float = Field(ge=250, le=350)
    rotational_speed: float = Field(gt=0, le=10000)
    torque: float = Field(ge=0, le=1000)
    tool_wear: float = Field(ge=0, le=1000)


@app.get("/")
def home():
    return {"message": "Welcome to the Predictra API"}


@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": True}



@app.post("/predict")
def predict(readings: SensorReadings):
    sensor_data = {
        "Type": readings.type,
        "Air temperature [K]": readings.air_temperature,
        "Process temperature [K]": readings.process_temperature,
        "Rotational speed [rpm]": readings.rotational_speed,
        "Torque [Nm]": readings.torque,
        "Tool wear [min]": readings.tool_wear,
    }

    input_data = pd.DataFrame([sensor_data])

    failure_probability = float(
    failure_model.predict_proba(input_data)[0][1]
    )

    FAILURE_THRESHOLD = 0.35
    failure_prediction = int(
        failure_probability >= FAILURE_THRESHOLD
    )

    anomaly_columns = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    ]

    anomaly_input = input_data[anomaly_columns]
    anomaly_prediction = int(
        anomaly_detector.predict(anomaly_input)[0]
    )
    is_anomaly = anomaly_prediction == -1

    save_prediction(
        readings,
        failure_prediction,
        failure_probability,
        is_anomaly,
    )

    return {
        "failure_prediction": failure_prediction,
        "failure_probability": round(failure_probability, 4),
        "is_anomaly": is_anomaly,
        "message": (
            "Potential failure detected"
            if failure_prediction == 1
            else "No failure predicted"
        ),
    }
@app.get("/history")
def get_prediction_history():
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT *
            FROM prediction_history
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    return [dict(row) for row in rows]

@app.get("/analytics")
def get_analytics():
    with sqlite3.connect(database_path) as connection:
        row = connection.execute("""
            SELECT
                COUNT(*) AS total_predictions,
                COALESCE(SUM(failure_prediction), 0) AS predicted_failures,
                COALESCE(SUM(is_anomaly), 0) AS anomalies_detected
            FROM prediction_history
        """).fetchone()

    total, failures, anomalies = row

    failure_rate = (
        round((failures / total) * 100, 2)
        if total > 0 else 0
    )

    return {
        "total_predictions": total,
        "predicted_failures": failures,
        "anomalies_detected": anomalies,
        "failure_rate": failure_rate
    }

