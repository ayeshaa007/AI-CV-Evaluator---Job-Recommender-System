import { useState } from "react";
import { X, Mail, Lock, User, Eye, EyeOff, Sparkles, ArrowRight } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import "./AuthModal.css";

export default function AuthModal({ onClose, defaultTab = "login" }) {
  const { login, signup } = useAuth();
  const [tab,     setTab]     = useState(defaultTab); // "login" | "signup"
  const [name,    setName]    = useState("");
  const [email,   setEmail]   = useState("");
  const [pass,    setPass]    = useState("");
  const [showPw,  setShowPw]  = useState(false);
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const handle = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (tab === "login") {
        await login(email, pass);
      } else {
        if (!name.trim()) throw new Error("Please enter your name");
        if (pass.length < 6) throw new Error("Password must be at least 6 characters");
        await signup(name.trim(), email, pass);
      }
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="auth-modal">
        {/* Close */}
        <button className="auth-close" onClick={onClose}><X size={16} /></button>

        {/* Logo */}
        <div className="auth-logo">
          <div className="auth-logo-icon"><Sparkles size={14} /></div>
          <span>ResumeAI</span>
        </div>

        {/* Title */}
        <h2 className="auth-title">
          {tab === "login" ? "Welcome back" : "Create your account"}
        </h2>
        <p className="auth-sub">
          {tab === "login"
            ? "Sign in to access your analysis history"
            : "Sign up to save and track your CV analyses"}
        </p>

        {/* Tabs */}
        <div className="auth-tabs">
          <button
            className={`auth-tab ${tab === "login" ? "auth-tab--active" : ""}`}
            onClick={() => { setTab("login"); setError(""); }}
          >Sign In</button>
          <button
            className={`auth-tab ${tab === "signup" ? "auth-tab--active" : ""}`}
            onClick={() => { setTab("signup"); setError(""); }}
          >Sign Up</button>
        </div>

        {/* Form */}
        <form className="auth-form" onSubmit={handle}>
          {tab === "signup" && (
            <div className="auth-field">
              <label>Full Name</label>
              <div className="auth-input-wrap">
                <User size={15} className="auth-input-icon" />
                <input
                  type="text"
                  placeholder="Ayesha Khan"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          <div className="auth-field">
            <label>Email</label>
            <div className="auth-input-wrap">
              <Mail size={15} className="auth-input-icon" />
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="auth-field">
            <label>Password</label>
            <div className="auth-input-wrap">
              <Lock size={15} className="auth-input-icon" />
              <input
                type={showPw ? "text" : "password"}
                placeholder="••••••••"
                value={pass}
                onChange={e => setPass(e.target.value)}
                required
              />
              <button
                type="button"
                className="auth-pw-toggle"
                onClick={() => setShowPw(v => !v)}
              >
                {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button className="auth-submit" disabled={loading}>
            {loading ? (
              <span className="auth-spinner" />
            ) : (
              <>
                {tab === "login" ? "Sign In" : "Create Account"}
                <ArrowRight size={15} />
              </>
            )}
          </button>
        </form>

        {/* Switch tab */}
        <p className="auth-switch">
          {tab === "login" ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => { setTab(tab === "login" ? "signup" : "login"); setError(""); }}>
            {tab === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>

        {/* Guest note */}
        <p className="auth-guest-note">
          You can also <button onClick={onClose}>continue as guest</button> — analyses won't be saved
        </p>
      </div>
    </div>
  );
}
