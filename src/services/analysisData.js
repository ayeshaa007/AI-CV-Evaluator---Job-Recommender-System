/* services/analysisData.js — mock result payload */

export const MOCK_RESULT = {
  overallScore: 78,
  jobRole: "Software Engineer",
  categories: [
    { name: "Skills Match",      score: 85, color: "#2563EB" },
    { name: "Experience",        score: 75, color: "#7C3AED" },
    { name: "Education",         score: 90, color: "#10B981" },
    { name: "ATS Keywords",      score: 70, color: "#F59E0B" },
    { name: "Format & Clarity",  score: 65, color: "#EF4444" },
  ],
  matchedSkills: [
    "React.js", "JavaScript", "TypeScript", "Node.js", "Python",
    "Git", "REST APIs", "MongoDB", "Problem Solving", "Team Collaboration",
  ],
  missingSkills: [
    { name: "Docker",         priority: "High"   },
    { name: "Kubernetes",     priority: "High"   },
    { name: "AWS / Cloud",    priority: "High"   },
    { name: "CI/CD",          priority: "Medium" },
    { name: "GraphQL",        priority: "Medium" },
    { name: "Jest / Testing", priority: "Low"    },
  ],
  strengths: [
    "Strong technical skill set well-aligned with the role",
    "Clear, well-structured resume format",
    "Measurable achievements included in experience",
    "Relevant project experience demonstrated",
    "Good academic background for the position",
  ],
  weaknesses: [
    "Missing key cloud / DevOps technologies",
    "Limited mention of CI/CD pipelines",
    "Professional summary could be more impactful",
    "Quantifiable metrics sparse in some roles",
  ],
  suggestions: [
    {
      title:  "Add Cloud & DevOps Skills",
      impact: "High",
      desc:   "Docker, Kubernetes, and AWS appear in 87% of senior engineering job postings. Add them or pursue a short certification.",
    },
    {
      title:  "Quantify Your Achievements",
      impact: "High",
      desc:   'Replace vague bullets with metrics — e.g., "reduced build time by 40%" or "served 1M+ monthly users".',
    },
    {
      title:  "Strengthen the Professional Summary",
      impact: "Medium",
      desc:   "Write a 2–3 sentence summary that hooks the recruiter: your role, stack, and one differentiating win.",
    },
    {
      title:  "Include Relevant Certifications",
      impact: "Medium",
      desc:   "AWS Certified Developer or equivalent cloud certification significantly boosts ATS keyword density.",
    },
  ],
};
