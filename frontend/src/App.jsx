import React, { useState } from 'react';
import InputForm from './components/InputForm';
import PipelineStatus from './components/PipelineStatus';
import ResultsPanel from './components/ResultsPanel';
import './App.css';

function App() {
  const [isRunning, setIsRunning] = useState(false);
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState({
    company_research: 'waiting',
    interview_patterns: 'waiting',
    skill_gap: 'waiting',
    final_report: 'waiting'
  });

  const handleAnalyze = async ({ company, role, jdText, resumeFile, company2 }) => {
    setIsRunning(true);
    setError(null);
    setResults(null);
    setCompany(company);
    setRole(role);
    setStatus({
      company_research: 'waiting',
      interview_patterns: 'waiting',
      skill_gap: 'waiting',
      final_report: 'waiting'
    });

    try {
      const formData = new FormData();
      formData.append('company', company);
      formData.append('role', role);
      formData.append('jd_text', jdText);
      formData.append('resume_file', resumeFile);
      if (company2) {
        formData.append('company2', company2);
      }

      const backendUrl = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
      const response = await fetch(`${backendUrl}/analyze`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server returned error status code: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // SSE yields events separated by double newlines
        const lines = buffer.split('\n\n');
        
        // Keep the last partial event in the buffer
        buffer = lines.pop();

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data: ')) continue;
          
          const rawJson = trimmed.slice(6);
          try {
            const event = JSON.parse(rawJson);
            if (event.type === 'status') {
              setStatus((prev) => ({
                ...prev,
                [event.step]: event.status
              }));
            } else if (event.type === 'result') {
              setResults(event.data);
            } else if (event.type === 'error') {
              setError(event.message);
            }
          } catch (e) {
            console.error("Failed to parse event JSON:", e, trimmed);
          }
        }
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'An unexpected error occurred during the analysis run.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎓 PlacementPrep AI</h1>
        <p>Automate candidate company intelligence, interview questions, and customized prep reports.</p>
      </header>

      {error && <div className="error-message">⚠️ {error}</div>}

      <div className="app-grid">
        <InputForm onSubmit={handleAnalyze} isRunning={isRunning} />
        <PipelineStatus status={status} />
      </div>

      <ResultsPanel results={results} company={company} role={role} />
    </div>
  );
}

export default App;
