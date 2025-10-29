import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./ResumeForm.css"; // Make sure this file is in the same directory

const ResumeForm = () => {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("No file chosen");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resume || !jobDescription.trim()) {
      setError("Please upload a resume and enter a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("jd_text", jobDescription);

    try {
      const res = await axios.post("https://talentalign-gzhqcthhgmd8apc5.southindia-01.azurewebsites.net/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult({
        job_keywords: res.data.job_keywords || {},
        resume_keywords: res.data.resume_keywords || {},
        analysis_report: res.data.analysis_report || "",
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

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setResume(file);
    setFileName(file ? file.name : "No file chosen");
  };

  return (
    <div className="form-container">
      <div className="form-card">
        <h2 className="form-title">Resume Analyzer</h2>
        <p className="form-subtitle">
          Upload your resume and paste the job description to get a detailed match analysis.
        </p>

        <form onSubmit={handleSubmit} className="resume-form">
          {/* File Upload */}
          <div className="input-group file-input-group">
            <label className="input-label">Upload Resume (PDF, DOCX, TXT)</label>
            <div className="file-upload-wrapper">
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                id="resume-upload"
                className="file-input"
              />
              <label htmlFor="resume-upload" className="file-upload-label">
                <span className="upload-icon">📄</span>
                Choose File
              </label>
              <span className="file-name">{fileName}</span>
            </div>
          </div>

          {/* Job Description */}
          <div className="input-group">
            <label className="input-label">Job Description</label>
            <textarea
              rows="6"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job description here..."
              className="textarea-input"
            />
          </div>

          {/* Submit Button */}
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing Resume...
              </>
            ) : (
              "Check Match"
            )}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span> {error}
          </div>
        )}

        {/* Loading Progress Bar */}
        {loading && (
          <div className="loading-container">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
            <p className="loading-text">Processing your resume and job description...</p>
          </div>
        )}

        {/* Result Display */}
        {result && !loading && (
          <div className="result-container fade-in">
            <h3 className="result-title">Analysis Report</h3>
            <div className="markdown-report">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.analysis_report}
              </ReactMarkdown>
            </div>
            </div>
          
        )}
      </div>
    </div>
  );
};

export default ResumeForm;
