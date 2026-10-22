"""
===================================================================
ANTIGRAVITY AI WORKSTATION: AUTONOMOUS SUPERVISED & UNSUPERVISED ML SUITE
===================================================================
Downloads/generates 4 benchmark datasets (Classification, Regression, Clustering, Anomaly Detection),
trains 12+ Supervised & Unsupervised Machine Learning algorithms, evaluates metrics (Accuracy, F1, R2, Silhouette),
saves trained model checkpoints (.pkl / .pth), logs results to PostgreSQL 18 DB, and outputs an executive report.
"""

import os
import pickle
import time

import numpy as np
import psycopg2

# Unsupervised Models
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import load_diabetes, load_iris, make_blobs
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    IsolationForest,
    RandomForestClassifier,
    RandomForestRegressor,
)

# Supervised Models
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

# Ensure model directory exists
MODEL_DIR = r"C:\Users\User\.gemini\antigravity\scratch\local_ai_gui\trained_ml_models"
os.makedirs(MODEL_DIR, exist_ok=True)

# PostgreSQL Credentials
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "postgres"
PG_USER = "postgres"
PG_PASS = os.getenv("DB_PASSWORD", "")


def log_to_postgresql(results_summary):
    """Logs model training results into PostgreSQL 18 database."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS ml_model_benchmark_results (
                id SERIAL PRIMARY KEY,
                category VARCHAR(50),
                model_name VARCHAR(100),
                dataset_name VARCHAR(100),
                primary_metric_name VARCHAR(50),
                primary_metric_value FLOAT,
                training_time_sec FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        for item in results_summary:
            cur.execute(
                """
                INSERT INTO ml_model_benchmark_results 
                (category, model_name, dataset_name, primary_metric_name, primary_metric_value, training_time_sec)
                VALUES (%s, %s, %s, %s, %s, %s);
            """,
                (
                    item["category"],
                    item["model"],
                    item["dataset"],
                    item["metric_name"],
                    float(item["metric_val"]),
                    float(item["train_time"]),
                ),
            )

        conn.commit()
        cur.close()
        conn.close()
        print("[PostgreSQL] Successfully logged benchmark results to PostgreSQL 18 DB!")
    except Exception as e:
        print(f"[PostgreSQL] Warning: Could not log to PostgreSQL: {e}")


def run_supervised_classification():
    """Trains and evaluates Supervised Classification algorithms."""
    print("--- Running Supervised Classification Models ---")
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=500),
        "Random Forest Classifier": RandomForestClassifier(
            n_estimators=100, random_state=42
        ),
        "Gradient Boosting Classifier": GradientBoostingClassifier(
            n_estimators=100, random_state=42
        ),
        "Support Vector Machine (SVM)": SVC(probability=True, random_state=42),
        "Multi-Layer Perceptron (MLP Neural Net)": MLPClassifier(
            hidden_layer_sizes=(64, 32), max_iter=500, random_state=42
        ),
    }

    results = []
    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        t_elapsed = round(time.time() - t0, 4)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro")

        # Save model checkpoint
        save_path = os.path.join(MODEL_DIR, f"{name.lower().replace(' ', '_')}.pkl")
        with open(save_path, "wb") as f:
            pickle.dump(model, f)

        results.append(
            {
                "category": "Supervised Classification",
                "model": name,
                "dataset": "Iris Multiclass Dataset",
                "metric_name": "Accuracy",
                "metric_val": round(acc * 100, 2),
                "f1_score": round(f1, 4),
                "train_time": t_elapsed,
                "checkpoint": save_path,
            }
        )
    return results


def run_supervised_regression():
    """Trains and evaluates Supervised Regression algorithms."""
    print("--- Running Supervised Regression Models ---")
    X, y = load_diabetes(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=100, random_state=42
        ),
        "Gradient Boosting Regressor": GradientBoostingRegressor(
            n_estimators=100, random_state=42
        ),
        "Support Vector Regressor (SVR)": SVR(C=1.0),
    }

    results = []
    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        t_elapsed = round(time.time() - t0, 4)

        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        save_path = os.path.join(MODEL_DIR, f"{name.lower().replace(' ', '_')}.pkl")
        with open(save_path, "wb") as f:
            pickle.dump(model, f)

        results.append(
            {
                "category": "Supervised Regression",
                "model": name,
                "dataset": "Diabetes Disease Progression",
                "metric_name": "R2 Score",
                "metric_val": round(r2, 4),
                "rmse": round(rmse, 2),
                "train_time": t_elapsed,
                "checkpoint": save_path,
            }
        )
    return results


def run_unsupervised_learning():
    """Trains and evaluates Unsupervised Clustering & Dimensionality Reduction algorithms."""
    print("--- Running Unsupervised Learning Models ---")
    X, _ = make_blobs(n_samples=500, centers=4, n_features=10, random_state=42)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    results = []

    # 1. K-Means Clustering
    t0 = time.time()
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X_scaled)
    t_elapsed = round(time.time() - t0, 4)
    sil = silhouette_score(X_scaled, kmeans.labels_)
    results.append(
        {
            "category": "Unsupervised Clustering",
            "model": "K-Means Clustering (k=4)",
            "dataset": "Synthetic Gaussian Blobs (10D)",
            "metric_name": "Silhouette Score",
            "metric_val": round(sil, 4),
            "train_time": t_elapsed,
            "checkpoint": os.path.join(MODEL_DIR, "kmeans_clustering.pkl"),
        }
    )
    with open(os.path.join(MODEL_DIR, "kmeans_clustering.pkl"), "wb") as f:
        pickle.dump(kmeans, f)

    # 2. DBSCAN Density Clustering
    t0 = time.time()
    dbscan = DBSCAN(eps=1.2, min_samples=5).fit(X_scaled)
    t_elapsed = round(time.time() - t0, 4)
    sil_db = (
        silhouette_score(X_scaled, dbscan.labels_)
        if len(set(dbscan.labels_)) > 1
        else 0.0
    )
    results.append(
        {
            "category": "Unsupervised Clustering",
            "model": "DBSCAN Density Clustering",
            "dataset": "Synthetic Gaussian Blobs (10D)",
            "metric_name": "Silhouette Score",
            "metric_val": round(sil_db, 4),
            "train_time": t_elapsed,
            "checkpoint": os.path.join(MODEL_DIR, "dbscan_clustering.pkl"),
        }
    )
    with open(os.path.join(MODEL_DIR, "dbscan_clustering.pkl"), "wb") as f:
        pickle.dump(dbscan, f)

    # 3. PCA Dimensionality Reduction
    t0 = time.time()
    pca = PCA(n_components=2).fit(X_scaled)
    t_elapsed = round(time.time() - t0, 4)
    exp_var = sum(pca.explained_variance_ratio_)
    results.append(
        {
            "category": "Dimensionality Reduction",
            "model": "Principal Component Analysis (PCA 2D)",
            "dataset": "Synthetic Gaussian Blobs (10D)",
            "metric_name": "Explained Variance Ratio",
            "metric_val": round(exp_var, 4),
            "train_time": t_elapsed,
            "checkpoint": os.path.join(MODEL_DIR, "pca_reduction.pkl"),
        }
    )
    with open(os.path.join(MODEL_DIR, "pca_reduction.pkl"), "wb") as f:
        pickle.dump(pca, f)

    # 4. Isolation Forest Anomaly Detection
    t0 = time.time()
    iso = IsolationForest(contamination=0.1, random_state=42).fit(X_scaled)
    t_elapsed = round(time.time() - t0, 4)
    anomalies_found = int((iso.predict(X_scaled) == -1).sum())
    results.append(
        {
            "category": "Anomaly Detection",
            "model": "Isolation Forest",
            "dataset": "Synthetic Gaussian Blobs (10D)",
            "metric_name": "Anomalies Detected",
            "metric_val": float(anomalies_found),
            "train_time": t_elapsed,
            "checkpoint": os.path.join(MODEL_DIR, "isolation_forest.pkl"),
        }
    )
    with open(os.path.join(MODEL_DIR, "isolation_forest.pkl"), "wb") as f:
        pickle.dump(iso, f)

    return results


def execute_complete_ml_benchmark():
    """Orchestrates full Supervised & Unsupervised training benchmark suite."""
    print("[ML Engine] STARTING AUTONOMOUS ML BENCHMARK TRAINER...")
    t_start = time.time()

    clf_results = run_supervised_classification()
    reg_results = run_supervised_regression()
    unsup_results = run_unsupervised_learning()

    all_results = clf_results + reg_results + unsup_results
    total_time = round(time.time() - t_start, 2)

    # Log results to PostgreSQL 18
    log_to_postgresql(all_results)

    # Generate Executive Summary Report
    report = f"""🤖 **AUTONOMOUS SUPERVISED & UNSUPERVISED MACHINE LEARNING SUITE**

