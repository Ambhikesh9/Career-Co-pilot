from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import docx
from services.analyze_resume import generate_resume_analysis
from services.refine_resume import refine_resume
from services.extract_keywords import extract_job_keywords, extract_resume_keywords


from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

# ---------------------------
# Helper Functions
# ---------------------------

def extract_text_from_pdf(file):
    """Extract text from PDF using PyMuPDF"""
    print("[DEBUG] Extracting text from PDF...")
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    print(f"[DEBUG] PDF text length: {len(text)}")
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX"""
    print("[DEBUG] Extracting text from DOCX...")
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    print(f"[DEBUG] DOCX text length: {len(text)}")
    return text

def extract_text(file):
    """Determine file type and extract text"""
    filename = file.filename.lower()
    print(f"[DEBUG] Extracting text from file: {filename}")
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)
    elif filename.endswith(".txt"):
        text = file.read().decode("utf-8")
        print(f"[DEBUG] TXT text length: {len(text)}")
        return text
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

# ---------------------------
# API Endpoint
# ---------------------------

@app.route("/analyze", methods=["POST"])
def analyze_resume_endpoint():
    print("[DEBUG] /analyze endpoint called")

    # Ensure resume is provided
    if "resume" not in request.files:
        print("[DEBUG] Resume file not found in request")
        return jsonify({"error": "Please provide a resume file."}), 400

    resume_file = request.files["resume"]
    print(f"[DEBUG] Resume file received: {resume_file.filename}")

    # Job description can be either uploaded or passed as text
    if "jd" in request.files:
        jd_file = request.files["jd"]
        jd_text = extract_text(jd_file)
        print(f"[DEBUG] Job description file received: {jd_file.filename}")
    elif "jd_text" in request.form:
        jd_text = request.form["jd_text"]
        print("[DEBUG] Job description text received from form")
    else:
        print("[DEBUG] Job description not provided")
        return jsonify({"error": "Please provide a job description file or text."}), 400

    # Extract resume text
    try:
        resume_text = extract_text(resume_file)
        print(f"[DEBUG] Resume text length: {len(resume_text)}")
    except Exception as e:
        print(f"[DEBUG] Failed to extract resume text: {str(e)}")
        return jsonify({"error": f"Failed to extract resume text: {str(e)}"}), 400

    # Extract keywords
    try:
        print("[DEBUG] Extracting job keywords...")
        job_keywords = extract_job_keywords(jd_text)
        print(f"[DEBUG] Job keywords: {job_keywords}")

        print("[DEBUG] Extracting resume keywords...")
        resume_keywords = extract_resume_keywords(resume_text)
        print(f"[DEBUG] Resume keywords: {resume_keywords}")
    except Exception as e:
        print(f"[DEBUG] Error extracting keywords: {str(e)}")
        return jsonify({"error": f"Error extracting keywords: {str(e)}"}), 500

    # Generate resume analysis report
    try:
        print("[DEBUG] Generating resume analysis report...")
        analysis_report = generate_resume_analysis(
            raw_job_description=jd_text,
            raw_resume=resume_text,
            extracted_job_keywords=job_keywords,
            extracted_resume_keywords=resume_keywords
        )
        print("[DEBUG] Analysis report generated")
    except Exception as e:
        print(f"[DEBUG] Error generating analysis report: {str(e)}")
        return jsonify({"error": f"Error generating analysis report: {str(e)}"}), 500

    # Generate refined resume
    try:
        print("[DEBUG] Generating refined resume...")
        refined_resume = refine_resume(
            raw_job_description=jd_text,
            extracted_job_keywords=job_keywords,
            raw_resume=resume_text,
            extracted_resume_keywords=resume_keywords,
            resume_analysis_report=analysis_report
        )
        print("[DEBUG] Refined resume generated, length:", len(refined_resume))
    except Exception as e:
        print(f"[DEBUG] Error refining resume: {str(e)}")
        return jsonify({"error": f"Error refining resume: {str(e)}"}), 500

    # Return JSON response
    print("[DEBUG] Returning JSON response")
    return jsonify({
        "job_keywords": job_keywords,
        "resume_keywords": resume_keywords,
        "analysis_report": analysis_report,
        "refined_resume": refined_resume
    })


if __name__ == "__main__":
    app.run(debug=True)
