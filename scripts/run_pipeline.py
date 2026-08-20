"""CLI entry point: load, validate, clean, and save the A/B test data.

Run from the repository root, e.g.:
    python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed
"""

import argparse
import sys
from pathlib import Path

# Allow running this script directly (python scripts/run_pipeline.py) from the
# repository root without installing the project as a package.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.pipeline import clean_data, inspect_data, load_data, save_data, validate_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load, validate, clean, and save the landing page A/B test data."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the raw ab_data.csv file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write clean_ab_data.csv and clean_ab_data.parquet",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    df = load_data(args.input)
    inspect_data(df)
    validate_data(df)
    cleaned_df, _report = clean_data(df)
    save_data(cleaned_df, args.output_dir)

    print(f"Saved cleaned data to '{args.output_dir}' (CSV and Parquet).")


if __name__ == "__main__":
    main()