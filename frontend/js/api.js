export const API_BASE_URL = "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ? JSON.stringify(body.detail) : JSON.stringify(body);
    } catch (e) {
      // response had no JSON body; fall back to statusText
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function createProspect(data) {
  const response = await fetch(`${API_BASE_URL}/api/prospects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

export async function getRunStatus(runId) {
  const response = await fetch(`${API_BASE_URL}/api/runs/${runId}/status`);
  return handleResponse(response);
}

export async function getRunDetail(runId) {
  const response = await fetch(`${API_BASE_URL}/api/runs/${runId}`);
  return handleResponse(response);
}

export async function getRuns(params = {}) {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE_URL}/api/runs${query ? `?${query}` : ""}`);
  return handleResponse(response);
}

export async function retryRun(runId) {
  const response = await fetch(`${API_BASE_URL}/api/runs/${runId}/retry`, { method: "POST" });
  return handleResponse(response);
}

export async function submitReview(draftId, data) {
  const response = await fetch(`${API_BASE_URL}/api/drafts/${draftId}/review`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

export async function getMetrics() {
  const response = await fetch(`${API_BASE_URL}/api/metrics`);
  return handleResponse(response);
}
