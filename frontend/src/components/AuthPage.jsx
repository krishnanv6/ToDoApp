import { useState } from 'react'
import { login, signup } from '../api'

export default function AuthPage({ onLogin }) {
  const [tab, setTab] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [loading, setLoading] = useState(false)

  function switchTab(t) {
    setTab(t); setError(''); setSuccessMsg(''); setUsername(''); setPassword('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(''); setSuccessMsg(''); setLoading(true)
    try {
      if (tab === 'login') {
        const data = await login(username, password)
        onLogin(data.access_token, username)
      } else {
        await signup(username, password)
        setSuccessMsg('Account created! You can now log in.')
        switchTab('login')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 11 12 14 22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>
          <h1>MyToDo App</h1>
          <p>Organize your day, effortlessly.</p>
        </div>

        <div className="auth-tabs">
          <button className={`tab-btn${tab === 'login' ? ' active' : ''}`} onClick={() => switchTab('login')}>Log In</button>
          <button className={`tab-btn${tab === 'signup' ? ' active' : ''}`} onClick={() => switchTab('signup')}>Sign Up</button>
        </div>

        {successMsg && <p className="success-msg">{successMsg}</p>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-field">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="your_username"
              required
              autoComplete="username"
            />
          </div>
          <div className="form-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
            />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '0.25rem' }}>
            {loading ? 'Please wait…' : tab === 'login' ? 'Log In' : 'Create Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
