import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import LandingPage   from "./pages/LandingPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import AnalyzingPage from "./pages/AnalyzingPage.jsx";
import ResultsPage   from "./pages/ResultsPage.jsx";
import ScrollToTop   from "./components/ScrollToTop.jsx";
import JobsPage from "./pages/JobsPage.jsx";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <Routes>
          <Route path="/"          element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analyzing" element={<AnalyzingPage />} />
          <Route path="/results"   element={<ResultsPage />} />
          <Route path="/jobs"      element={<JobsPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
