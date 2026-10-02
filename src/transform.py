import re
import pandas as pd

# Standard ICD-10 mapping rule set based on clinical key phrases
ICD10_MAPPINGS = {
    "copd": {
        "code": "J44.9",
        "description": "Chronic obstructive pulmonary disease, unspecified",
    },
    "chronic obstructive pulmonary disease": {
        "code": "J44.9",
        "description": "Chronic obstructive pulmonary disease, unspecified",
    },
    "type 2 diabetes": {
        "code": "E11.9",
        "description": "Type 2 diabetes mellitus without complications",
    },
    "migraine": {
        "code": "G43.909",
        "description": "Migraine, unspecified, not intractable, without status migrainosus",
    },
}


def clean_text(text: str) -> str:
    """Standardizes raw clinical text by lowercasing and stripping special punctuation."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
    return text


def map_icd10(cleaned_note: str) -> tuple[str, str]:
    """Maps cleaned clinical note text to appropriate ICD-10 code and description."""
    for keyword, info in ICD10_MAPPINGS.items():
        if keyword in cleaned_note:
            return info["code"], info["description"]
    return "UNKNOWN", "Unmapped clinical note"


def transform_clinical_notes(df: pd.DataFrame) -> pd.DataFrame:
    """Processes the raw clinical DataFrame to add cleaned text and ICD-10 classifications."""
    df_transformed = df.copy()

    # 1. Clean clinical notes
    df_transformed["cleaned_note"] = df_transformed["clinical_note"].apply(
        clean_text
    )

    # 2. Extract ICD-10 codes and descriptions
    mapped_results = df_transformed["cleaned_note"].apply(map_icd10)
    df_transformed["icd10_code"] = [res[0] for res in mapped_results]
    df_transformed["icd10_description"] = [res[1] for res in mapped_results]

    print(
        f"[TRANSFORM SUCCESS] Processed {len(df_transformed)} clinical records with ICD-10 mappings."
    )
    return df_transformed


if __name__ == "__main__":
    from extract import load_raw_clinical_notes

    # Read raw notes and apply transformations
    raw_df = load_raw_clinical_notes("data/raw_notes.json")
    transformed_df = transform_clinical_notes(raw_df)

    print("\n--- Transformed Data with ICD-10 Codes ---")
    print(
        transformed_df[
            ["encounter_id", "patient_id", "icd10_code", "icd10_description"]
        ]
    )