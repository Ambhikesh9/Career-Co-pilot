import json
from services.gemini_client import generate_text

JOB_KEYWORDS_PROMPT = """You are a JSON-extraction engine. Convert the following raw job posting text into exactly the JSON schema below:
— Do not add any extra fields or prose.
— Use "YYYY-MM-DD" for all dates.
— Ensure any URLs (website, applyLink) conform to URI format.
— Do not change the structure or key names; output only valid JSON matching the schema.
- Do not format the response in Markdown or any other format. Just output raw JSON.

Schema:
```json
{{
    "jobId": "string",
    "jobTitle": "string",
    "companyProfile": {{
        "companyName": "string",
        "industry": "Optional[string]",
        "website": "Optional[string]",
        "description": "Optional[string]"
    }},
    "location": {{
        "city": "string",
        "state": "string",
        "country": "string",
        "remoteStatus": "string"
    }},
    "datePosted": "YYYY-MM-DD",
    "employmentType": "string",
    "jobSummary": "string",
    "keyResponsibilities": [
        "string",
        "..."
    ],
    "qualifications": {{
        "required": [
            "string",
            "..."
        ],
        "preferred": [
            "string",
            "..."
        ]
    }},
    "compensationAndBenefits": {{
        "salaryRange": "string",
        "benefits": [
            "string",
            "..."
        ]
    }},
    "applicationInfo": {{
        "howToApply": "string",
        "applyLink": "string",
        "contactEmail": "Optional[string]"
    }},
    "extractedKeywords": [
        "string",
        "..."
    ]
}}
Job Posting:
{raw_job_description}

Note: Please output only a valid JSON matching the EXACT schema with no surrounding commentary.
"""
RESUME_KEYWORDS_PROMPT = """You are a JSON extraction engine. Convert the following resume text into precisely the JSON schema specified below.
- Do not compose any extra fields or commentary.
- Do not make up values for any fields.
- Use "Present" if an end date is ongoing.
- Make sure dates are in YYYY-MM-DD.
- Do not format the response in Markdown or any other format. Just output raw JSON.

Schema:
{
    "personalInfo": {
        "name": "string",
        "title": "string",
        "email": "string",
        "phone": "string",
        "location": "string | null",
        "website": "string | null",
        "linkedin": "string | null",
        "github": "string | null"
    },
    "summary": "string | null",
    "experience": [
        {
            "id": 0,
            "title": "string",
            "company": "string",
            "location": "string",
            "years": "string",
            "description": ["string"]
        }
    ],
    "education": [
        {
            "id": 0,
            "institution": "string",
            "degree": "string",
            "years": "string | null",
            "description": "string | null"
        }
    ],
    "skills": ["string"]
}

Resume:
{raw_resume}

NOTE: Please output only a valid JSON matching the EXACT schema.
"""

def extract_job_keywords(raw_job_description: str):
    prompt = JOB_KEYWORDS_PROMPT.format(raw_job_description=raw_job_description)
    out = generate_text(prompt, model_name="gemini-2.5-pro")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        # Attempt to salvage: strip code fences or leading/trailing text
        cleaned = out.strip().strip("```").strip()
        try:
            return json.loads(cleaned)
        except Exception as e:
            return {"error": "failed_to_parse_json", "raw_output": out}

def extract_resume_keywords(raw_resume: str):
    #prompt = RESUME_KEYWORDS_PROMPT.format(raw_resume=raw_resume.replace("{", "{{").replace("}", "}}"))
    # Instead of using .format()
    prompt = RESUME_KEYWORDS_PROMPT.replace("{raw_resume}", raw_resume)

    out = generate_text(prompt, model_name="gemini-2.5-pro")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        cleaned = out.strip().strip("```").strip()
        try:
            return json.loads(cleaned)
        except Exception as e:
            return {"error": "failed_to_parse_json", "raw_output": out}
