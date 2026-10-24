
import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Gauge,
  LayoutDashboard,
  Menu,
  RefreshCw,
  ShieldCheck,
  Thermometer,
  Wrench,
} from "lucide-react";
import "./App.css";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const initialReadings = {
  type: "M",
  air_temperature: 300,
  process_temperature: 310,
  rotational_speed: 1500,
  torque: 40,
  tool_wear: 100,
};

function App() {
  const [readings, setReadings] = useState(initialReadings);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [analytics, setAnalytics] = useState({
  total_predictions: 0,
  predicted_failures: 0,
  anomalies_detected: 0,
  failure_rate: 0,
});

  function updateReading(event) {
    const { name, value } = event.target;
    setReadings((previous) => ({
      ...previous,
      [name]: name === "type" ? value : Number(value),
    }));
  }

  const [history, setHistory] = useState([]);
const [historyLoading, setHistoryLoading] = useState(true);
const [failureFilter, setFailureFilter] = useState("all");
const [anomalyFilter, setAnomalyFilter] = useState("all");

async function loadHistory() {
  try {
    const response = await fetch("http://127.0.0.1:8000/history");

    if (!response.ok) {
      throw new Error("Could not load history");
    }

    const data = await response.json();
    setHistory(data);
  } catch (error) {
    console.error("History loading failed:", error);
  } finally {
    setHistoryLoading(false);
  }
}

async function loadAnalytics() {
  try {
    const response = await fetch("http://127.0.0.1:8000/analytics");

    if (!response.ok) {
      throw new Error("Could not load analytics");
    }

    const data = await response.json();
    setAnalytics(data);
  } catch (error) {
    console.error("Analytics loading failed:", error);
  }
}

const chartData = [...history].reverse().map((item) => ({
  name: `#${item.id}`,
  probability: Number(
    (item.failure_probability * 100).toFixed(1)
  ),
}));

useEffect(() => {
  loadHistory();
  loadAnalytics();
}, []);

  async function predictFailure(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(readings),
      });

      if (!response.ok) {
        throw new Error(`API request failed (${response.status})`);
      }

      const data = await response.json();
      setResult(data);
      await loadHistory();
      await loadAnalytics();
    } catch {
      setError(
        "Could not connect to Predictra API. Make sure your backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  const probability = result
    ? (result.failure_probability * 100).toFixed(1)
    : null;
  const filteredHistory = history.filter((item) => {
  const failureMatches =
    failureFilter === "all" ||
    (failureFilter === "failure" &&
      Number(item.failure_prediction) === 1) ||
    (failureFilter === "normal" &&
      Number(item.failure_prediction) === 0);

  const anomalyMatches =
    anomalyFilter === "all" ||
    (anomalyFilter === "anomaly" &&
      Number(item.is_anomaly) === 1) ||
    (anomalyFilter === "normal" &&
      Number(item.is_anomaly) === 0);

  return failureMatches && anomalyMatches;
});
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Activity size={23} /></div>
          <div>
            <h2>Predictra</h2>
            <span>INTELLIGENCE PLATFORM</span>
          </div>
        </div>

        <p className="nav-heading">WORKSPACE</p>
        <div className="nav-item active">
          <LayoutDashboard size={18} /> Overview
        </div>
        <div className="nav-item">
          <Gauge size={18} /> Machine health
        </div>
        <div className="nav-item">
          <BrainCircuit size={18} /> Predictions
        </div>
        <div className="nav-item">
          <AlertTriangle size={18} /> Anomalies
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>API connection</strong>
            <span>Local environment</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="mobile-brand"><Menu size={21} /> Predictra</div>
          <div className="breadcrumb">Workspace / <strong>Overview</strong></div>
          <div className="system-status"><span /> ML ENGINE READY</div>
        </header>

        <section className="page-heading">
          <div>
            <p className="eyebrow">PREDICTIVE MAINTENANCE</p>
            <h1>Machine intelligence</h1>
            <p className="subtitle">
              Monitor sensor readings and predict potential machine failures.
            </p>
          </div>
          <div className="date-label">AI4I 2020 DATASET</div>
        </section>

        
<section className="metrics-grid">
  <article className="metric-card">
    <div className="metric-top">
      <span>Total predictions</span>
      <Activity size={19} />
    </div>
    <h2>{analytics.total_predictions}</h2>
    <p>
      <span className="tiny-dot green" /> Assessments recorded
    </p>
  </article>

  <article className="metric-card">
    <div className="metric-top">
      <span>Failures predicted</span>
      <AlertTriangle size={19} />
    </div>
    <h2>{analytics.predicted_failures}</h2>
    <p>
      <span className="tiny-dot green" /> Potential failures flagged
    </p>
  </article>

  <article className="metric-card">
    <div className="metric-top">
      <span>Anomalies detected</span>
      <Gauge size={19} />
    </div>
    <h2>{analytics.anomalies_detected}</h2>
    <p>
      <span className="tiny-dot green" /> Unusual sensor patterns
    </p>
  </article>

  <article className="metric-card">
    <div className="metric-top">
      <span>Failure rate</span>
      <ShieldCheck size={19} />
    </div>
    <h2>{analytics.failure_rate}%</h2>
    <p>
      <span className="tiny-dot green" /> Predicted failures / total
    </p>
  </article>
</section>


        <div className="workspace-grid">
          <section className="panel sensor-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">INPUT CONFIGURATION</p>
                <h2>Machine sensor readings</h2>
              </div>
              <div className="heading-icon"><Thermometer size={20} /></div>
            </div>
            <p className="panel-description">
              Enter operating conditions to run a live prediction.
            </p>

            <form onSubmit={predictFailure}>
              <label className="field-label" htmlFor="type">Machine type</label>
              <select id="type" name="type" value={readings.type} onChange={updateReading}>
                <option value="L">L — Low</option>
                <option value="M">M — Medium</option>
                <option value="H">H — High</option>
              </select>

              <div className="field-grid">
                <div>
                  <label className="field-label" htmlFor="air_temperature">Air temperature (K)</label>
                  <input id="air_temperature" name="air_temperature" type="number" min="250" max="350" step="any" value={readings.air_temperature} onChange={updateReading} required />
                </div>
                <div>
                  <label className="field-label" htmlFor="process_temperature">Process temperature (K)</label>
                  <input id="process_temperature" name="process_temperature" type="number" min="250" max="350" step="any" value={readings.process_temperature} onChange={updateReading} required />
                </div>
                <div>
                  <label className="field-label" htmlFor="rotational_speed">Rotational speed (rpm)</label>
                  <input id="rotational_speed" name="rotational_speed" type="number" min="1" max="10000" value={readings.rotational_speed} onChange={updateReading} required />
                </div>
                <div>
                  <label className="field-label" htmlFor="torque">Torque (Nm)</label>
                  <input id="torque" name="torque" type="number" min="0" max="1000" step="any" value={readings.torque} onChange={updateReading} required />
                </div>
                <div className="full-width">
                  <label className="field-label" htmlFor="tool_wear">Tool wear (minutes)</label>
                  <input id="tool_wear" name="tool_wear" type="number" min="0" max="1000" value={readings.tool_wear} onChange={updateReading} required />
                </div>
              </div>

              <button className="predict-button" type="submit" disabled={loading}>
                {loading ? <RefreshCw size={18} className="spin" /> : <BrainCircuit size={18} />}
                {loading ? "Analyzing readings..." : "Run failure prediction"}
              </button>
            </form>
            {error && <p className="error-message">{error}</p>}
          </section>

          <section className="panel results-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">MODEL OUTPUT</p>
                <h2>Prediction results</h2>
              </div>
              <div className="heading-icon"><Activity size={20} /></div>
            </div>

            {!result ? (
              <div className="empty-state">
                <div className="empty-icon"><BrainCircuit size={30} /></div>
                <h3>Awaiting sensor data</h3>
                <p>Submit your readings to view the model's failure prediction and anomaly assessment.</p>
              </div>
            ) : (
              <>
                <div className={`result-banner ${result.failure_prediction ? "warning" : "healthy"}`}>
                  {result.failure_prediction
                    ? <AlertTriangle size={23} />
                    : <CheckCircle2 size={23} />}
                  <div>
                    <strong>{result.failure_prediction ? "Potential failure detected" : "No failure predicted"}</strong>
                    <p>{result.message}</p>
                  </div>
                </div>

                <div className="probability-card">
                  <div className="result-label">Predicted failure probability</div>
                  <div className="probability-value">{probability}%</div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${Math.min(Number(probability), 100)}%` }} />
                  </div>
                  <p className="result-note">Estimated by the trained classification model.</p>
                </div>

                <div className={`anomaly-card ${result.is_anomaly ? "warning" : ""}`}>
                  <div className="anomaly-icon"><Activity size={20} /></div>
                  <div>
                    <strong>{result.is_anomaly ? "Unusual sensor pattern" : "No anomaly flagged"}</strong>
                    <p>{result.is_anomaly ? "The sensor readings appear unusual compared with learned normal patterns." : "The anomaly detector did not flag these readings."}</p>
                  </div>
                  <span className={`state-pill ${result.is_anomaly ? "alert" : ""}`}>
                    {result.is_anomaly ? "REVIEW" : "NORMAL"}
                  </span>
                </div>
              </>
            )}

            <div className="model-note">
              <Wrench size={16} />
              <span>Model outputs are estimates, not a guarantee of machine safety.</span>
            </div>
          </section>
        </div>


<section className="panel chart-panel">
  <div className="panel-heading">
    <div>
      <p className="eyebrow">MODEL ANALYTICS</p>
      <h2>Failure probability trend</h2>
    </div>
  </div>

  <p className="panel-description">
    Track predicted failure probability across recent assessments.
  </p>

  {chartData.length === 0 ? (
    <p className="history-message">
      Run a prediction to start building your trend chart.
    </p>
  ) : (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 20, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis
            tickFormatter={(value) => `${value}%`}
            domain={[0, 100]}
          />
          <Tooltip
            formatter={(value) => [
              `${Number(value).toFixed(1)}%`,
              "Failure probability",
            ]}
          />
          <Line
            type="monotone"
            dataKey="probability"
            stroke="#5865d8"
            strokeWidth={2.5}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )}
</section>


<section className="panel history-panel">
  <div className="panel-heading">
    <div>
      <p className="eyebrow">RECENT ACTIVITY</p>
      <h2>Prediction history</h2>
    </div>
    <button
      className="refresh-button"
      type="button"
      onClick={loadHistory}
    >
      <RefreshCw size={15} /> Refresh
    </button>
  </div>

  <p className="panel-description">
    Your latest saved machine assessments.
  </p>


<div className="history-filters">
  <label>
    Failure status
    <select
      value={failureFilter}
      onChange={(event) => setFailureFilter(event.target.value)}
    >
      <option value="all">All predictions</option>
      <option value="failure">Failures predicted</option>
      <option value="normal">Normal predictions</option>
    </select>
  </label>

  <label>
    Anomaly status
    <select
      value={anomalyFilter}
      onChange={(event) => setAnomalyFilter(event.target.value)}
    >
      <option value="all">All sensor readings</option>
      <option value="anomaly">Anomalies detected</option>
      <option value="normal">No anomaly detected</option>
    </select>
  </label>
</div>



{historyLoading ? (
  <p className="history-message">
    Loading prediction history...
  </p>
) : history.length === 0 ? (
  <p className="history-message">
    No saved predictions yet. Run your first prediction above.
  </p>
) : filteredHistory.length === 0 ? (
  <p className="history-message">
    No predictions match the selected filters.
  </p>
  ) : (
    <div className="table-scroll">
      <table className="history-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Machine</th>
            <th>Failure result</th>
            <th>Probability</th>
            <th>Anomaly</th>
          </tr>
        </thead>
        <tbody>
          {filteredHistory.map((item) => (
            <tr key={item.id}>
              <td>
                {new Date(item.timestamp).toLocaleString()}
              </td>
              <td>{item.machine_type}</td>
              <td>
                <span
                  className={`table-pill ${
                    item.failure_prediction ? "pill-warning" : "pill-good"
                  }`}
                >
                  {item.failure_prediction ? "Failure predicted" : "Normal"}
                </span>
              </td>
              <td>
                {(item.failure_probability * 100).toFixed(1)}%
              </td>
              <td>
                <span
                  className={`table-pill ${
                    item.is_anomaly ? "pill-warning" : "pill-good"
                  }`}
                >
                  {item.is_anomaly ? "Detected" : "Not detected"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )}
</section>

        <footer>Predictra <span>•</span> AI-powered predictive maintenance prototype</footer>
      </main>
    </div>
  );
}

export default App;
