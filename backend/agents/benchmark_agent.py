"""
Agent 3: Benchmark Agent
Loads the Energy-Languages dataset subset (Python, C, C++, Java)
and returns real Intel RAPL reference values for comparison.
"""

import os
import pandas as pd

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset_subset.csv")
LANGUAGES    = ["Python", "C", "C++", "Java"]


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH)
    df = df[df["language"].isin(LANGUAGES)]
    return df


def get_benchmark(task_type: str) -> dict:
    df = load_dataset()

    # Try exact match first, fallback to "general"
    subset = df[df["task_type"] == task_type]
    if subset.empty:
        subset = df[df["task_type"] == "general"]

    result = {}
    for lang in LANGUAGES:
        row = subset[subset["language"] == lang]
        if not row.empty:
            result[lang.lower().replace("+", "p")] = {
                "energy_joules": float(row.iloc[0]["energy_joules"]),
                "time_seconds":  float(row.iloc[0]["time_seconds"]),
                "memory_mb":     float(row.iloc[0]["memory_mb"]),
            }

    result["task_type"] = task_type
    result["source"]    = "Energy-Languages-Dataset (Intel RAPL, bare-metal hardware)"
    return result


def get_all_language_comparison(task_type: str) -> list:
    """Return a list of dicts for charting all languages side by side."""
    df     = load_dataset()
    subset = df[df["task_type"] == task_type]
    if subset.empty:
        subset = df[df["task_type"] == "general"]

    rows = []
    for lang in LANGUAGES:
        row = subset[subset["language"] == lang]
        if not row.empty:
            rows.append({
                "language":      lang,
                "energy_joules": float(row.iloc[0]["energy_joules"]),
                "time_seconds":  float(row.iloc[0]["time_seconds"]),
                "memory_mb":     float(row.iloc[0]["memory_mb"]),
            })
    return rows
