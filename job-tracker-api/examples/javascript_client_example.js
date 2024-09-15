/*
JavaScript Client Example (browser-compatible)
- Uses Fetch API for HTTP requests
- Demonstrates CRUD operations against Applications API
- Shows async/await and Promise-based error handling
- Includes examples for Tracking endpoints

How to use (in browser or with bundler):
- Set API_BASE_URL to your API endpoint (e.g., https://your-service-name.onrender.com)
- If your API requires an API key, set API_KEY and include the header
*/

const API_BASE_URL = (typeof window !== 'undefined' && window.API_BASE_URL)
  || (typeof process !== 'undefined' && process.env.API_BASE_URL)
  || 'https://your-service-name.onrender.com';

const API_KEY = (typeof window !== 'undefined' && window.API_KEY)
  || (typeof process !== 'undefined' && process.env.API_KEY)
  || null;

function buildHeaders(extra = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...extra,
  };
  if (API_KEY) headers['X-API-Key'] = API_KEY;
  return headers;
}

async function handleResponse(resp) {
  const contentType = resp.headers.get('content-type') || '';
  let data = null;
  if (contentType.includes('application/json')) {
    data = await resp.json().catch(() => null);
  } else {
    data = await resp.text().catch(() => null);
  }
  if (!resp.ok) {
    const error = new Error((data && (data.message || data.error)) || `HTTP ${resp.status}`);
    error.status = resp.status;
    error.data = data;
    throw error;
  }
  return data;
}

// CRUD Operations using async/await
export async function listApplications(params = {}) {
  const url = new URL(`${API_BASE_URL}/api/applications/`);
  Object.entries(params).forEach(([k, v]) => {
    if (Array.isArray(v)) v.forEach((val) => url.searchParams.append(k, val));
    else if (v !== undefined && v !== null) url.searchParams.set(k, v);
  });
  const resp = await fetch(url, { headers: buildHeaders() });
  return handleResponse(resp);
}

export async function createApplication(app) {
  const resp = await fetch(`${API_BASE_URL}/api/applications/`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(app),
  });
  return handleResponse(resp);
}

export async function getApplication(id) {
  const resp = await fetch(`${API_BASE_URL}/api/applications/${id}`, {
    headers: buildHeaders(),
  });
  return handleResponse(resp);
}

export async function updateApplication(id, patch) {
  const resp = await fetch(`${API_BASE_URL}/api/applications/${id}`, {
    method: 'PUT',
    headers: buildHeaders(),
    body: JSON.stringify(patch),
  });
  return handleResponse(resp);
}

export async function updateApplicationStatus(id, status) {
  const url = new URL(`${API_BASE_URL}/api/applications/${id}/status`);
  url.searchParams.set('status', status);
  const resp = await fetch(url, {
    method: 'PATCH',
    headers: buildHeaders(),
  });
  return handleResponse(resp);
}

export async function deleteApplication(id) {
  const resp = await fetch(`${API_BASE_URL}/api/applications/${id}`, {
    method: 'DELETE',
    headers: buildHeaders(),
  });
  return handleResponse(resp);
}

// Tracking endpoints
export async function quickTrack(payload) {
  const resp = await fetch(`${API_BASE_URL}/api/tracking/track`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(resp);
}

export async function getAnalyticsStats() {
  const resp = await fetch(`${API_BASE_URL}/api/tracking/stats`, {
    headers: buildHeaders(),
  });
  return handleResponse(resp);
}

export async function getApplicationHistory(appId) {
  const resp = await fetch(`${API_BASE_URL}/api/tracking/application-history/${appId}`, {
    headers: buildHeaders(),
  });
  return handleResponse(resp);
}

// Demo runner using async/await with try/catch
export async function runAsyncDemo() {
  try {
    // Create
    const created = await createApplication({
      company_name: 'Example Corp',
      job_title: 'Frontend Engineer',
      status: 'applied',
    });
    console.log('Created:', created);
    const id = (created && created.data && created.data.id) || created.id;

    // Read
    const fetched = await getApplication(id);
    console.log('Fetched:', fetched);

    // Update
    const updated = await updateApplication(id, {
      status: 'reviewing',
      notes: 'Screening scheduled',
    });
    console.log('Updated:', updated);

    // Patch status
    const patched = await updateApplicationStatus(id, 'phone_screen');
    console.log('Patched status:', patched);

    // List
    const list = await listApplications({ limit: 5 });
    console.log('List:', list);

    // Tracking
    const tracked = await quickTrack({ company: 'TrackCo', title: 'Dev' });
    console.log('Quick track:', tracked);
    const stats = await getAnalyticsStats();
    console.log('Analytics:', stats);

    // Delete
    const del = await deleteApplication(id);
    console.log('Deleted:', del);
  } catch (err) {
    console.error('Async demo error:', err && err.message ? err.message : err);
    if (err && err.data) console.error('Error data:', err.data);
  }
}

// Promise-based usage example (no async/await)
export function runPromiseDemo() {
  createApplication({ company_name: 'Promise Inc', job_title: 'SWE I' })
    .then((created) => {
      console.log('Created:', created);
      const id = (created && created.data && created.data.id) || created.id;
      return getApplication(id).then((fetched) => ({ id, fetched }));
    })
    .then(({ id }) => updateApplicationStatus(id, 'reviewing').then(() => id))
    .then((id) => deleteApplication(id))
    .then((res) => console.log('Cleanup result:', res))
    .catch((err) => {
      console.error('Promise demo error:', err && err.message ? err.message : err);
      if (err && err.data) console.error('Error data:', err.data);
    });
}

// If executed directly in Node with experimental ESM or bundlers, you can run demos:
if (typeof window === 'undefined') {
  // Attempt to detect direct execution
  const isDirect = process.argv && process.argv[1] && process.argv[1].includes('javascript_client_example');
  if (isDirect) {
    runAsyncDemo().then(() => runPromiseDemo());
  }
}

