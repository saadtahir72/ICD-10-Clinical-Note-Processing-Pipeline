import os
from src.extract import load_raw_clinical_notes
from src.transform import transform_clinical_notes
from src.load import load_to_duckdb


def run_pipeline() -> None:
    """Orchestrates the end-to-end ICD-10 Clinical Note ETL Pipeline."""
    print("=" * 60)
    print("STARTING ICD-10 CLINICAL NOTE ETL PIPELINE")
    print("=" * 60)

    # File paths
    raw_json_path = os.path.join("data", "raw_notes.json")
    db_path = os.path.join("data", "clinical_notes.duckdb")

    # Step 1: Extract
    print("\n[STEP 1/3] Extracting raw clinical notes...")
    raw_df = load_raw_clinical_notes(raw_json_path)

    # Step 2: Transform
    print("\n[STEP 2/3] Transforming notes and assigning ICD-10 codes...")
    transformed_df = transform_clinical_notes(raw_df)

    # Step 3: Load
    print("\n[STEP 3/3] Loading processed data into DuckDB...")
    load_to_duckdb(transformed_df, db_path=db_path)

    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()