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
```mermaid
flowchart TD
    A[📄 Raw Execution Log] -->|Unstructured Traces & Corrupt Lines| B[⚙️ Tier 1: Ingest & Parse]
    
    subgraph Tier1 [Tier 1 Processing]
        B --> B1[Extract Metadata via Regex]
        B --> B2[Tag Malformed as CORRUPT]
    end

    B1 & B2 --> C[🧹 Tier 2: Clean & Transform]

    subgraph Tier2 [Tier 2 Feature Engineering]
        C --> C1[Vector Differential Timing]
        C --> C2[Execution Duration Extraction]
        C --> C3[Text Sanitization & Masking]
    end

    C1 & C2 & C3 --> D[🤖 Tier 3: ML Anomaly Detection]

    subgraph Tier3 [Tier 3 Machine Learning]
        D --> D1[TF-IDF Text Vectorizer]
        D --> D2[StandardScaler Matrix]
        D1 & D2 --> D3[DBSCAN Clustering]
    end

    D3 --> E[📊 Automated Reporting]
    E --> F[📁 anomalies_report.csv]
    E --> G[📁 diagnostics_summary.json]

    style A fill:#ffffff,stroke:#333,stroke-width:2px,color:#000000
    style D3 fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#ffffff
    style E fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#ffffff
```
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
