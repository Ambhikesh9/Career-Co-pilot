from services.gemini_client import generate_text

REFINEMENT_PROMPT = """Your main goal is to implement the specific, actionable feedback from the Resume Analysis Report.
Use the report as your primary instruction manual for the revision. The Job Description and keyword lists should be used
as context to ensure the report's recommendations are applied in a way that perfectly aligns with the target role.

Instructions:
1. Prioritize the Analysis Report:
    - Carefully study the entire Resume Analysis Report, paying close attention to IMMEDIATE IMPROVEMENT RECOMMENDATIONS and ENHANCED RESUME RECOMMENDATIONS.
    - Your revision must address identified gaps such as Missing Critical Skills and Experience Gaps.
    - Integrate the exact Keywords to Integrate and Key Skills to Add as suggested in the report, placing them naturally.

2. Implement Structural and Content Edits:
    - Rewrite the Professional Summary and Experience Section per the report's tone and examples.
    - Apply Achievement Quantification (STAR) using suggested metrics.
    - Incorporate Revised Resume Structure Recommendation and ATS Optimization Checklist.

3. Align with Job & Keywords:
    - Cross-reference Job Description and Extracted Job Keywords to ensure alignment.

4. Output Format:
    - ONLY output the final, improved resume.
    - DO NOT include explanations or commentary.
    - Entire output must be the revised resume in Markdown format.

Inputs:

Job Description:
```md
{raw_job_description}
Extracted Job Keywords:

{extracted_job_keywords}


Original Resume:

{raw_resume}


Extracted Resume Keywords:

{extracted_resume_keywords}


Resume Analysis Report:

{resume_analysis_report}


"""

def refine_resume(
    raw_job_description: str,
    extracted_job_keywords,
    raw_resume: str,
    extracted_resume_keywords,
    resume_analysis_report: str
) -> str:
    """
    Generates a refined resume in Markdown using the Gemini API.
    """
    prompt = REFINEMENT_PROMPT.format(
        raw_job_description=raw_job_description,
        extracted_job_keywords=extracted_job_keywords if isinstance(extracted_job_keywords, str) else str(extracted_job_keywords),
        raw_resume=raw_resume,
        extracted_resume_keywords=extracted_resume_keywords if isinstance(extracted_resume_keywords, str) else str(extracted_resume_keywords),
        resume_analysis_report=resume_analysis_report
    )

    # Call Gemini API
    refined_resume_md = generate_text(prompt, model_name="gemini-2.5-pro")

    return refined_resume_md
