import { useNavigate, useLocation } from "react-router-dom";
import { ArrowLeft, Download, RefreshCw } from "lucide-react";
import AppLayout         from "../components/layout/AppLayout.jsx";
import ScoreCard         from "../components/results/ScoreCard.jsx";
import CategoryBreakdown from "../components/results/CategoryBreakdown.jsx";
import SkillsCard        from "../components/results/SkillsCard.jsx";
import { StrengthsCard, WeaknessesCard } from "../components/results/StrengthsWeaknesses.jsx";
import SuggestionsCard   from "../components/results/SuggestionsCard.jsx";
import { MOCK_RESULT }   from "../services/analysisData.js";
import "./ResultsPage.css";

export default function ResultsPage() {
  const navigate  = useNavigate();
  const location  = useLocation();

  // Use real backend result if available; otherwise fall back to mock data
  const r = location.state?.result ?? MOCK_RESULT;

  return (
    <AppLayout>
      <div className="results-page page-enter">
        {/* Header */}
        <div className="results-header">
          <button className="btn btn-secondary btn-sm" onClick={() => navigate("/dashboard")}>
            <ArrowLeft size={14} /> Back
          </button>
          <div className="results-header-mid">
            <h1 className="results-title">Analysis Report</h1>
            <p className="results-sub">Compared against: <strong>{r.jobRole}</strong></p>
          </div>
          <div className="results-header-actions">
            <button className="btn btn-secondary btn-sm" onClick={() => navigate("/dashboard")}>
              <RefreshCw size={13} /> New analysis
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => window.print()}>
              <Download size={13} /> Download PDF
            </button>
          </div>
        </div>

        {/* Score + Breakdown */}
        <div className="results-top-grid">
          <ScoreCard score={r.overallScore} jobRole={r.jobRole} />
          <CategoryBreakdown categories={r.categories} />
        </div>

        {/* Skills */}
        <section className="results-section">
          <h2 className="results-section-title">Skill Analysis</h2>
          <SkillsCard matched={r.matchedSkills} missing={r.missingSkills} />
        </section>

        {/* Strengths & Weaknesses */}
        <section className="results-section">
          <h2 className="results-section-title">Strengths &amp; Areas to Improve</h2>
          <div className="results-sw-grid">
            <StrengthsCard  strengths={r.strengths}   />
            <WeaknessesCard weaknesses={r.weaknesses} />
          </div>
        </section>

        {/* Suggestions */}
        <section className="results-section">
          <h2 className="results-section-title">AI Recommendations</h2>
          <SuggestionsCard suggestions={r.suggestions} />
        </section>

        {/* Footer CTA */}
        <div className="results-footer-cta card">
          <div className="results-footer-cta-text">
            <h3>Ready to revise your CV?</h3>
            <p>Apply the suggestions above, then re-analyse to track your improvement.</p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate("/dashboard")}>
            <RefreshCw size={15} /> Analyse again
          </button>
        </div>
      </div>
    </AppLayout>
  );
}
