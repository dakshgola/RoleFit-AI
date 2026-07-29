import React, { useState } from 'react';

export default function InputForm({ onSubmit, isRunning }) {
  const [company, setCompany] = useState('');
  const [company2, setCompany2] = useState('');
  const [role, setRole] = useState('');
  const [jdText, setJdText] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!company || !role || !jdText || !resumeFile) {
      alert("Please fill in all inputs and upload a resume PDF.");
      return;
    }
    onSubmit({ company, role, jdText, resumeFile, company2 });
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        setResumeFile(file);
      } else {
        alert("Only PDF resume files are accepted.");
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card input-form">
      <h3>📝 Preparation Inputs</h3>
      
      <div className="input-group">
        <label htmlFor="company">Target Company Name</label>
        <input
          id="company"
          type="text"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          placeholder="e.g. Stripe, Canva, Google"
          disabled={isRunning}
          required
        />
      </div>

      <div className="input-group">
        <label htmlFor="company2">Compare with another company (Optional)</label>
        <input
          id="company2"
          type="text"
          value={company2}
          onChange={(e) => setCompany2(e.target.value)}
          placeholder="e.g. Apple, Meta (optional)"
          disabled={isRunning}
        />
      </div>

      <div className="input-group">
        <label htmlFor="role">Target Role Name</label>
        <input
          id="role"
          type="text"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          placeholder="e.g. Software Engineer, Product Manager"
          disabled={isRunning}
          required
        />
      </div>

      <div className="input-group">
        <label htmlFor="jd">Job Description or Career URL</label>
        <textarea
          id="jd"
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste job details or input the career posting URL..."
          disabled={isRunning}
          required
          rows={7}
        />
      </div>

      <div className="input-group">
        <label>Upload Resume PDF</label>
        <div 
          className={`file-dropzone ${dragActive ? 'active' : ''} ${resumeFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={isRunning}
            className="hidden-file-input"
          />
          <label htmlFor="file-upload" className="dropzone-label">
            {resumeFile ? (
              <span className="file-name">📄 {resumeFile.name}</span>
            ) : (
              <span>Drag & drop resume PDF here or <strong style={{color: '#3b82f6', cursor: 'pointer'}}>browse</strong></span>
            )}
          </label>
        </div>
      </div>

      <button type="submit" className="primary-btn" disabled={isRunning || !company || !role || !jdText || !resumeFile}>
        {isRunning ? "🔄 Processing Analysis..." : "🚀 Run Analysis"}
      </button>
      <p className="caption">Note: uses external API quota — avoid rapid repeated runs during testing</p>
    </form>
  );
}