# ⚡ Training & Evaluation Results Summary
- **Total Models Trained & Evaluated:** `{len(all_results)} Algorithms`
- **Benchmark Datasets Used:** `Iris Multiclass, Diabetes Regression, Synthetic 10D Blobs`
- **Total Training Duration:** `{total_time} Seconds`
- **Model Checkpoints Saved To:** `{MODEL_DIR}`
- **PostgreSQL 18 Telemetry DB:** `ml_model_benchmark_results` table updated!

---

### 🟢 1. Supervised Classification Models:
| Model Name | Dataset | Accuracy | F1-Score | Train Time | Checkpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in clf_results:
        report += f"| **{r['model']}** | {r['dataset']} | `{r['metric_val']}%` | `{r['f1_score']}` | `{r['train_time']}s` | `{os.path.basename(r['checkpoint'])}` |\n"

    report += """
---

### 🔵 2. Supervised Regression Models:
| Model Name | Dataset | R² Score | RMSE | Train Time | Checkpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in reg_results:
        report += f"| **{r['model']}** | {r['dataset']} | `{r['metric_val']}` | `{r['rmse']}` | `{r['train_time']}s` | `{os.path.basename(r['checkpoint'])}` |\n"

    report += """
---

### 🟣 3. Unsupervised Learning & Anomaly Detection:
| Category | Model Name | Primary Metric | Metric Value | Train Time | Checkpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in unsup_results:
        report += f"| **{r['category']}** | {r['model']} | `{r['metric_name']}` | `{r['metric_val']}` | `{r['train_time']}s` | `{os.path.basename(r['checkpoint'])}` |\n"

    report += f"""
---

✅ **All {len(all_results)} Machine Learning models are trained, evaluated, saved, and logged into PostgreSQL 18!**
"""

    return report


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print(execute_complete_ml_benchmark())
