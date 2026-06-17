import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Upload, Briefcase, Sparkles, ChevronRight,
  Star, TrendingUp, Target, X, FileText,
  BookOpen, DollarSign, Zap, AlertCircle,
} from "lucide-react";
import AppLayout from "../components/layout/AppLayout.jsx";
import "./JobsPage.css";

const API_URL = "http://127.0.0.1:8000";

// ── Small reusable components ────────────────────────────────────────────────

function SkillTag({ name, type }) {
  return (
    <span className={`job-skill-tag job-skill-tag--${type}`}>{name}</span>
  );
}

function DemandBadge({ demand }) {
  const color = {
    "Extremely High": "#8B5CF6",
    "Very High":      "#10B981",
    "High":           "#3B82F6",
    "Medium":         "#F59E0B",
  }[demand] || "#6B7280";
  return (
    <span className="job-demand-badge" style={{ color, borderColor: color + "33", background: color + "11" }}>
      <Zap size={10} /> {demand}
    </span>
  );
}

function ScoreRing({ score, color }) {
  const r   = 26;
  const circ = 2 * Math.PI * r;
  const fill = (score / 100) * circ;
  return (
    <div className="job-score-ring">
      <svg width="68" height="68" viewBox="0 0 68 68">
        <circle cx="34" cy="34" r={r} fill="none" stroke="#E2E8F0" strokeWidth="5" />
        <circle
          cx="34" cy="34" r={r} fill="none"
          stroke={color} strokeWidth="5"
          strokeDasharray={`${fill} ${circ - fill}`}
          strokeLinecap="round"
          transform="rotate(-90 34 34)"
          style={{ transition: "stroke-dasharray 1s ease" }}
        />
      </svg>
      <div className="job-score-ring-text">
        <span className="job-score-num" style={{ color }}>{score}</span>
        <span className="job-score-pct">%</span>
      </div>
    </div>
  );
}

function JobCard({ job, index }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className={`job-card job-card--${job.matchLabel.toLowerCase().replace(" ", "-")}`}>
      <div className="job-card-top">
        <div className="job-card-left">
          <div className="job-card-emoji">{job.emoji}</div>
          <div>
            <h3 className="job-card-title">{job.title}</h3>
            <div className="job-card-meta">
              <span className="job-card-category">{job.category}</span>
              <DemandBadge demand={job.demand} />
            </div>
          </div>
        </div>
        <ScoreRing score={job.score} color={job.matchColor} />
      </div>

      <p className="job-card-desc">{job.description}</p>

      {/* Salary */}
      <div className="job-card-salary">
        <DollarSign size={13} />
        <span>{job.salaryPKR}</span>
        <span className="job-card-salary-usd">· {job.salaryUSD}</span>
      </div>

      {/* Matched skills */}
      {job.matchedSkills.length > 0 && (
        <div className="job-card-skills">
          <span className="job-card-skills-label">✅ You have:</span>
          <div className="job-card-skill-tags">
            {job.matchedSkills.map(s => <SkillTag key={s} name={s} type="matched" />)}
          </div>
        </div>
      )}

      {/* Missing core */}
      {job.missingCore.length > 0 && (
        <div className="job-card-skills">
          <span className="job-card-skills-label">❌ Missing core:</span>
          <div className="job-card-skill-tags">
            {job.missingCore.map(s => <SkillTag key={s} name={s} type="missing-core" />)}
          </div>
        </div>
      )}

      {/* Expand for tip */}
      <button className="job-card-expand" onClick={() => setExpanded(v => !v)}>
        <BookOpen size={13} />
        {expanded ? "Hide" : "What to learn to qualify"}
        <ChevronRight size={13} style={{ transform: expanded ? "rotate(90deg)" : "none", transition: ".2s" }} />
      </button>

      {expanded && (
        <div className="job-card-tip">
          <Sparkles size={13} />
          <p>{job.tip}</p>
        </div>
      )}
    </div>
  );
}

