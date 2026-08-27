"""Run the DuckDB analysis queries against the cleaned parquet file.

Reads the named queries out of sql/analysis.sql, runs each against a DuckDB
view over data/processed/clean_ab_data.parquet, prints the result, and saves
it to outputs/<query_name>.csv.

Run from the repository root, e.g.:
    python scripts/run_sql.py
"""

import argparse
from pathlib import Path

import duckdb

REQUIRED_QUERY_NAMES = ["group_summary", "daily_conversion", "data_verification"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run DuckDB analysis queries against the cleaned parquet file."
    )
    parser.add_argument(
        "--parquet",
        default="data/processed/clean_ab_data.parquet",
        help="Path to the cleaned parquet file",
    )
    parser.add_argument(
        "--sql-file", default="sql/analysis.sql", help="Path to the SQL query file"
    )
    parser.add_argument(
        "--output-dir", default="outputs", help="Directory to write result CSVs"
    )
    return parser.parse_args()


def parse_named_queries(sql_path: str) -> dict:
    """Split a SQL file into {name: query_text} using '-- @name: X' markers."""
    text = Path(sql_path).read_text()
    queries = {}
    current_name = None
    current_lines: list[str] = []

    for line in text.splitlines():
        marker = line.strip()
        if marker.startswith("-- @name:"):
            if current_name is not None:
                queries[current_name] = "\n".join(current_lines).strip()
            current_name = marker.split("-- @name:")[1].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        queries[current_name] = "\n".join(current_lines).strip()

    return queries


def main() -> None:
    args = parse_args()

    queries = parse_named_queries(args.sql_file)
    missing = [name for name in REQUIRED_QUERY_NAMES if name not in queries]
    if missing:
        raise ValueError(f"Missing required quer(y/ies) in {args.sql_file}: {missing}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute(
        f"CREATE VIEW clean_ab_data AS SELECT * FROM read_parquet('{args.parquet}')"
    )

    for name in REQUIRED_QUERY_NAMES:
        result_df = con.execute(queries[name]).df()
        print(f"\n--- {name} ---")
        print(result_df)

        out_path = out_dir / f"{name}.csv"
        result_df.to_csv(out_path, index=False)
        print(f"Saved '{name}' results to {out_path}")


if __name__ == "__main__":
    main()