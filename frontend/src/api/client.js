const storageKey = "plate-scan-session"

export function readSession() {
  const raw = sessionStorage.getItem(storageKey)
  if (!raw) {
    return null
  }
  return JSON.parse(raw)
}

export function saveSession(session) {
  sessionStorage.setItem(storageKey, JSON.stringify(session))
}

export function clearSession() {
  sessionStorage.removeItem(storageKey)
}

async function send(path, options = {}) {
  const session = readSession()
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) }
  if (session?.access_token) {
    headers.Authorization = `Bearer ${session.access_token}`
  }
  const response = await fetch(path, { ...options, headers })
  const text = await response.text()
  const body = text ? JSON.parse(text) : null
  if (response.status === 401 && session?.access_token) {
    clearSession()
    window.location.assign("/")
  }
  if (!response.ok) {
    const detail = body?.detail
    throw new Error(typeof detail === "string" ? detail : "Request failed")
  }
  return body
}

export function login(username, password) {
  return send("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  })
}

export function listCases(status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : ""
  return send(`/api/v1/cases${query}`)
}

export function getTrail(caseId) {
  return send(`/api/v1/cases/${caseId}/scans`)
}

export function claimCase(caseId) {
  return send(`/api/v1/cases/${caseId}/claim`, { method: "POST" })
}
