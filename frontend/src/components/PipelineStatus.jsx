import React from 'react';

export default function PipelineStatus({ status }) {
  const steps = [
    { key: "company_research", label: "Company Research" },
    { key: "interview_patterns", label: "Interview Patterns" },
    { key: "skill_gap", label: "Skill Gap Analysis" },
    { key: "final_report", label: "Report Generation" }
  ];

  const getStatusIcon = (state) => {
    switch (state) {
      case "running":
        return <span className="status-indicator status-running">🔄</span>;
      case "done":
        return <span className="status-indicator status-done">✅</span>;
      case "waiting":
      default:
        return <span className="status-indicator status-waiting">⏳</span>;
    }
  };

  const getStatusClass = (state) => {
    switch (state) {
      case "running":
        return "step-running";
      case "done":
        return "step-done";
      case "waiting":
      default:
        return "step-waiting";
    }
  };

  return (
    <div className="card status-panel">
      <h3>📋 Pipeline Status</h3>
      <hr />
      <div className="steps-list">
        {steps.map((step) => {
          const state = status[step.key] || "waiting";
          return (
            <div key={step.key} className={`status-step ${getStatusClass(state)}`}>
              {getStatusIcon(state)}
              <span className="step-label">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
