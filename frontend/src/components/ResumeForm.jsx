import React, { useState } from "react";
import axios from "axios";
import "./ResumeForm.css";


const ResumeForm = () => {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resume || !jobDescription) {
      alert("Please upload resume and provide job description");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("jd_text", jobDescription);

    try {
      const res = await axios.post("https://career-co-pilot-1.onrender.com/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Ensure arrays to prevent .map() errors
      const safeJobKeywords = Array.isArray(res.data.job_keywords)
        ? res.data.job_keywords
        : [];
      const safeResumeKeywords = Array.isArray(res.data.resume_keywords)
        ? res.data.resume_keywords
        : [];

      setResult({
        job_keywords: safeJobKeywords,
        resume_keywords: safeResumeKeywords,
        analysis_report: res.data.analysis_report || "",
        refined_resume: res.data.refined_resume || "",
      });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error || "Failed to analyze resume. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit}>
        <label>Upload Resume (PDF/DOCX/TXT):</label>
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => setResume(e.target.files[0])}
        />

        <label>Job Description:</label>
        <textarea
          rows="5"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the job description here..."
        />

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Check Match"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div className="result">
          <h3>Analysis Report:</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{result.analysis_report}</pre>

          <h3>Refined Resume:</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{result.refined_resume}</pre>

          <h4>Job Keywords:</h4>
          <ul>
            {(result.job_keywords || []).map((k, i) => (
              <li key={i}>{k}</li>
            ))}
          </ul>

          <h4>Resume Keywords:</h4>
          <ul>
            {(result.resume_keywords || []).map((k, i) => (
              <li key={i}>{k}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeForm;
