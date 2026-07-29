import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { generatePDF } from '../utils/pdfGenerator';
import InteractiveChecklist from './InteractiveChecklist';

export default function ResultsPanel({ results, company, role }) {
  const [activeTab, setActiveTab] = useState(null);

  if (!results || !results.report) return null;

  const toggleTab = (tab) => {
    if (activeTab === tab) {
      setActiveTab(null);
    } else {
      setActiveTab(tab);
    }
  };

  const handleDownload = () => {
    const fileContent = reportClean;
    const blob = new Blob([fileContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${company.toLowerCase().replace(/\s+/g, '_')}_prep_report.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadPDF = () => {
    generatePDF(results.report, company, role);
  };

  // Strip initial thought block (if present) before file download or display to keep it polished
  const reportClean = results.report.replace(/^<thought>[\s\S]*?<\/thought>\s*/i, '');

  return (
    <div className="results-container">
      <h2>📊 Analysis Results</h2>

      {/* Raw Data Expanders */}
      <div className="expanders-section">
        <div className="expander">
          <button className="expander-trigger" onClick={() => toggleTab('research')}>
            <span>📂 Raw Company Research</span>
            <span>{activeTab === 'research' ? '▲' : '▼'}</span>
          </button>
          {activeTab === 'research' && (
            <div className="expander-content">
              <ReactMarkdown>{results.company_research}</ReactMarkdown>
            </div>
          )}
        </div>

        <div className="expander">
          <button className="expander-trigger" onClick={() => toggleTab('patterns')}>
            <span>📂 Raw Interview Patterns</span>
            <span>{activeTab === 'patterns' ? '▲' : '▼'}</span>
          </button>
          {activeTab === 'patterns' && (
            <div className="expander-content">
              <ReactMarkdown>{results.interview_patterns}</ReactMarkdown>
            </div>
          )}
        </div>

        <div className="expander">
          <button className="expander-trigger" onClick={() => toggleTab('gap')}>
            <span>📂 Raw Skill Gap Analysis</span>
            <span>{activeTab === 'gap' ? '▲' : '▼'}</span>
          </button>
          {activeTab === 'gap' && (
            <div className="expander-content">
              <ReactMarkdown>{results.skill_gap}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* Final Markdown Report Preview */}
      <div className="card report-card">
        <div className="report-header">
          <h3>📄 Customized Preparation Report</h3>
          <div className="report-actions">
            <button className="download-btn" onClick={handleDownload}>
              📥 Download MD
            </button>
            <button className="download-pdf-btn" onClick={handleDownloadPDF}>
              🎓 Download PDF
            </button>
          </div>
        </div>
        <hr />
        <div className="report-markdown-body">
          <ReactMarkdown>{reportClean}</ReactMarkdown>
        </div>
      </div>

      {/* Interactive Action Checklist */}
      <InteractiveChecklist reportText={reportClean} company={company} role={role} />
    </div>
  );
}
