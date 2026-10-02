import duckdb
import pandas as pd


def load_to_duckdb(
    transformed_df: pd.DataFrame, db_path: str = "clinical_notes.duckdb"
):
    """Loads transformed clinical notes data frame into DuckDB."""
    if transformed_df.empty:
        print("[LOAD SKIPPED] DataFrame is empty.")
        return

    conn = duckdb.connect(db_path)
    table_name = "clinical_notes"

    conn.register("df_view", transformed_df)

    # Check if target table exists
    table_exists = (
        conn.execute(
            f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        ).fetchone()[0]
        > 0
    )

    if not table_exists:
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_view")
        print(
            f"[LOAD SUCCESS] Created table '{table_name}' and loaded {len(transformed_df)} records."
        )
    else:
        target_cols = len(
            conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        )
        incoming_cols = len(transformed_df.columns)

        if target_cols != incoming_cols:
            print(
                f"[LOAD WARNING] Schema mismatch. Recreating table '{table_name}'."
            )
            conn.execute(f"DROP TABLE {table_name}")
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_view")
        else:
            conn.execute(
                f"INSERT INTO {table_name} SELECT * FROM df_view EXCEPT SELECT * FROM {table_name}"
            )
            print(
                f"[LOAD SUCCESS] Appended/Synced {len(transformed_df)} records into '{table_name}'."
            )

    conn.close()