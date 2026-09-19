import { useEffect, useState } from 'react'
import { getMe } from './api'
import AuthPage from './components/AuthPage'
import TodoPage from './components/TodoPage'

export default function App() {
  const [user, setUser] = useState(undefined) // undefined = checking, null = not logged in

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  if (user === undefined) return null

  if (!user) return <AuthPage onLogin={setUser} />

  return <TodoPage user={user} onLogout={() => setUser(null)} />
}
