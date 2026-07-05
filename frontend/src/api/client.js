const API_BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Error ${response.status}`);
  }

  return response.json();
}

export const api = {
  listPersons: () => request("/persons"),
  getPerson: (personId) => request(`/persons/${personId}`),
  startOffboarding: (payload) =>
    request("/offboarding", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getOffboardingEvent: (eventId) => request(`/offboarding/${eventId}`),
  getOrphanedAccess: () => request("/security/orphaned-access"),
};