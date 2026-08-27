APDA Final Project — Landing Page A/B Test

Project question:

An online service tested two landing pages: a control group that saw the old page and a treatment group
that saw the new page.
This project builds a small, reproducible analytics pipeline to clean the experiment records,
summarize conversion behavior, and determine whether the observed difference in conversion rate
between the two pages is statistically supported.

Experimental unit: a user (user_id)
Control: group = control, landing_page = old_page
Treatment: group = treatment, landing_page = new_page
Primary metric: conversion_rate  (propotion of users with converted = 1)

Dataset source:
Dataset: A/B testing dataset on Kaggle
File used: ab_data.csv only
Kaggle URL: https://www.kaggle.com/datasets/zhangluyuan/ab-testing
Download data: 17/8/2026

the raw CSV is not committed to this repositry, Download it yourself and place it in: "data/raw/ab_testing.csv"

Details of the dataset title, URL, filename, and download date are recorded in "data/raw/README.md"

Repositry structure:

apda-ab-test-STUDENT_ID/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- data/
|   |-- raw/README.md
|   `-- processed/
|-- src/pipeline.py
|-- scripts/run_pipeline.py
|-- scripts/run_sql.py
|-- sql/analysis.sql
|-- r/ab_test.R
|-- tests/test_pipeline.py
|-- outputs/
|   |-- group_summary.csv
|   |-- daily_conversion.csv
|   `-- figures/
`-- .github/workflows/tests.yml


Requirements:
Python (see requirements.txt):
pandas
duckdb
pytest

R:
readr
dplyr
ggplot2
stats (Base R)

Generated outputs:

File	                                Description
data/processed/clean_ab_data.csv	    Cleaned experiment records (CSV)
data/processed/clean_ab_data.parquet	Cleaned experiment records (Parquet)
outputs/group_summary.csv	            Users, conversions, conversion rate per group (DuckDB)
outputs/daily_conversion.csv	        Daily users, conversions, conversion rate per group (DuckDB)
outputs/figures/*.png	                Bar chart and daily line chart of conversion rate (R/ggplot2)

Running scripts/run_sql.py also prints a data_verificationresult to the console
(total rows, distinct user IDs, and min/max experiment_date)
so the row count and distinct-user count can be confirmed to agree after cleaning.

SETUP:
Run all commands from the repository root.

1. Create and activate the virtual environment:

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

2. Install Python requirements:

pip install -r requirements.txt

3. Download and place the raw data:
    1. Download ab_data.csv from the Kaggle dataset (see URL above).
    2. Copy it to data/raw/ab_data.csv.
    3. Do not edit the raw file and do not commit it to GitHub.

#Running the project:

Run the Python pipeline:

python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed
This loads, validates, and cleans ab_data.csv, then writes data/processed/clean_ab_data.csv 
and data/processed/clean_ab_data.parquet.

Run the tests:

pytest -q
Tests use small in-memory DataFrames and do not require the Kaggle file.

Run the DuckDB analysis:

python scripts/run_sql.py
This runs the queries in sql/analysis.sql against data/processed/clean_ab_data.parquet, writes
outputs/group_summary.csv and outputs/daily_conversion.csv, and prints a data_verification summary 
(total rows, distinct user IDs, min/max experiment_date) to the console.

#Run the R analysis

Rscript r/ab_test.R
This reads data/processed/clean_ab_data.csv, computes the group summary, absolute and relative lift,
runs prop.test, and saves two figures to outputs/figures/.

Reproducibility notes:
All scripts use relative paths from the repository root; no personal absolute paths are used.

Re-running the pipeline, tests, DuckDB analysis, and R script from a clean clone (after placing the raw CSV) 
recreates all processed files, result tables, and figures without editing any source paths.
