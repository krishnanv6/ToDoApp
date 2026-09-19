const BASE_URL = 'http://localhost:8000'
const TOKEN_KEY = 'auth_token'

function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    credentials: 'include',
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

async function authedRequest(path, options = {}) {
  const headers = {
    ...authHeaders(),
    ...(options.headers || {}),
  }
  return request(path, { ...options, headers })
}

function jsonHeaders() {
  return { 'Content-Type': 'application/json' }
}

// --- Cookie-session auth (legacy) ---

export function signup(username, password) {
  return request('/auth/signup', {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ username, password }),
  })
}

export function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ username, password }),
  })
}

export function logout() {
  return request('/auth/logout', { method: 'POST' })
}

export function getMe() {
  return request('/auth/me')
}

// --- JWT auth ---

export function loginWithToken(username, password) {
  return request('/auth/login', {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ username, password }),
  })
}

export function registerUser(username, password) {
  return request('/auth/register', {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ username, password }),
  })
}

// --- Todos (attach Bearer token when available) ---

export function getTodos() {
  return authedRequest('/todos')
}

export function createTodo({ title, priority, due_date }) {
  return authedRequest('/todos', {
    method: 'POST',
    headers: jsonHeaders(),
    body: JSON.stringify({ title, priority, due_date: due_date || null }),
  })
}

export function updateTodo(id, patch) {
  return authedRequest(`/todos/${id}`, {
    method: 'PATCH',
    headers: jsonHeaders(),
    body: JSON.stringify(patch),
  })
}

export function deleteTodo(id) {
  return authedRequest(`/todos/${id}`, { method: 'DELETE' })
}
