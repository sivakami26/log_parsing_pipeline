# ⚡ Automated Log Diagnostics & Anomaly Detection Pipeline

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A production-grade, vectorized Python data pipeline designed to parse unstructured hardware and system execution logs, extract latency metrics, and isolate diagnostic anomalies using density-based unsupervised clustering (`DBSCAN`) and TF-IDF text vectorization.

---

## 📌 Context & Business Impact

During high-stress hardware validation runs (e.g., DDR5 PHY memory calibration, PCIe link training, embedded microcode execution), parsing multi-gigabyte log traces manually is inefficient and prone to missing subtle latency spikes. 

This repository provides an automated **3-Tier Data Hygiene Pipeline** that ingests raw log files, transforms unstructured text streams into standardized numerical feature matrices, detects timing anomalies using machine learning, and exports structured reports in CSV and JSON formats for downstream analytics platforms (such as Tableau or Power BI).

---

## 🏗️ Architecture & 3-Tier Data Flow
┌─────────────────────────┐│     Raw Execution Log   │  Unstructured execution traces & malformed lines└────────────┬────────────┘│▼┌─────────────────────────┐│ Tier 1: Ingest & Parse  │  Regex parsing + Graceful fallback for corrupt lines└────────────┬────────────┘│▼┌─────────────────────────┐│ Tier 2: Clean & Transform│ Timestamps, vector differential timing (delta_sec),└────────────┬────────────┘  metric regex extraction, text sanitization│▼┌─────────────────────────┐│ Tier 3: ML Anomaly Model │  TF-IDF (50 features) + Standardized Latency Matrix└────────────┬────────────┘  ──> DBSCAN Clustering (Cluster -1 = Noise/Outlier)│▼┌─────────────────────────┐│   Automated Reporting   │  Exports: anomalies_report.csv & diagnostics_summary.json└─────────────────────────┘
---

## 🔑 Key Features

* **Robust Parsing Engine:** Custom regular expressions dynamically segment timestamps, log levels (`INFO`, `WARNING`, `ERROR`, `CRITICAL`), sub-modules, and messages. Malformed lines without timestamps are categorized as `CORRUPT` without halting processing.
* **Vectorized Latency Tracking:** Uses `pandas` differential timing (`.diff()`) with median imputation to calculate execution delta times between consecutive operations without slow Python loops.
* **Hybrid Machine Learning Anomaly Detection:**
  * **Text Features:** Extracts message semantics using `TfidfVectorizer` while regularizing numerical noise and hex memory addresses (e.g., `0x7FFA4B` $\rightarrow$ `<NUM>`).
  * **Density Clustering:** Combines scaled text features with standardized execution latency metrics via `DBSCAN` to detect unscripted outliers (`cluster = -1`).
  * **Rule Overrides:** Hard-flags high-severity events (`CRITICAL`, `ERROR`) and severe execution spikes (> 3.0s).
* **Automated Export Pipeline:** Exports structured CSV anomaly reports and API-ready JSON payloads complete with execution metadata and summary metrics.

---

## 🛠️ Tech Stack & Dependencies

* **Language:** Python 3.10+
* **Data Processing:** `pandas`, `numpy`, `re`
* **Machine Learning & Feature Scaling:** `scikit-learn` (`DBSCAN`, `TfidfVectorizer`, `StandardScaler`)
* **Serialization & Storage:** `json`, `os`

---

## 🚀 Quickstart Guide

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone [https://github.com/sivakami26/log-parsing-pipeline.git](https://github.com/sivakami26/log-parsing-pipeline.git)
cd log-parsing-pipeline

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
2. Install DependenciesBashpip install pandas numpy scikit-learn
3. Run PipelineBashpython log_pipeline.py
📊 Sample Output & Diagnostics SummaryTerminal Summary OutputPlaintext=================== PIPELINE SUMMARY ===================
 -> Total Logs Processed: 16
 -> Valid Timestamp Logs: 15
 -> Detected Anomalies: 2
 -> Critical Errors: 1

=================== EXPORT COMPLETE ===================
 -> Anomalies CSV: log_exports/anomalies_report_20261007_163500.csv
 -> Diagnostics JSON: log_exports/diagnostics_summary_20261007_163500.json
Detected Anomalies Output TableLineLevelModuleDelta SecDuration (ms)Message9ERRORMemory4.95s4500.0msBuffer overflow detected at address 0x7FFA4C...10CRITICALSystem0.01s0.0msCore execution stalled unexpectedly...
📄 License

Distributed under the MIT License. See LICENSE for more information.

👤 Author: Sivakami Srinivasan

📫 Contact: LinkedIn | Portfolio Website
EOF