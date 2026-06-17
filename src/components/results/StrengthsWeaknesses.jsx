import { TrendingUp, TrendingDown } from "lucide-react";
import "./StrengthsWeaknesses.css";

export function StrengthsCard({ strengths }) {
  return (
    <div className="card sw-card">
      <div className="sw-head">
        <div className="sw-icon sw-icon--green"><TrendingUp size={16} /></div>
        <div>
          <h3 className="sw-title">Strengths</h3>
          <p className="sw-sub">What your CV does well</p>
        </div>
      </div>
      <ul className="sw-list">
        {strengths.map((s, i) => (
          <li key={i} className="sw-item sw-item--strength">
            <span className="sw-bullet sw-bullet--green" />
            {s}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function WeaknessesCard({ weaknesses }) {
  return (
    <div className="card sw-card">
      <div className="sw-head">
        <div className="sw-icon sw-icon--red"><TrendingDown size={16} /></div>
        <div>
          <h3 className="sw-title">Areas to Improve</h3>
          <p className="sw-sub">Key gaps to address</p>
        </div>
      </div>
      <ul className="sw-list">
        {weaknesses.map((w, i) => (
          <li key={i} className="sw-item sw-item--weakness">
            <span className="sw-bullet sw-bullet--red" />
            {w}
          </li>
        ))}
      </ul>
    </div>
  );
}
