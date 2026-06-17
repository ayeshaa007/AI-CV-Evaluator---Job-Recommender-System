import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Brain, CheckCircle2, AlertCircle, Info, LogIn } from "lucide-react";
import AppLayout           from "../components/layout/AppLayout.jsx";
import UploadBox           from "../components/dashboard/UploadBox.jsx";
import JobRoleInput        from "../components/dashboard/JobRoleInput.jsx";
import JobDescriptionInput from "../components/dashboard/JobDescriptionInput.jsx";
import AuthModal           from "../components/ui/AuthModal.jsx";
import { useAuth }         from "../context/AuthContext";
import { analyzeResume }   from "../services/api";
import "./DashboardPage.css";

const ANALYZE_ITEMS = [
  "Skills & keyword matching",
  "ATS compatibility scoring",
  "Work experience relevance",
  "Education alignment",
  "Format & structure check",
  "Gap analysis vs. job description",
];

export default function DashboardPage() {
  const navigate      = useNavigate();
  const location      = useLocation();
  const { user, saveAnalysis } = useAuth();

  const [file,      setFile]      = useState(null);
  const [role,      setRole]      = useState("");
  const [jd,        setJd]        = useState("");
  const [error,     setError]     = useState(location.state?.error || "");
  const [loading,   setLoading]   = useState(false);
  const [authModal, setAuthModal] = useState(null);

  // Clear navigation error after reading it
  useEffect(() => {
    if (location.state?.error) {
      window.history.replaceState({}, "");
    }
  }, []);

  const canAnalyze = file && role.trim() && jd.trim() && !loading;

  const handleAnalyze = async () => {
    if (!canAnalyze) return;
    setError("");
    setLoading(true);

    try {
      const resultPromise = analyzeResume(file, role, jd);

      // Store promise + metadata for AnalyzingPage
      window.__cvAnalysisPromise  = resultPromise;
      window.__cvAnalysisMeta     = { role: role.trim(), fileName: file.name };

      navigate("/analyzing");
    } catch (err) {
      setError("Failed to start analysis. Make sure the backend is running.");
      setLoading(false);
    }
  };

  const wordCount = jd.trim().split(/\s+/).filter(Boolean).length;

  return (
    <AppLayout>
      <div className="dash-page page-enter">

        {/* Page header */}
        <div className="dash-page-header">
          <div>
            <h1 className="dash-page-title">Analyze your CV</h1>
            <p className="dash-page-sub">
              Upload your resume and provide the job details for a detailed match report
            </p>
          </div>
          {/* Show login prompt if guest */}
          {!user && (
            <button
              className="dash-login-prompt"
              onClick={() => setAuthModal("login")}
            >
              <LogIn size={14} />
              Sign in to save results
            </button>
          )}
        </div>

        <div className="dash-page-grid">
          {/* ── Left: inputs ── */}
          <div className="dash-inputs">

            <div className="card dash-step-card">
              <div className="dash-step-header">
                <span className="dash-step-badge">Step 1</span>
                <h2 className="dash-step-title">Upload your CV / Resume</h2>
                <p className="dash-step-desc">PDF format only, maximum 5 MB</p>
              </div>
              <UploadBox file={file} onChange={setFile} />
            </div>

            <div className="card dash-step-card">
              <div className="dash-step-header">
                <span className="dash-step-badge">Step 2</span>
                <h2 className="dash-step-title">Target job role</h2>
                <p className="dash-step-desc">The position you are applying for</p>
              </div>
              <JobRoleInput value={role} onChange={setRole} />
            </div>

            <div className="card dash-step-card">
              <div className="dash-step-header">
                <div className="dash-step-header-row">
                  <div>
                    <span className="dash-step-badge">Step 3</span>
                    <h2 className="dash-step-title">Job description</h2>
                    <p className="dash-step-desc">Paste the full job posting for best accuracy</p>
                  </div>
                  {wordCount > 0 && (
                    <span className="dash-jd-wordcount">{wordCount} words</span>
                  )}
                </div>
              </div>
              <JobDescriptionInput value={jd} onChange={setJd} />
            </div>

            {error && (
              <div className="dash-error-banner">
                <AlertCircle size={14} /> {error}
              </div>
            )}

            <div className="dash-analyze-wrap">
              {!canAnalyze && !loading && (
                <div className="dash-missing-hint">
                  <Info size={13} />
                  {!file && "Upload a CV · "}
                  {!role.trim() && "Enter a job role · "}
                  {!jd.trim() && "Paste a job description"}
                </div>
              )}
              <button
                className="btn btn-primary btn-lg btn-full"
                onClick={handleAnalyze}
                disabled={!canAnalyze}
              >
                <Brain size={18} />
                {loading ? "Analyzing…" : "Analyze with AI"}
              </button>
              {!user && (
                <p className="dash-guest-note">
                  Not signed in — results won't be saved.{" "}
                  <button onClick={() => setAuthModal("signup")}>Create a free account</button>
                </p>
              )}
            </div>
          </div>

          {/* ── Right: info panel ── */}
          <aside className="dash-aside">
            <div className="card dash-aside-card">
              <h3 className="dash-aside-title">What we analyze</h3>
              <ul className="dash-analyze-list">
                {ANALYZE_ITEMS.map((item, i) => (
                  <li key={i} className="dash-analyze-item">
                    <CheckCircle2 size={14} className="dash-check-icon" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div className="card dash-tip-card">
              <div className="dash-tip-head">
                <AlertCircle size={15} />
                <span>Tips for best results</span>
              </div>
              <ul className="dash-tip-list">
                <li>Use a standard, clean PDF layout</li>
                <li>Include measurable achievements</li>
                <li>Paste the <em>full</em> job description</li>
                <li>Avoid tables, headers/footers in PDF</li>
                <li>Keep your CV to 1–2 pages</li>
              </ul>
            </div>

            <div className="card dash-progress-card">
              <h3 className="dash-aside-title" style={{ marginBottom: 14 }}>Your checklist</h3>
              <div className="dash-checklist">
                {[
                  { label: "CV uploaded",       done: !!file        },
                  { label: "Job role entered",  done: !!role.trim() },
                  { label: "Job description",   done: !!jd.trim()   },
                ].map((c, i) => (
                  <div key={i} className={`dash-check-row${c.done ? " dash-check-row--done" : ""}`}>
                    <div className="dash-check-indicator">
                      {c.done ? <CheckCircle2 size={15} /> : <span className="dash-check-empty" />}
                    </div>
                    <span>{c.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* Auth modal */}
      {authModal && (
        <AuthModal defaultTab={authModal} onClose={() => setAuthModal(null)} />
      )}
    </AppLayout>
  );
}
