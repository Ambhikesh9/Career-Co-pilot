import json
from services.gemini_client import generate_text

# --- THIS PROMPT IS NOW FIXED ---
# All literal { and } have been doubled to {{ and }}
# The real placeholders {raw_job_description} and {raw_resume} remain single.

COMBINED_EXTRACTION_PROMPT = """
You are a JSON-extraction engine. Your task is to extract structured data from BOTH a job description and a resume, provided in a single prompt.

You must return ONLY a single, valid JSON object that follows this exact schema:

```json
{{
  "job_keywords": {{
    "jobTitle": "string",
    "companyName": "string",
    "industry": "Optional[string]",
    "location": "string",
    "remoteStatus": "string",
    "keyResponsibilities": ["string", "..."],
    "requiredQualifications": ["string", "..."],
    "preferredQualifications": ["string", "..."],
    "extractedHardSkills": ["string", "..."],
    "extractedSoftSkills": ["string", "..."]
  }},
  "resume_keywords": {{
    "personalInfo": {{
      "name": "string",
      "title": "string",
      "email": "string",
      "phone": "string",
      "location": "string | null",
      "linkedin": "string | null",
      "github": "string | null"
    }},
    "summary": "string | null",
    "experience": [
      {{
        "title": "string",
        "company": "string",
        "years": "string",
        "description_bullets": ["string", "..."]
      }}
    ],
    "education": [
      {{
        "institution": "string",
        "degree": "string",
        "years": "string | null"
      }}
    ],
    "skills": ["string"]
  }}
}}
Do not add any extra fields, explanations, or markdown formatting.

If a field is not found, use null or an empty array [] as appropriate.

Pay close attention to the schema nesting.

Here is the data:

---JOB DESCRIPTION START--- {raw_job_description} ---JOB DESCRIPTION END---

---RESUME START--- {raw_resume} ---RESUME END---

Output only the JSON. """

def extract_all_keywords(raw_job_description: str, raw_resume: str):
    """ Extracts keywords from BOTH the JD and resume in a single API call. """
    prompt = COMBINED_EXTRACTION_PROMPT.format( raw_job_description=raw_job_description, raw_resume=raw_resume )

    out = generate_text(prompt, model_name="gemini-2.5-pro") 

    # Check if generate_text returned an error string
    if isinstance(out, str) and out.startswith("Error:"):
        print(f"Error from gemini_client: {out}")
        return {{"error": "api_call_failed", "raw_output": out}}

    loaded_data = None
    try:
        loaded_data = json.loads(out)
    except json.JSONDecodeError as e1:
        # Attempt to salvage
        cleaned = out.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        try:
            loaded_data = json.loads(cleaned)
        except Exception as e2:
            print(f"Failed to parse JSON even after cleaning. Original error: {e1}. Second error: {e2}")
            return {{"error": "failed_to_parse_json", "raw_output": out}}

    # --- NEW VALIDATION STEP ---
    # Check if the loaded data is a dictionary
    if not isinstance(loaded_data, dict):
        print(f"Failed to parse: API returned a {type(loaded_data)} instead of a dict.")
        return {{"error": "api_returned_invalid_type", "raw_output": out}}
        
    # Check if it has the top-level keys we expect
    if "job_keywords" not in loaded_data or "resume_keywords" not in loaded_data:
        print(f"Failed to parse: API output missing required keys 'job_keywords' or 'resume_keywords'.")
        return {{"error": "api_output_missing_keys", "raw_output": out, "keys_found": list(loaded_data.keys())}}

    # Success
    return loaded_data