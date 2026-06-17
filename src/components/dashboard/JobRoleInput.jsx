import { Briefcase } from "lucide-react";
import "./JobRoleInput.css";

const POPULAR = [
  "Software Engineer", "Data Scientist", "Product Manager",
  "UX Designer", "DevOps Engineer", "Full Stack Developer",
  "Machine Learning Engineer", "Frontend Developer",
];

export default function JobRoleInput({ value, onChange }) {
  return (
    <div className="job-role-field">
      <label className="input-label" htmlFor="job-role">
        Target Job Role <span className="required-star">*</span>
      </label>
      <div className="job-role-input-wrap">
        <Briefcase size={15} className="job-role-icon" />
        <input
          id="job-role"
          type="text"
          className="input-base job-role-input"
          placeholder="e.g., Software Engineer, Data Scientist…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
        />
      </div>
      <p className="input-hint">Start typing or pick from suggestions below</p>
      <div className="job-chips">
        {POPULAR.map((r) => (
          <button
            key={r}
            className={`job-chip${value === r ? " job-chip--active" : ""}`}
            onClick={() => onChange(r)}
            type="button"
          >
            {r}
          </button>
        ))}
      </div>
    </div>
  );
}
