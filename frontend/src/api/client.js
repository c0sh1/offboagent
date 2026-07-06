import { getToken, clearToken } from "./authToken";

const API_BASE_URL = "http://127.0.0.1:8000";

let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    clearToken();
    onUnauthorized();
    throw new Error("Sesión expirada. Vuelve a iniciar sesión.");
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Error ${response.status}`);
  }

  return response.json();
}

export const api = {
  register: (payload) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) =>
    request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  getMe: () => request("/auth/me"),

  listPersons: () => request("/persons"),
  getPerson: (personId) => request(`/persons/${personId}`),
  createPerson: (payload) =>
    request("/persons", { method: "POST", body: JSON.stringify(payload) }),
  addAccessGrant: (personId, payload) =>
    request(`/persons/${personId}/access-grants`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  startOffboarding: (payload) =>
    request("/offboarding", { method: "POST", body: JSON.stringify(payload) }),
  getOffboardingEvent: (eventId) => request(`/offboarding/${eventId}`),
  listOffboardingEvents: () => request("/offboarding"),

  getOrphanedAccess: () => request("/security/orphaned-access"),

  getDashboardStats: () => request("/dashboard/stats"),

  listSystems: () => request("/systems"),
};