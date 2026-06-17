const API_URL = "http://127.0.0.1:8000";

/**
 * Sends the CV file + job details to the FastAPI backend.
 * Returns the full analysis result object.
 */
export async function analyzeResume(file, role, jd) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("role", role);
  formData.append("job_description", jd);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${response.status}`);
  }

  return response.json();
}
