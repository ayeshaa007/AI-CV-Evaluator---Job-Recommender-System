import { useState } from "react";
import { AlignLeft, ChevronDown, ChevronUp, Clipboard } from "lucide-react";
import "./JobDescriptionInput.css";

const CHAR_LIMIT = 5000;

const PLACEHOLDER = `Paste the full job description here…

Example:
We are looking for a Senior Software Engineer to join our team. You will be responsible for designing and developing high-quality software solutions.

Requirements:
• 5+ years of experience with React, Node.js
• Experience with cloud platforms (AWS/GCP)
• Strong understanding of CI/CD pipelines
• Excellent communication skills`;

export default function JobDescriptionInput({ value, onChange }) {
  const [expanded, setExpanded] = useState(false);
  const charCount = value.length;
  const isNearLimit = charCount > CHAR_LIMIT * 0.85;
  const isOverLimit = charCount > CHAR_LIMIT;

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      onChange(text.slice(0, CHAR_LIMIT));
    } catch (_) {}
  };

  return (
    <div className="jd-field">
      <div className="jd-label-row">
        <label className="input-label" htmlFor="job-desc">
          Job Description <span className="required-star" style={{ color: "var(--red)" }}>*</span>
        </label>
        <div className="jd-label-actions">
          <button className="jd-action-btn" onClick={handlePaste} type="button" title="Paste from clipboard">
            <Clipboard size={13} /> Paste
          </button>
          <button className="jd-action-btn" onClick={() => setExpanded(e => !e)} type="button">
            {expanded ? <><ChevronUp size={13} /> Collapse</> : <><ChevronDown size={13} /> Expand</>}
          </button>
        </div>
      </div>

      <div className={`jd-textarea-wrap${expanded ? " jd-textarea-wrap--expanded" : ""}`}>
        <AlignLeft size={14} className="jd-textarea-icon" />
        <textarea
          id="job-desc"
          className={`input-base jd-textarea${isOverLimit ? " jd-textarea--error" : ""}`}
          placeholder={PLACEHOLDER}
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, CHAR_LIMIT))}
          style={{ height: expanded ? 400 : 160 }}
        />
      </div>

      <div className="jd-footer">
        <p className="input-hint">
          Pasting the full job posting gives more accurate keyword matching
        </p>
        <span className={`jd-charcount${isNearLimit ? " jd-charcount--warn" : ""}${isOverLimit ? " jd-charcount--error" : ""}`}>
          {charCount}/{CHAR_LIMIT}
        </span>
      </div>
    </div>
  );
}
