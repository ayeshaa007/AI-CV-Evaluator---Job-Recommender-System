import { Lightbulb, ArrowRight } from "lucide-react";
import "./SuggestionsCard.css";

const IMPACT_PILL = {
  High:   "pill-red",
  Medium: "pill-amber",
};

export default function SuggestionsCard({ suggestions }) {
  return (
    <div className="card sug-card">
      <div className="sug-head">
        <div className="sug-icon"><Lightbulb size={16} /></div>
        <div>
          <h3 className="sug-title">AI Suggestions</h3>
          <p className="sug-sub">Actionable improvements prioritised by impact</p>
        </div>
      </div>
      <div className="sug-grid">
        {suggestions.map((s, i) => (
          <div key={i} className="sug-item">
            <div className="sug-item-top">
              <span className="sug-num">{String(i + 1).padStart(2, "0")}</span>
              <h4 className="sug-item-title">{s.title}</h4>
              <span className={`pill ${IMPACT_PILL[s.impact] || "pill-gray"}`}>
                {s.impact} Impact
              </span>
            </div>
            <p className="sug-item-desc">{s.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
