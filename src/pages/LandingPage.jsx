import { useNavigate } from "react-router-dom";
import { Sparkles, ArrowRight, CheckCircle2, FileText, Target, Zap, BarChart2, Shield } from "lucide-react";
import "./LandingPage.css";
import { Link} from "react-router-dom";

const FEATURES = [
  { icon: FileText,  title: "Smart CV Parsing",    desc: "Extracts and structures every section of your resume with high accuracy." },
  { icon: Target,    title: "Job Match Scoring",   desc: "Compares your CV against job descriptions to produce a precise fit score." },
  { icon: Zap,       title: "Instant Feedback",    desc: "Get prioritised, actionable suggestions within seconds of uploading." },
  { icon: BarChart2, title: "ATS Compatibility",   desc: "Checks keyword density, formatting, and readability for ATS systems." },
];

const STEPS = [
  { n: "01", title: "Upload your CV",          desc: "Drop a PDF — we parse everything." },
  { n: "02", title: "Enter the job details",   desc: "Add role and paste the job description." },
  { n: "03", title: "Get your report",         desc: "Receive a detailed score with fixes." },
];

const STATS = [
  { value: "98%",  label: "Parsing accuracy"  },
  { value: "50K+", label: "CVs analysed"       },
  { value: "4.9",  label: "Average rating"     },
  { value: "< 5s", label: "Analysis time"      },
];

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      {/* ── Nav ── */}
      <header className="landing-nav">
        <div className="landing-container">
          <div className="landing-nav-inner">
       <Link to="/" className="landing-logo">
  <div className="landing-logo-icon">
    <Sparkles size={15} />
  </div>
  <span className="landing-logo-name">ResumeAI</span>
</Link>
            <nav className="landing-nav-links">
              <a href="#features">Features</a>
              <a href="#how">How it works</a>
            </nav>
            <button className="btn btn-primary btn-sm" onClick={() => navigate("/dashboard")}>
              Get started <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="landing-hero">
        <div className="landing-container">
          <div className="landing-hero-inner">
            <div className="landing-hero-badge">
              <Sparkles size={12} /> Powered by AI & NLP
            </div>
            <h1 className="landing-hero-title">
              Optimize your resume<br />
              <span className="landing-hero-accent">for any job in seconds</span>
            </h1>
            <p className="landing-hero-sub">
              Upload your CV, paste the job description, and get a detailed ATS score with
              prioritised suggestions — so you can apply with confidence.
            </p>
            <div className="landing-hero-btns">
              <button className="btn btn-primary btn-lg" onClick={() => navigate("/dashboard")}>
                Analyze my CV <ArrowRight size={16} />
              </button>
              <button className="btn btn-secondary btn-lg">See sample report</button>
            </div>
            {/* Trust line */}
            <div className="landing-trust">
              {["No account needed", "100% private", "Free to try"].map((t) => (
                <span key={t} className="landing-trust-item">
                  <CheckCircle2 size={13} /> {t}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Stats strip */}
        <div className="landing-stats-strip">
          <div className="landing-container">
            <div className="landing-stats">
              {STATS.map((s) => (
                <div key={s.label} className="landing-stat">
                  <span className="landing-stat-value">{s.value}</span>
                  <span className="landing-stat-label">{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="landing-section" id="features">
        <div className="landing-container">
          <div className="landing-section-head">
            <span className="landing-eyebrow">Features</span>
            <h2 className="landing-section-title">Everything you need to land the interview</h2>
            <p className="landing-section-sub">
              Built for job seekers who want real feedback, not vague tips.
            </p>
          </div>
          <div className="landing-features-grid">
            {FEATURES.map((f, i) => (
              <div key={i} className="card landing-feature-card">
                <div className="landing-feature-icon">
                  <f.icon size={18} />
                </div>
                <h3 className="landing-feature-title">{f.title}</h3>
                <p className="landing-feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="landing-section landing-how-section" id="how">
        <div className="landing-container">
          <div className="landing-section-head">
            <span className="landing-eyebrow">How it works</span>
            <h2 className="landing-section-title">Three steps to a better CV</h2>
          </div>
          <div className="landing-steps">
            {STEPS.map((s, i) => (
              <div key={i} className="landing-step">
                <span className="landing-step-num">{s.n}</span>
                <h3 className="landing-step-title">{s.title}</h3>
                <p className="landing-step-desc">{s.desc}</p>
                {i < STEPS.length - 1 && <div className="landing-step-arrow">→</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="landing-section">
        <div className="landing-container">
          <div className="landing-cta-card card">
            <Shield size={36} className="landing-cta-icon" />
            <h2 className="landing-cta-title">Ready to optimize your CV?</h2>
            <p className="landing-cta-sub">
              Join 50,000+ job seekers who have improved their applications with ResumeAI.
            </p>
            <button className="btn btn-primary btn-lg" onClick={() => navigate("/dashboard")}>
              Analyze for free <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="landing-container">
          <div className="landing-footer-inner">
            <div className="landing-logo">
              <div className="landing-logo-icon"><Sparkles size={15} /></div>
              <span className="landing-logo-name">ResumeAI</span>
            </div>
            <p className="landing-footer-copy">© 2026 ResumeAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
