import { useEffect, useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import "./LoadingAnimation.css";

const STEPS = [
  "Uploading and parsing PDF…",
  "Extracting sections & content…",
  "Running ATS compatibility check…",
  "Matching skills to job description…",
  "Calculating category scores…",
  "Generating AI recommendations…",
];

export default function LoadingAnimation({ onComplete }) {
  const [progress, setProgress]   = useState(0);
  const [stepIdx, setStepIdx]     = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setProgress((p) => {
        const next = p + 1.4;
        if (next >= 100) {
          clearInterval(id);
          setTimeout(onComplete, 600);
          return 100;
        }
        setStepIdx(Math.min(Math.floor((next / 100) * STEPS.length), STEPS.length - 1));
        return next;
      });
    }, 50);
    return () => clearInterval(id);
  }, [onComplete]);

  return (
    <div className="la-wrap">
      <div className="la-card card">
        {/* Spinner */}
        <div className="la-spinner-ring">
          <div className="la-spinner-track" />
          <svg className="la-spinner-svg" viewBox="0 0 80 80">
            <circle
              cx="40" cy="40" r="34"
              fill="none"
              stroke="var(--blue)"
              strokeWidth="5"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 34}`}
              strokeDashoffset={`${2 * Math.PI * 34 * (1 - progress / 100)}`}
              style={{ transition: "stroke-dashoffset .2s linear", transform: "rotate(-90deg)", transformOrigin: "center" }}
            />
          </svg>
          <div className="la-spinner-pct">{Math.round(progress)}%</div>
        </div>

        <h2 className="la-title">Analyzing your CV…</h2>
        <p className="la-sub">This usually takes a few seconds</p>

        {/* Progress bar */}
        <div className="la-bar-wrap">
          <div className="progress-track la-bar-track">
            <div
              className="progress-fill"
              style={{ width: `${progress}%`, background: "var(--blue)" }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="la-steps">
          {STEPS.map((s, i) => {
            const done    = i < stepIdx;
            const current = i === stepIdx;
            return (
              <div key={i} className={`la-step${done ? " la-step--done" : current ? " la-step--current" : " la-step--pending"}`}>
                <div className="la-step-icon">
                  {done
                    ? <CheckCircle2 size={14} />
                    : current
                    ? <Loader2 size={14} className="la-spin" />
                    : <span className="la-step-num">{i + 1}</span>
                  }
                </div>
                <span className="la-step-label">{s}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
