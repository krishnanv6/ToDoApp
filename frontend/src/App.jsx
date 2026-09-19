import { useState } from 'react'
import AuthPage from './components/AuthPage'
import TodoPage from './components/TodoPage'

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('todo_token') || null)
  const [user, setUser] = useState(() => localStorage.getItem('todo_user') || null)

  function handleLogin(newToken, username) {
    localStorage.setItem('todo_token', newToken)
    localStorage.setItem('todo_user', username)
    setToken(newToken)
    setUser(username)
  }

  function handleLogout() {
    localStorage.removeItem('todo_token')
    localStorage.removeItem('todo_user')
    setToken(null)
    setUser(null)
  }

  if (!token) {
    return <AuthPage onLogin={handleLogin} />
  }

  return <TodoPage token={token} user={user} onLogout={handleLogout} />
}
