"""Focused tests for src/pipeline.py.
 
These tests build small DataFrames directly in this file and never read the
Kaggle CSV, so they run in a clean environment (local or GitHub Actions).
"""

import pandas as pd
import pytest

from src.pipeline import  clean_data, validate_data

def test_validate_data_rejects_missing_columns():
    """validate_data should raise ValueError when a required column is absent."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2],
            "timestamp": ["2021-01-01", "2021-01-02"],
            "group": ["control", "treatment"],
            # 'landing_page' column intentionally omitted/removed to test validation
            "converted": [0, 1],
        }
    )
    with pytest.raises(ValueError):
        validate_data(df)
        
def test_validate_data_rejects_invalid_values():
    """validate_data should raise ValueError when group/landing_page/converted hold bad values."""
    df = pd.DataFrame(
        {
            "user_id": [1,2],
            "timestamp": ["2021-01-01", "2021-01-02"],
            "group": ["control", "invalid_group"], #given invalid group value
            "landing_page": ["old_page", "new_page"],
            "converted": [0, 2]
        }
    )
    with pytest.raises(ValueError):
        validate_data(df)
        
        
def test_clean_data_removes_incorrect_group_page_assignment():
    """clean_data should drop rows where group and landing_page are not correctly aligned."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 3],
            "timestamp": ["2021-01-01", "2021-01-02", "2021-01-03"],
            "group": ["control", "treatment", "control"],# user 3 is misaligned: control paired with new_page
            "landing_page": ["old_page", "new_page", "new_page"],
            "converted": [0, 1, 0],
        }
    )
    
    cleaned, report = clean_data(df)
    assert set(cleaned["user_id"]) == {1,2}
    assert report["rows_before"] == 3
    assert report["rows_after_assignment_cleaning"] == 2
    
def test_clean_data_keeps_earliest_duplicate_and_preserves_input():
    """clean_data should keep only the earliest record per user_id and not mutate the input."""
    df = pd.DataFrame(
        {
            "user_id": [1, 1, 2],
            "timestamp": [
                "2017-01-05 00:00:00",  # later record for user 1
                "2017-01-01 00:00:00",  # earlier record for user 1 (should be kept)
                "2017-01-02 00:00:00",
            ],
            "group": ["control", "control", "treatment"],
            "landing_page": ["old_page", "old_page", "new_page"],
            "converted": [1, 0, 1],
        }
    )
    original_row_count = len(df)
    
    cleaned, report = clean_data(df)
    
     # Only one row remains for user 1, and it is the earliest one (converted=0).
    user_1_rows = cleaned[cleaned["user_id"] == 1]
    assert len(user_1_rows) == 1
    assert user_1_rows.iloc[0]["converted"] == 0
    assert report["rows_after_duplicate_cleaning"] == 2
    
    # The original input DataFrame must be unchanged.
    assert len(df) == original_row_count
    assert "experiment_date" not in df.columns