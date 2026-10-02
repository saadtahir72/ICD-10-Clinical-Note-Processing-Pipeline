import os
import time
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# 1. Define Pydantic Schema for structured LLM output
class ClinicalExtraction(BaseModel):
    icd10_code: str = Field(
        description="The primary official ICD-10 diagnostic code matching the note (e.g., J18.9, E11.9, G43.909, M17.11, K21.9)."
    )
    icd10_description: str = Field(
        description="Official medical description of the assigned ICD-10 code."
    )
    reasoning: str = Field(
        description="Brief explanation of why this code was assigned based on symptoms/diagnoses in the note, taking negations into account."
    )


def extract_icd10_with_ai(
    client: genai.Client, clinical_note: str, max_retries: int = 3
) -> tuple[str, str, str]:
    """Uses Gemini API with Structured Outputs and retry handling."""
    prompt = f"""
    You are an expert clinical medical coder. Analyze the following physician note and identify the PRIMARY medical diagnosis.
    Assign the correct standard ICD-10 code and description. Pay close attention to negations (e.g., 'denies history of hypertension' means hypertension is NOT the primary diagnosis).

    Clinical Note:
    "{clinical_note}"
    """

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",  # Active model endpoint
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ClinicalExtraction,
                    temperature=0.1,  # Low temperature for deterministic factual extraction
                ),
            )

            # Parse structured object directly
            result: ClinicalExtraction = response.parsed
            return result.icd10_code, result.icd10_description, result.reasoning

        except Exception as e:
            error_str = str(e)
            if "GenerateRequestsPerDay" in error_str:
                print("   [QUOTA EXHAUSTED] Daily limit reached for this model.")
                return "UNKNOWN", "Unmapped clinical note", "Daily API quota limit reached"

            if ("429" in error_str or "503" in error_str) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 15
                print(
                    f"   [WAIT] Rate limit or busy server. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                print(f"   [AI ERROR] Failed to process note: {e}")
                return "UNKNOWN", "Unmapped clinical note", f"Error: {str(e)}"

    return "UNKNOWN", "Unmapped clinical note", "Error: Max retries exceeded"


def transform_clinical_notes(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw notes into structured ICD-10 data using Gemini AI."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing! Please set it before running."
        )

    client = genai.Client(api_key=api_key)

    df_transformed = df.copy()

    codes = []
    descriptions = []
    reasonings = []

    print("[AI TRANSFORM] Processing clinical notes through Gemini AI...")
    for idx, row in df_transformed.iterrows():
        print(
            f"  -> Processing note {idx + 1}/{len(df_transformed)} (Encounter: {row['encounter_id']})..."
        )
        code, desc, reason = extract_icd10_with_ai(
            client, row["clinical_note"]
        )
        codes.append(code)
        descriptions.append(desc)
        reasonings.append(reason)

        # 12-second delay between notes to strictly stay under 5 Requests Per Minute
        time.sleep(12)

    df_transformed["icd10_code"] = codes
    df_transformed["icd10_description"] = descriptions
    df_transformed["ai_reasoning"] = reasonings

    print(
        f"[TRANSFORM SUCCESS] AI extracted ICD-10 codes for {len(df_transformed)} clinical records."
    )
    return df_transformed


if __name__ == "__main__":
    from extract import load_raw_clinical_notes

    raw_df = load_raw_clinical_notes("data/raw_notes.json")
    transformed_df = transform_clinical_notes(raw_df)

    print("\n--- AI Transformed Data Sample ---")
    print(
        transformed_df[
            [
                "encounter_id",
                "icd10_code",
                "icd10_description",
                "ai_reasoning",
            ]
        ].head()
    )