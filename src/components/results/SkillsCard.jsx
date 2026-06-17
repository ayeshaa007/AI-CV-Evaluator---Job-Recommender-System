import { CheckCircle2, AlertCircle } from "lucide-react";
import "./SkillsCard.css";

const PRIORITY_PILL = {
  High:   "pill-red",
  Medium: "pill-amber",
  Low:    "pill-blue",
};

export default function SkillsCard({ matched, missing }) {
  return (
    <div className="skills-grid-2">
      {/* Matched */}
      <div className="card skills-card">
        <div className="skills-card-head">
          <div className="skills-card-icon skills-card-icon--green">
            <CheckCircle2 size={16} />
          </div>
          <div>
            <h3 className="skills-card-title">Matched Skills</h3>
            <p className="skills-card-sub">{matched.length} skills detected</p>
          </div>
        </div>
        <div className="skills-chips">
          {matched.map((s) => (
            <span key={s} className="chip chip-green">{s}</span>
          ))}
        </div>
      </div>

      {/* Missing */}
      <div className="card skills-card">
        <div className="skills-card-head">
          <div className="skills-card-icon skills-card-icon--amber">
            <AlertCircle size={16} />
          </div>
          <div>
            <h3 className="skills-card-title">Missing Skills</h3>
            <p className="skills-card-sub">{missing.length} gaps found</p>
          </div>
        </div>
        <div className="missing-list">
          {missing.map((s) => (
            <div key={s.name} className="missing-row">
              <span className="missing-name">{s.name}</span>
              <span className={`pill ${PRIORITY_PILL[s.priority]}`}>{s.priority}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
