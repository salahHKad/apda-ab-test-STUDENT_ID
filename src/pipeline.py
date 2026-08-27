"""Reusable data pipeline for the landing page A/B test project.

This module contains small, testable functions for loading, validating,
inspecting, cleaning, and saving the experiment records. It has no
command-line interface itself; see scripts/run_pipeline.py for that.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["user_id", "timestamp", "group", "landing_page", "converted"]
VALID_GROUPS = {"control", "treatment"}
VALID_PAGES = {"old_page", "new_page"}
VALID_CONVERTED = {0, 1}


def load_data(input_path: str) -> pd.DataFrame:
    """Load the raw experiment CSV into a DataFrame."""
    return pd.read_csv(input_path)


def inspect_data(df: pd.DataFrame) -> dict:
    """Summarize shape, dtypes, missing values, duplicate user IDs, and group/page counts."""
    summary = {
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_user_ids": int(df["user_id"].duplicated().sum())
        if "user_id" in df.columns
        else None,
        "group_page_counts": (
            df.groupby(["group", "landing_page"]).size().to_dict()
            if {"group", "landing_page"}.issubset(df.columns)
            else None
        ),
    }

    print(f"Shape: {summary['shape']}")
    print(f"Dtypes: {summary['dtypes']}")
    print(f"Missing values per column: {summary['missing_values']}")
    print(f"Duplicate user_id rows: {summary['duplicate_user_ids']}")
    print(f"Group/landing_page counts: {summary['group_page_counts']}")

    return summary


def validate_data(df: pd.DataFrame) -> None:
    """Validate the data contract; raise ValueError on any violation."""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required column(s): {missing_columns}")

    bad_groups = set(df["group"].dropna().unique()) - VALID_GROUPS
    if bad_groups:
        raise ValueError(f"Column 'group' contains invalid value(s): {bad_groups}")

    bad_pages = set(df["landing_page"].dropna().unique()) - VALID_PAGES
    if bad_pages:
        raise ValueError(f"Column 'landing_page' contains invalid value(s): {bad_pages}")

    bad_converted = set(df["converted"].dropna().unique()) - VALID_CONVERTED
    if bad_converted:
        raise ValueError(f"Column 'converted' contains invalid value(s): {bad_converted}")


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean experiment records; return the cleaned DataFrame and a row-count report.

    Steps: keep only correctly aligned group/page assignments, convert
    timestamp to datetime, derive experiment_date, sort by timestamp, and
    keep only the earliest record per user_id. Does not mutate the input.
    """
    working = df.copy()
    rows_before = len(working)

    aligned_mask = (
        (working["group"] == "control") & (working["landing_page"] == "old_page")
    ) | ((working["group"] == "treatment") & (working["landing_page"] == "new_page"))
    working = working[aligned_mask].copy()
    rows_after_assignment_cleaning = len(working)

    working["timestamp"] = pd.to_datetime(working["timestamp"])
    working["experiment_date"] = working["timestamp"].dt.date

    working = working.sort_values("timestamp")
    working = working.drop_duplicates(subset="user_id", keep="first")
    rows_after_duplicate_cleaning = len(working)

    working = working.reset_index(drop=True)

    if not working["user_id"].is_unique:
        raise ValueError("user_id is not unique after cleaning.")
    
    still_misaligned = ~(
        ((working["group"] == "control") & (working["landing_page"] == "old_page"))
        | ((working["group"] == "treatment") & (working["landing_page"] == "new_page"))
    )
    if still_misaligned.any():
        raise ValueError("Invalid group/landing_page pair remains after cleaning.")

    report = {
        "rows_before": rows_before,
        "rows_after_assignment_cleaning": rows_after_assignment_cleaning,
        "rows_after_duplicate_cleaning": rows_after_duplicate_cleaning,
    }
    print(f"Rows before cleaning: {report['rows_before']}")
    print(f"Rows after assignment cleaning: {report['rows_after_assignment_cleaning']}")
    print(f"Rows after duplicate-user cleaning: {report['rows_after_duplicate_cleaning']}")

    return working, report


def save_data(df: pd.DataFrame, output_dir: str) -> None:
    """Save the cleaned DataFrame as CSV and Parquet in output_dir."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path / "clean_ab_data.csv", index=False)
    df.to_parquet(out_path / "clean_ab_data.parquet", index=False)