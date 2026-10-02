import json
import os
import pandas as pd


def load_raw_clinical_notes(file_path: str) -> pd.DataFrame:
    """Reads raw clinical encounter notes from a JSON file and returns a clean pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data file not found at: {file_path}")

    # Using 'utf-8-sig' strips any PowerShell UTF-8 Byte Order Mark (BOM)
    with open(file_path, "r", encoding="utf-8-sig") as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    print(
        f"[EXTRACT SUCCESS] Ingested {len(df)} clinical encounter records."
    )
    return df


if __name__ == "__main__":
    raw_json_path = os.path.join("data", "raw_notes.json")
    df_raw = load_raw_clinical_notes(raw_json_path)
    print("\n--- Raw Extracted Data ---")
    print(df_raw[["encounter_id", "patient_id", "physician"]])