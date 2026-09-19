const BASE_URL = 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

function authHeaders(token) {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
}

export function signup(username, password) {
  return request('/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

export function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

export function getTodos(token) {
  return request('/todos', { headers: authHeaders(token) })
}

export function createTodo(token, { title, priority, due_date }) {
  return request('/todos', {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ title, priority, due_date: due_date || null }),
  })
}

export function updateTodo(token, id, patch) {
  return request(`/todos/${id}`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify(patch),
  })
}

export function deleteTodo(token, id) {
  return request(`/todos/${id}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
}
