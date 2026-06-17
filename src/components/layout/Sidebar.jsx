import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard, History, LogOut, Menu, X,
  Sparkles, ChevronRight, LogIn, UserPlus,
  FileText, Trash2, Clock,
} from "lucide-react";
import { Briefcase } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import AuthModal from "../ui/AuthModal";
import "./Sidebar.css";

export default function Sidebar() {
  const navigate         = useNavigate();
  const { pathname }     = useLocation();
  const { user, logout, history, deleteAnalysis } = useAuth();

  const [open,      setOpen]      = useState(false);
  const [authModal, setAuthModal] = useState(null); // "login" | "signup" | null
  const [showHist,  setShowHist]  = useState(false);

  const go = (path) => { navigate(path); setOpen(false); };

  const scoreColor = (s) => {
    if (s >= 75) return "#10B981";
    if (s >= 50) return "#F59E0B";
    return "#EF4444";
  };

  const formatDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
  };

  return (
    <>
      {/* Mobile hamburger */}
      <button className="sidebar-hamburger" onClick={() => setOpen(true)}>
        <Menu size={20} />
      </button>

      {open && <div className="sidebar-backdrop" onClick={() => setOpen(false)} />}

      <aside className={`sidebar${open ? " sidebar--open" : ""}`}>

        {/* ── Logo ── */}
        <div className="sidebar-logo" onClick={() => go("/")} style={{ cursor: "pointer" }}>
          <div className="sidebar-logo-icon"><Sparkles size={16} /></div>
          <span className="sidebar-logo-name">ResumeAI</span>
          <button className="sidebar-close" onClick={(e) => { e.stopPropagation(); setOpen(false); }}>
            <X size={16} />
          </button>
        </div>

        <div className="sidebar-divider" />

        {/* ── Nav ── */}
        <nav className="sidebar-nav">
          <p className="sidebar-section-label">Workspace</p>

          {/* Dashboard */}
          <button
            className={`sidebar-item${pathname === "/dashboard" ? " sidebar-item--active" : ""}`}
            onClick={() => go("/dashboard")}
          >
            <LayoutDashboard size={16} />
            <span>Dashboard</span>
            {pathname === "/dashboard" && <ChevronRight size={13} className="sidebar-item-arrow" />}
          </button>


<button
  className={`sidebar-item${pathname === "/jobs" ? " sidebar-item--active" : ""}`}
  onClick={() => go("/jobs")}
>
  <Briefcase size={16} />
  <span>Job Recommender</span>
  {pathname === "/jobs" && <ChevronRight size={13} className="sidebar-item-arrow" />}
</button>
          {/* History — only shown to logged in users */}
          {user && (
            <button
              className={`sidebar-item${showHist ? " sidebar-item--active" : ""}`}
              onClick={() => setShowHist(v => !v)}
            >
              <History size={16} />
              <span>History</span>
              {history.length > 0 && (
                <span className="sidebar-badge">{history.length}</span>
              )}
              <ChevronRight
                size={13}
                className="sidebar-item-arrow"
                style={{ transform: showHist ? "rotate(90deg)" : "none", transition: "transform .2s" }}
              />
            </button>
          )}

          {/* History panel */}
          {user && showHist && (
            <div className="sidebar-history">
              {history.length === 0 ? (
                <p className="sidebar-history-empty">No analyses yet</p>
              ) : (
                history.slice(0, 8).map(h => (
                  <div
                    key={h.id}
                    className="sidebar-history-item"
                    onClick={() => {
                      navigate("/results", { state: { result: h.result } });
                      setOpen(false);
                    }}
                  >
                    <div className="sidebar-history-left">
                      <FileText size={12} />
                      <div>
                        <span className="sidebar-history-role">{h.role}</span>
                        <span className="sidebar-history-date">
                          <Clock size={10} /> {formatDate(h.date)}
                        </span>
                      </div>
                    </div>
                    <div className="sidebar-history-right">
                      <span
                        className="sidebar-history-score"
                        style={{ color: scoreColor(h.score) }}
                      >{h.score}</span>
                      <button
                        className="sidebar-history-del"
                        onClick={e => { e.stopPropagation(); deleteAnalysis(h.id); }}
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </nav>

        {/* ── Footer ── */}
        <div className="sidebar-footer">
          <div className="sidebar-divider" />

          {user ? (
            /* Logged in state */
            <>
              <div className="sidebar-user">
                <div className="sidebar-avatar">{user.initials}</div>
                <div className="sidebar-user-info">
                  <span className="sidebar-user-name">{user.name}</span>
                  <span className="sidebar-user-role">Free Plan</span>
                </div>
              </div>
              <button
                className="sidebar-item sidebar-logout"
                onClick={() => { logout(); go("/"); }}
              >
                <LogOut size={16} />
                <span>Log out</span>
              </button>
            </>
          ) : (
            /* Guest state */
            <div className="sidebar-auth-btns">
              <p className="sidebar-auth-hint">Sign in to save your analyses</p>
              <button
                className="sidebar-item sidebar-signin-btn"
                onClick={() => setAuthModal("login")}
              >
                <LogIn size={16} />
                <span>Sign In</span>
              </button>
              <button
                className="sidebar-item sidebar-signup-btn"
                onClick={() => setAuthModal("signup")}
              >
                <UserPlus size={16} />
                <span>Create Account</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Auth Modal */}
      {authModal && (
        <AuthModal
          defaultTab={authModal}
          onClose={() => setAuthModal(null)}
        />
      )}
    </>
  );
}
