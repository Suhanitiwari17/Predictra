
# Predictra
### AI-Powered Predictive Maintenance and Anomaly Detection

Predictra is a machine-learning-based predictive maintenance prototype that analyzes machine sensor readings to estimate potential failures and identify unusual operating patterns.

The project combines a Python ML pipeline, a FastAPI backend, a SQLite database, and a React dashboard.

## Features

- **Failure prediction:** A Random Forest classifier estimates the likelihood of machine failure from sensor readings.
- **Anomaly detection:** An Isolation Forest model flags unusual sensor patterns.
- **Interactive dashboard:** Submit machine readings and inspect prediction results.
- **Prediction history:** Store and review recent assessments using SQLite.
- **Live analytics:** View prediction counts, flagged failures, anomaly counts, and failure rate.
- **History filters:** Filter saved results by failure and anomaly status.
- **Probability trend:** Visualize predicted failure probabilities across assessments.
- **Threshold experiments:** Compare precision, recall, F1-score, and false alarms at different classification thresholds.

## Tech Stack

**Machine Learning:** Python, pandas, NumPy, scikit-learn, joblib  
**Backend:** FastAPI, Uvicorn  
**Frontend:** React, Vite, Recharts, Lucide React  
**Database:** SQLite  
**Dataset:** AI4I 2020 Predictive Maintenance Dataset

## Project Structure

```text
Predictra/
├── backend/
│   └── main.py
├── data/
│   └── ai4i2020.csv
├── models/
│   ├── failure_model.joblib
│   └── anomaly_detector.joblib
├── src/
│   ├── data_exploration.py
│   ├── data_analysis.py
│   ├── train_failure_model.py
│   ├── detect_anomalies.py
│   ├── threshold_experiment.py
│   └── final_model_evaluation.py
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── index.css
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Predictra
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

Make sure `data/ai4i2020.csv` is present in the `data` folder.

### 3. Train the models

```bash
python src/train_failure_model.py
python src/detect_anomalies.py
```

Run these commands when you need to generate or regenerate the saved model files.

### 4. Start the backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload
```

The API is available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually:

`http://localhost:5173`

Keep both the backend and frontend running while using the application.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/predict` | Predict failure and detect anomalies |
| GET | `/history` | Retrieve saved prediction history |
| GET | `/analytics` | Retrieve dashboard analytics |
| GET | `/docs` | Explore and test the API |

## Model Evaluation

Threshold experiments illustrate the trade-off between detecting more failures and increasing false alarms.

In one validation-guided experiment, a threshold of 0.35 achieved the following results on the evaluated test split:

- Failure precision: 72.88%
- Failure recall: 63.24%
- Failure F1-score: 0.677
- Failures detected: 43 out of 68
- False alarms: 16

These are exploratory results, not an independent final performance estimate. The test split had also been used in earlier threshold experiments. Further evaluation on an untouched test set is needed before reporting definitive model performance.

## Limitations

- The AI4I 2020 dataset is synthetic and may not represent actual industrial operating conditions.
- Failure predictions can produce false alarms or miss real failures.
- Anomaly detection identifies unusual sensor patterns; an anomaly does not necessarily mean a machine is failing.
- A predicted failure probability is a model estimate, not a guarantee of machine safety.
- This is an academic prototype and is not intended to replace industrial safety systems.

## Future Improvements

- Validate the final model on an untouched test set.
- Improve failure recall while controlling false alarms.
- Add more detailed model-performance visualizations.
- Support multiple machines and machine-specific histories.
- Explore deployment and monitoring in a controlled environment.

## Author

Developed as a machine-learning and full-stack predictive maintenance project.
