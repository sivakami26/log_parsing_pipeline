import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


class LogDiagnosticsPipeline:

    def __init__(self, log_file_path: str, output_dir: str = "output_reports"):
        self.log_file_path = log_file_path
        self.output_dir = output_dir
        self.raw_df: pd.DataFrame = pd.DataFrame()
        self.cleaned_df: pd.DataFrame = pd.DataFrame()
        self.anomaly_df: pd.DataFrame = pd.DataFrame()

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        self.log_pattern = re.compile(
            r"^\[(?P<timestamp>[\d\-:\.\s]+)\]\s+"
            r"\[(?P<level>INFO|WARNING|ERROR|CRITICAL)\]\s+"
            r"\[(?P<module>[\w\.\-]+)\]\s+"
            r"(?P<message>.*)$"
        )

    def ingest_and_parse(self) -> pd.DataFrame:
        parsed_records: List[Dict[str, str]] = []
        with open(
            self.log_file_path, "r", encoding="utf-8", errors="replace"
        ) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                match = self.log_pattern.match(line)
                if match:
                    record = match.groupdict()
                    record["line_num"] = line_num
                    parsed_records.append(record)
                else:
                    parsed_records.append({
                        "timestamp": None,
                        "level": "CORRUPT",
                        "module": "UNKNOWN",
                        "message": line,
                        "line_num": line_num,
                    })
        self.raw_df = pd.DataFrame(parsed_records)
        return self.raw_df

    def clean_and_transform(self) -> pd.DataFrame:
        df = self.raw_df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

        # Delta calculation with median imputation
        df["delta_seconds"] = df["timestamp"].diff().dt.total_seconds()
        median_delta = (
            df["delta_seconds"].median()
            if not df["delta_seconds"].dropna().empty
            else 0.0
        )
        df["delta_seconds"] = df["delta_seconds"].fillna(median_delta)

        # Extract execution duration metric
        def extract_execution_ms(msg: str) -> float:
            match = re.search(
                r"(?:time|duration|latency)=(\d+\.?\d*)ms", msg, re.IGNORECASE
            )
            return float(match.group(1)) if match else 0.0

        df["execution_ms"] = df["message"].apply(extract_execution_ms)
        df["clean_message"] = df["message"].apply(
            lambda x: re.sub(r"0x[0-9a-fA-F]+|\d+", "<NUM>", x)
        )

        self.cleaned_df = df
        return self.cleaned_df

    def detect_anomalies(
        self, eps: float = 0.5, min_samples: int = 2
    ) -> pd.DataFrame:
        df = self.cleaned_df.copy()

        vectorizer = TfidfVectorizer(max_features=50, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(df["clean_message"]).toarray()

        scaler = StandardScaler()
        latency_features = scaler.fit_transform(
            df[["delta_seconds", "execution_ms"]].fillna(0)
        )
        combined_features = np.hstack((tfidf_matrix, latency_features))

        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        df["cluster_label"] = dbscan.fit_predict(combined_features)

        # Anomaly rules
        is_dbscan_outlier = df["cluster_label"] == -1
        is_critical_or_corrupt = df["level"].isin(
            ["CRITICAL", "CORRUPT", "ERROR"]
        )
        is_info_latency_spike = (df["level"] == "INFO") & (
            (df["delta_seconds"] > 3.0) | (df["execution_ms"] > 1000.0)
        )

        df["is_anomaly"] = (
            (is_dbscan_outlier & (df["level"] != "INFO"))
            | is_critical_or_corrupt
            | is_info_latency_spike
        )

        self.anomaly_df = df
        return self.anomaly_df

    # -------------------------------------------------------------------------
    # NEW: Automated Export Functionality (CSV & JSON)
    # -------------------------------------------------------------------------
    def export_results(
        self, summary: Dict[str, int]
    ) -> Dict[str, str]:
        """Exports full execution data and detected anomalies to CSV and JSON formats."""
        if self.anomaly_df.empty:
            raise ValueError(
                "Export error: No processed data available. Run run_pipeline() first."
            )

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_paths = {}

        # Convert timestamps to string format for clean JSON serialization
        export_df = self.anomaly_df.copy()
        export_df["timestamp"] = export_df["timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )

        # 1. Export Anomalies to CSV
        anomalies_df = export_df[export_df["is_anomaly"]].drop(
            columns=["clean_message"]
        )
        csv_path = os.path.join(
            self.output_dir, f"anomalies_report_{timestamp_str}.csv"
        )
        anomalies_df.to_csv(csv_path, index=False)
        export_paths["csv_anomalies"] = csv_path

        # 2. Export Summary & Anomalies to JSON
        json_path = os.path.join(
            self.output_dir, f"diagnostics_summary_{timestamp_str}.json"
        )
        json_payload = {
            "metadata": {
                "source_log_file": self.log_file_path,
                "execution_timestamp": datetime.now().isoformat(),
            },
            "summary_metrics": summary,
            "detected_anomalies": anomalies_df.to_dict(orient="records"),
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_payload, f, indent=4)
        export_paths["json_summary"] = json_path

        return export_paths

    def run_pipeline(
        self, export: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Executes full pipeline and optionally triggers exports."""
        self.ingest_and_parse()
        self.clean_and_transform()
        results = self.detect_anomalies()

        summary = {
            "total_logs_processed": len(self.raw_df),
            "valid_timestamp_logs": len(self.cleaned_df),
            "detected_anomalies": int(results["is_anomaly"].sum()),
            "critical_errors": int((results["level"] == "CRITICAL").sum()),
        }

        if export:
            paths = self.export_results(summary)
            print("\n=================== EXPORT COMPLETE ===================")
            print(f" -> Anomalies CSV: {paths['csv_anomalies']}")
            print(f" -> Diagnostics JSON: {paths['json_summary']}")

        return results, summary


if __name__ == "__main__":
    pipeline = LogDiagnosticsPipeline(
        "test_execution.log", output_dir="log_exports"
    )
    results_df, report = pipeline.run_pipeline(export=True)