function SectionHeader({ icon: Icon, label, count, color }) {
  return (
    <div className="jobs-section-header" style={{ "--accent": color }}>
      <div className="jobs-section-icon" style={{ background: color + "18", color }}>
        <Icon size={16} />
      </div>
      <h2 className="jobs-section-title">{label}</h2>
      <span className="jobs-section-count" style={{ background: color + "18", color }}>{count}</span>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────

export default function JobsPage() {
  const navigate  = useNavigate();
  const inputRef  = useRef(null);

  const [file,    setFile]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");
  const [result,  setResult]  = useState(null);

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files supported.");
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      setError("File too large — max 5 MB.");
      return;
    }
    setFile(f);
    setError("");
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_URL}/recommend-jobs`, { method: "POST", body: form });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error ${res.status}`);
      }
      setResult(await res.json());
    } catch (err) {
      setError(err.message || "Something went wrong. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <AppLayout>
      <div className="jobs-page page-enter">

        {/* ── Hero header ── */}
        <div className="jobs-hero">
          <div className="jobs-hero-icon"><Briefcase size={22} /></div>
          <div>
            <h1 className="jobs-hero-title">Job Recommender</h1>
            <p className="jobs-hero-sub">
              Upload your CV and our AI agent will match you with the best job roles
            </p>
          </div>
        </div>

        {/* ── Upload card ── */}
        {!result && (
          <div className="jobs-upload-card card">
            <div className="jobs-upload-inner">
              {/* Drop zone */}
              <div
                className={`jobs-dropzone${file ? " jobs-dropzone--has-file" : ""}`}
                onDragOver={e => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => !file && inputRef.current?.click()}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".pdf"
                  style={{ display: "none" }}
                  onChange={e => handleFile(e.target.files[0])}
                />

                {file ? (
                  <div className="jobs-file-preview">
                    <div className="jobs-file-icon"><FileText size={28} /></div>
                    <div className="jobs-file-info">
                      <span className="jobs-file-name">{file.name}</span>
                      <span className="jobs-file-size">
                        {(file.size / 1024).toFixed(0)} KB · PDF
                      </span>
                    </div>
                    <button
                      className="jobs-file-remove"
                      onClick={e => { e.stopPropagation(); setFile(null); }}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ) : (
                  <div className="jobs-dropzone-empty">
                    <div className="jobs-upload-icon"><Upload size={26} /></div>
                    <p className="jobs-drop-title">Drop your CV here</p>
                    <p className="jobs-drop-sub">or click to browse · PDF only · Max 5 MB</p>
                  </div>
                )}
              </div>

              {error && (
                <div className="jobs-error">
                  <AlertCircle size={14} /> {error}
                </div>
              )}

              <button
                className="jobs-analyze-btn"
                onClick={handleAnalyze}
                disabled={!file || loading}
              >
                {loading ? (
                  <><span className="jobs-spinner" /> Analyzing your CV…</>
                ) : (
                  <><Sparkles size={16} /> Find Matching Jobs</>
                )}
              </button>

              <p className="jobs-upload-note">
                No job description needed — the agent figures it out from your CV
              </p>
            </div>

            {/* How it works */}
            <div className="jobs-how">
              <p className="jobs-how-title">How it works</p>
              {[
                { step: "1", text: "Upload your CV PDF" },
                { step: "2", text: "Agent extracts your skills and experience level" },
                { step: "3", text: "Scores your profile against 35+ job roles" },
                { step: "4", text: "Shows personalized matches with learning tips" },
              ].map(s => (
                <div key={s.step} className="jobs-how-step">
                  <span className="jobs-how-num">{s.step}</span>
                  <span>{s.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Results ── */}
        {result && (
          <div className="jobs-results page-enter">

            {/* Summary banner */}
            <div className="jobs-summary-banner">
              <div className="jobs-summary-left">
                <div className="jobs-summary-icon"><Sparkles size={18} /></div>
                <div>
                  <p className="jobs-summary-text">{result.summary}</p>
                  <div className="jobs-summary-tags">
                    <span className="jobs-summary-tag">
                      🎯 {result.experienceLevel}
                    </span>
                    <span className="jobs-summary-tag">
                      💼 {result.primaryField}
                    </span>
                    <span className="jobs-summary-tag">
                      🔧 {result.cvSkills.length} skills detected
                    </span>
                  </div>
                </div>
              </div>
              <button
                className="jobs-retry-btn"
                onClick={() => { setResult(null); setFile(null); }}
              >
                Try another CV
              </button>
            </div>

            {/* Detected skills */}
            <div className="jobs-detected-skills card">
              <p className="jobs-detected-label">Skills detected in your CV</p>
              <div className="jobs-detected-tags">
                {result.cvSkills.map(s => (
                  <span key={s} className="jobs-detected-tag">{s}</span>
                ))}
              </div>
            </div>

            {/* Best Matches */}
            {result.best.length > 0 && (
              <section className="jobs-section">
                <SectionHeader
                  icon={Star}
                  label="Best Matches"
                  count={result.best.length}
                  color="#10B981"
                />
                <div className="jobs-grid">
                  {result.best.map((job, i) => <JobCard key={job.title} job={job} index={i} />)}
                </div>
              </section>
            )}

            {/* Good Matches */}
            {result.good.length > 0 && (
              <section className="jobs-section">
                <SectionHeader
                  icon={TrendingUp}
                  label="Good Matches"
                  count={result.good.length}
                  color="#3B82F6"
                />
                <div className="jobs-grid">
                  {result.good.map((job, i) => <JobCard key={job.title} job={job} index={i} />)}
                </div>
              </section>
            )}

            {/* Stretch Goals */}
            {result.stretch.length > 0 && (
              <section className="jobs-section">
                <SectionHeader
                  icon={Target}
                  label="Stretch Goals"
                  count={result.stretch.length}
                  color="#F59E0B"
                />
                <p className="jobs-stretch-note">
                  These roles need a few more skills — but they're achievable with focused learning.
                </p>
                <div className="jobs-grid">
                  {result.stretch.map((job, i) => <JobCard key={job.title} job={job} index={i} />)}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
