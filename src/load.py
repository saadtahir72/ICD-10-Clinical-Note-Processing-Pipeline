import os
import duckdb
import pandas as pd


def load_to_duckdb(
    df: pd.DataFrame,
    db_path: str = "data/clinical_notes.duckdb",
    table_name: str = "clinical_encounters",
) -> None:
    """Loads transformed clinical data into a local DuckDB database table."""
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Establish connection to DuckDB file
    conn = duckdb.connect(db_path)

    # Register pandas DataFrame as a temporary view for SQL querying
    conn.register("df_view", df)

    # Create table or replace existing records
    conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df_view"
    )

    # Append new records if table already exists
    conn.execute(f"INSERT INTO {table_name} SELECT * FROM df_view EXCEPT SELECT * FROM {table_name}")

    # Verify record count
    record_count = conn.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]
    print(
        f"[LOAD SUCCESS] Data loaded into DuckDB table '{table_name}'. Total records in table: {record_count}"
    )

    conn.close()


if __name__ == "__main__":
    from extract import load_raw_clinical_notes
    from transform import transform_clinical_notes

    # Execute full pipeline sequentially for testing
    raw_df = load_raw_clinical_notes("data/raw_notes.json")
    transformed_df = transform_clinical_notes(raw_df)

    # Load into database
    load_to_duckdb(transformed_df)