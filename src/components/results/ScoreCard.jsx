import { RadialBarChart, RadialBar, ResponsiveContainer } from "recharts";
import "./ScoreCard.css";

function grade(s) {
  if (s >= 85) return { label: "Excellent",    color: "#10B981" };
  if (s >= 70) return { label: "Good",         color: "#2563EB" };
  if (s >= 55) return { label: "Fair",         color: "#F59E0B" };
  return           { label: "Needs Work",   color: "#EF4444" };
}

export default function ScoreCard({ score, jobRole }) {
  const { label, color } = grade(score);
  const data = [{ value: score, fill: color }];

  return (
    <div className="score-card card">
      <div className="score-card-header">
        <div>
          <p className="score-card-eyebrow">Overall ATS Score</p>
          <h2 className="score-card-job">{jobRole}</h2>
        </div>
        <span className="pill" style={{
          background: color + "18",
          color,
          border: `1px solid ${color}44`,
          fontSize: ".8125rem",
          fontWeight: 700,
        }}>
          {label}
        </span>
      </div>

      <div className="score-card-body">
        <div className="score-ring-wrap" style={{ width: 180, height: 180 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%" cy="50%"
              innerRadius="72%" outerRadius="96%"
              startAngle={90} endAngle={-270}
              data={data}
              barSize={16}
            >
              <RadialBar
                background={{ fill: "#F1F5F9" }}
                dataKey="value"
                cornerRadius={8}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="score-ring-text">
            <span className="score-ring-number" style={{ color }}>{score}</span>
            <span className="score-ring-denom">/100</span>
          </div>
        </div>

        <div className="score-card-meta">
          <p className="score-card-desc">
            Your resume scores <strong>{label.toLowerCase()}</strong> against the job requirements.
            {score < 80 && " Follow the suggestions below to improve your chances."}
            {score >= 80 && " Great work — refine the remaining gaps to maximise your chances."}
          </p>
          <div className="score-tier-list">
            {[
              { range: "85–100", label: "Excellent", col: "#10B981" },
              { range: "70–84",  label: "Good",      col: "#2563EB" },
              { range: "55–69",  label: "Fair",      col: "#F59E0B" },
              { range: "0–54",   label: "Needs Work",col: "#EF4444" },
            ].map((t) => (
              <div key={t.range} className={`score-tier${t.col === color ? " score-tier--active" : ""}`}>
                <span className="score-tier-dot" style={{ background: t.col }} />
                <span className="score-tier-range">{t.range}</span>
                <span className="score-tier-label">{t.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
