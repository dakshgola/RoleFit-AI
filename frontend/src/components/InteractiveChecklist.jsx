import React, { useState, useEffect } from 'react';

export default function InteractiveChecklist({ reportText, company, role }) {
  const [items, setItems] = useState([]);
  const [checkedState, setCheckedState] = useState({});
  
  // Storage key unique to this company and role
  const storageKey = `checklist_${company.toLowerCase().replace(/\s+/g, '_')}_${role.toLowerCase().replace(/\s+/g, '_')}`;

  useEffect(() => {
    if (!reportText) return;

    // Parse checklist items from the markdown report
    const checklistIndex = reportText.indexOf("## Final Checklist");
    if (checklistIndex === -1) {
      setItems([]);
      return;
    }

    const checklistPart = reportText.substring(checklistIndex + "## Final Checklist".length);
    const nextHeadingIndex = checklistPart.search(/\n##\s/);
    const sectionText = nextHeadingIndex !== -1 ? checklistPart.substring(0, nextHeadingIndex) : checklistPart;
    
    const lines = sectionText.split('\n');
    const parsedItems = [];
    
    for (let line of lines) {
      const trimmed = line.trim();
      // Matches: - [ ] text, - [x] text, * [ ] text, - text, * text
      const match = trimmed.match(/^[-*]\s+(?:\[([ xX])\]\s+)?(.*)/);
      if (match) {
        const isCheckedInMarkdown = match[1] ? (match[1] === 'x' || match[1] === 'X') : false;
        const text = match[2].replace(/\*\*/g, '').trim(); // Strip markdown bold tags
        if (text) {
          parsedItems.push({ text, defaultChecked: isCheckedInMarkdown });
        }
      }
    }
    
    setItems(parsedItems);

    // Load or initialize checked states from localStorage
    const savedStates = localStorage.getItem(storageKey);
    if (savedStates) {
      try {
        setCheckedState(JSON.parse(savedStates));
      } catch (e) {
        console.error("Failed to parse saved checklist states:", e);
        initializeCheckedStates(parsedItems);
      }
    } else {
      initializeCheckedStates(parsedItems);
    }
  }, [reportText, storageKey]);

  const initializeCheckedStates = (parsedItems) => {
    const initial = {};
    parsedItems.forEach(item => {
      initial[item.text] = item.defaultChecked;
    });
    setCheckedState(initial);
  };

  const handleCheckboxChange = (text) => {
    const updated = {
      ...checkedState,
      [text]: !checkedState[text]
    };
    setCheckedState(updated);
    localStorage.setItem(storageKey, JSON.stringify(updated));
  };

  if (items.length === 0) return null;

  // Calculate completion percentage
  const completedCount = items.filter(item => checkedState[item.text]).length;
  const totalCount = items.length;
  const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="card checklist-card">
      <div className="checklist-header">
        <h3>📋 Interactive Action Checklist</h3>
        <span className="checklist-badge">{completedCount} / {totalCount} Completed</span>
      </div>
      <p className="checklist-sub">Check off preparation tasks to track your readiness for {company}:</p>
      
      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar" style={{ width: `${percentage}%` }}></div>
        <span className="progress-text">{percentage}%</span>
      </div>

      {/* Checkbox list */}
      <div className="checklist-list">
        {items.map((item, idx) => {
          const isChecked = !!checkedState[item.text];
          return (
            <label key={idx} className={`checklist-item ${isChecked ? 'completed' : ''}`}>
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => handleCheckboxChange(item.text)}
              />
              <span className="checklist-text">{item.text}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}
