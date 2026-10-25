
import os
import math
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


def diagnose_failure_modes(readings: SensorReadings):
    temperature_difference = (
        readings.process_temperature - readings.air_temperature
    )

    mechanical_power = (
        readings.torque
        * readings.rotational_speed
        * 2 * math.pi / 60
    )

    wear_torque = readings.tool_wear * readings.torque

    osf_limits = {
        "L": 11000,
        "M": 12000,
        "H": 13000,
    }

    osf_limit = osf_limits[readings.type]

    tool_wear_flag = 200 <= readings.tool_wear <= 240

    heat_flag = (
        temperature_difference < 8.6
        and readings.rotational_speed < 1380
    )

    power_flag = (
        mechanical_power < 3500
        or mechanical_power > 9000
    )

    overstrain_flag = wear_torque > osf_limit

    results = [
        {
            "code": "TWF",
            "name": "Tool Wear Failure",
            "indicated": tool_wear_flag,
            "reason": (
                "Tool wear is in the dataset's 200–240 minute "
                "TWF interval."
                if tool_wear_flag
                else (
                    "Tool wear is outside the dataset's "
                    "200–240 minute TWF interval. This does "
                    "not prove the tool is safe."
                )
            ),
            "suggested_check": (
                "Inspect tool condition and review the "
                "machine's tool-replacement schedule."
            ),
        },
        {
            "code": "HDF",
            "name": "Heat Dissipation Failure",
            "indicated": heat_flag,
            "reason": (
                f"Temperature difference is "
                f"{temperature_difference:.1f} K and speed is "
                f"{readings.rotational_speed} rpm. The dataset "
                "indicator requires a difference below 8.6 K "
                "and speed below 1380 rpm."
            ),
            "suggested_check": (
                "Inspect cooling, heat dissipation, and "
                "temperature sensors."
            ),
        },
        {
            "code": "PWF",
            "name": "Power Failure",
            "indicated": power_flag,
            "reason": (
                f"Estimated mechanical power is "
                f"{mechanical_power:.0f} W. The dataset rule "
                "flags power below 3500 W or above 9000 W."
            ),
            "suggested_check": (
                "Review torque, rotational speed, and "
                "the machine's actual power requirements."
            ),
        },
        {
            "code": "OSF",
            "name": "Overstrain Failure",
            "indicated": overstrain_flag,
            "reason": (
                f"Tool wear × torque = {wear_torque:.0f} "
                f"Nm·min; the dataset threshold for type "
                f"{readings.type} is {osf_limit} Nm·min."
            ),
            "suggested_check": (
                "Inspect mechanical load, tool wear, and "
                "the machine's operating limits."
            ),
        },
        {
            "code": "RNF",
            "name": "Random Failure",
            "indicated": None,
            "reason": (
                "This failure mode is random in the dataset "
                "and cannot be determined from the supplied "
                "sensor readings alone."
            ),
            "suggested_check": (
                "Use maintenance records, event logs, and "
                "additional diagnostic signals."
            ),
        },
    ]

    return results

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
        "possible_failures": diagnose_failure_modes(readings),
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

