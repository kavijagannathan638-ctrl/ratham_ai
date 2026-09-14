const BASE = 'http://localhost:8000';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('ratham_token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(BASE + path, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Server error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const authApi = {
  login: (email, password) => apiFetch('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  me: () => apiFetch('/api/v1/auth/me'),
  register: (data) => apiFetch('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(data) }),
};

export const analyticsApi = {
  overview: () => apiFetch('/api/v1/analytics/overview'),
  models: () => apiFetch('/api/v1/analytics/models'),
};

export const patientApi = {
  list: (params = '') => apiFetch(`/api/v1/patients${params}`),
  get: (id) => apiFetch(`/api/v1/patients/${id}`),
  create: (data) => apiFetch('/api/v1/patients', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => apiFetch(`/api/v1/patients/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  predictions: (id) => apiFetch(`/api/v1/patients/${id}/predictions`),
  timeline: (id) => apiFetch(`/api/v1/patients/${id}/timeline`),
};

export const donorApi = {
  list: (params = '') => apiFetch(`/api/v1/donors${params}`),
  get: (id) => apiFetch(`/api/v1/donors/${id}`),
  create: (data) => apiFetch('/api/v1/donors', { method: 'POST', body: JSON.stringify(data) }),
  updateAvailability: (id, status) => apiFetch(`/api/v1/donors/${id}/availability`, { method: 'PATCH', body: JSON.stringify({ availability_status: status }) }),
  risk: (id) => apiFetch(`/api/v1/donors/${id}/risk`),
};

export const predictionApi = {
  need: (data) => apiFetch('/api/v1/predictions/need', { method: 'POST', body: JSON.stringify(data) }),
  reachability: (data) => apiFetch('/api/v1/predictions/reachability', { method: 'POST', body: JSON.stringify(data) }),
};

export const matchingApi = {
  rank: (data) => apiFetch('/api/v1/matching/rank', { method: 'POST', body: JSON.stringify(data) }),
};

export const emergencyApi = {
  list: (params = '') => apiFetch(`/api/v1/emergencies${params}`),
  get: (id) => apiFetch(`/api/v1/emergencies/${id}`),
  create: (data) => apiFetch('/api/v1/emergencies', { method: 'POST', body: JSON.stringify(data) }),
  activate: (id) => apiFetch(`/api/v1/emergencies/${id}/activate`, { method: 'POST' }),
  decline: (id) => apiFetch(`/api/v1/emergencies/${id}/decline`, { method: 'POST' }),
  confirm: (id, donor_id) => apiFetch(`/api/v1/emergencies/${id}/confirm${donor_id ? `?donor_id=${donor_id}` : ''}`, { method: 'POST' }),
};

export const orchestrationApi = {
  reset: () => apiFetch('/api/v1/demo/reset', { method: 'POST' }),
  processDecline: (id) => apiFetch(`/api/v1/demo/simulate-decline/${id}`, { method: 'POST' }),
  processConfirm: (id) => apiFetch(`/api/v1/demo/simulate-confirm/${id}`, { method: 'POST' }),
};
export const demoApi = orchestrationApi;

export const adminApi = {
  audits: () => apiFetch('/api/v1/admin/audits'),
  models: () => apiFetch('/api/v1/admin/models'),
};
