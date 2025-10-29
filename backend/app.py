from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import docx
from services.analyze_resume import generate_resume_analysis
from services.extract_keywords import extract_all_keywords
from flask_cors import CORS
import traceback  # <-- ADD THIS IMPORT

# ---------------------------
# Flask App Setup
# ---------------------------
app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

# Maximum file size: 2 MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB

# ---------------------------
# Helper Functions
# ---------------------------
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(file):
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

# ---------------------------
# Routes
# ---------------------------
@app.route('/', methods=['GET'])
def home():
    return "Backend is live! POST requests should go to /analyze"

@app.route("/analyze", methods=["POST"])
def analyze_resume_endpoint():
    try:
        # Validate resume file
        if "resume" not in request.files:
            return jsonify({"error": "Please provide a resume file."}), 400
        resume_file = request.files["resume"]

        # Validate job description (text or file)
        if "jd" in request.files:
            jd_file = request.files["jd"]
            jd_text = extract_text(jd_file)
        elif "jd_text" in request.form:
            jd_text = request.form["jd_text"]
        else:
            return jsonify({"error": "Please provide a job description file or text."}), 400

        # Limit text size
        MAX_TEXT_LENGTH = 50000  # 50k characters
        resume_text = extract_text(resume_file)
        if len(resume_text) > MAX_TEXT_LENGTH:
            return jsonify({"error": "Resume text too long"}), 400
        if len(jd_text) > MAX_TEXT_LENGTH:
            return jsonify({"error": "Job description too long"}), 400

        # --- CONSOLIDATED API CALL 1 ---
        print("Calling extract_all_keywords...") # Added log
        extracted_data = extract_all_keywords(jd_text, resume_text)
        
        # Error handling for extraction
        if "error" in extracted_data:
             print(f"Error from extract_all_keywords: {extracted_data.get('raw_output')}") # Added log
             return jsonify({"error": "Failed to parse API response for keywords.", "details": extracted_data.get("raw_output")}), 500
        
        job_keywords = extracted_data.get("job_keywords", {})
        resume_keywords = extracted_data.get("resume_keywords", {})

        # --- API CALL 2 ---
        print("Calling generate_resume_analysis...") # Added log
        analysis_report = generate_resume_analysis(
            raw_job_description=jd_text,
            raw_resume=resume_text,
            extracted_job_keywords=job_keywords,
            extracted_resume_keywords=resume_keywords
        )
        
        print("Analysis complete. Sending response.") # Added log
        return jsonify({
            "job_keywords": job_keywords,
            "resume_keywords": resume_keywords,
            "analysis_report": analysis_report
        })

    except ValueError as ve:
        # --- ADDED LOGGING ---
        print(f"--- VALUE ERROR --- \n{ve}")
        traceback.print_exc()
        # ---------------------
        return jsonify({"error": str(ve)}), 400
        
    except Exception as e:
        # --- THIS IS THE CRITICAL CHANGE ---
        print("--- AN UNCAUGHT EXCEPTION OCCURRED ---")
        traceback.print_exc() 
        # -----------------------------------
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)