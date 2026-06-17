import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoadingAnimation from "../components/ui/LoadingAnimation.jsx";

const MIN_DISPLAY_MS = 3000; // always show animation for at least 3 seconds

export default function AnalyzingPage() {
  const navigate         = useNavigate();
  const { saveAnalysis } = useAuth();
  const hasNavigated     = useRef(false);
  const [animDone, setAnimDone]       = useState(false);
  const [apiResult, setApiResult]     = useState(null);
  const [apiError,  setApiError]      = useState(null);

  useEffect(() => {
    const promise = window.__cvAnalysisPromise;
    const meta    = window.__cvAnalysisMeta || {};

    if (!promise) {
      navigate("/dashboard");
      return;
    }

    // Start the minimum display timer
    const timer = setTimeout(() => setAnimDone(true), MIN_DISPLAY_MS);

    promise
      .then((result) => {
        delete window.__cvAnalysisPromise;
        delete window.__cvAnalysisMeta;
        saveAnalysis(result, meta.role || "Unknown Role", meta.fileName || "resume.pdf");
        setApiResult(result);
      })
      .catch((err) => {
        delete window.__cvAnalysisPromise;
        delete window.__cvAnalysisMeta;
        setApiError(err.message || "Analysis failed.");
      });

    return () => clearTimeout(timer);
  }, []);

  // Navigate only when BOTH animation timer done AND API responded
  useEffect(() => {
    if (hasNavigated.current) return;

    if (apiError && animDone) {
      hasNavigated.current = true;
      navigate("/dashboard", { state: { error: apiError } });
      return;
    }

    if (apiResult && animDone) {
      hasNavigated.current = true;
      navigate("/results", { state: { result: apiResult } });
    }
  }, [animDone, apiResult, apiError, navigate]);

  return <LoadingAnimation onComplete={() => {}} />;
}
