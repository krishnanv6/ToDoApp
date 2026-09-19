import { useEffect, useState } from 'react'
import { getMe } from './api'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import TodoPage from './components/TodoPage'

function AppContent() {
  const { isAuthenticated, logout } = useAuth()
  const [authPage, setAuthPage] = useState('login') // 'login' | 'register'

  // Legacy cookie-session user (kept for backward compatibility)
  const [sessionUser, setSessionUser] = useState(undefined) // undefined = checking

  useEffect(() => {
    if (isAuthenticated) {
      setSessionUser(null) // JWT auth takes priority; skip cookie check
      return
    }
    getMe()
      .then(setSessionUser)
      .catch(() => setSessionUser(null))
  }, [isAuthenticated])

  // Still doing the initial cookie-session check and not JWT-authenticated
  if (!isAuthenticated && sessionUser === undefined) return null

  // JWT-authenticated
  if (isAuthenticated) {
    return (
      <TodoPage
        user={{ username: 'User' }}
        onLogout={logout}
      />
    )
  }

  // Legacy cookie-session authenticated
  if (sessionUser) {
    return <TodoPage user={sessionUser} onLogout={() => setSessionUser(null)} />
  }

  // Not authenticated — show login or register
  if (authPage === 'register') {
    return (
      <Register onNavigateLogin={() => setAuthPage('login')} />
    )
  }

  return (
    <Login onNavigateRegister={() => setAuthPage('register')} />
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
