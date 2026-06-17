import "./CategoryBreakdown.css";

export default function CategoryBreakdown({ categories }) {
  return (
    <div className="cat-card card">
      <div className="cat-card-head">
        <h3 className="cat-card-title">Category Breakdown</h3>
        <p className="cat-card-sub">Score by evaluation dimension</p>
      </div>
      <div className="cat-list">
        {categories.map((c) => (
          <div key={c.name} className="cat-item">
            <div className="cat-row">
              <span className="cat-name">{c.name}</span>
              <span className="cat-score" style={{ color: c.color }}>{c.score}<span className="cat-denom">/100</span></span>
            </div>
            <div className="progress-track">
              <div
                className="progress-fill"
                style={{
                  width: `${c.score}%`,
                  background: c.color,
                  animation: "barGrow .9s cubic-bezier(.22,1,.36,1) both",
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
