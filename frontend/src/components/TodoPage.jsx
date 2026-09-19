import { useEffect, useState } from 'react'
import { deleteTodo, getTodos, updateTodo } from '../api'
import AddTodoForm from './AddTodoForm'
import TodoList from './TodoList'
import ConfirmModal from './ConfirmModal'

function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
      <path d="M10 11v6M14 11v6" />
      <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
    </svg>
  )
}

export default function TodoPage({ token, user, onLogout }) {
  const [todos, setTodos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [showBulkConfirm, setShowBulkConfirm] = useState(false)
  const [bulkDeleting, setBulkDeleting] = useState(false)
  const [bulkCompleting, setBulkCompleting] = useState(false)
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem('dark_mode') === 'true'
  )

  useEffect(() => {
    document.body.setAttribute('data-theme', darkMode ? 'dark' : 'light')
    localStorage.setItem('dark_mode', darkMode)
  }, [darkMode])

  useEffect(() => {
    getTodos(token)
      .then(setTodos)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [token])

  function handleAdd(todo) { setTodos((prev) => [todo, ...prev]) }

  function handleUpdate(updated) {
    setTodos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
  }

  function handleDelete(id) {
    setTodos((prev) => prev.filter((t) => t.id !== id))
    setSelectedIds((prev) => { const s = new Set(prev); s.delete(id); return s })
  }

  function handleSelect(id) {
    setSelectedIds((prev) => {
      const s = new Set(prev)
      s.has(id) ? s.delete(id) : s.add(id)
      return s
    })
  }

  function handleSelectAll(ids) {
    setSelectedIds(new Set(ids))
  }

  async function handleBulkComplete() {
    setBulkCompleting(true)
    const ids = [...selectedIds]
    const results = await Promise.allSettled(
      ids.map((id) => updateTodo(token, id, { completed: true }))
    )
    results.forEach((r) => {
      if (r.status === 'fulfilled') handleUpdate(r.value)
    })
    setSelectedIds(new Set())
    setBulkCompleting(false)
  }

  async function handleBulkDelete() {
    setBulkDeleting(true)
    const ids = [...selectedIds]
    await Promise.allSettled(ids.map((id) => deleteTodo(token, id)))
    setTodos((prev) => prev.filter((t) => !selectedIds.has(t.id)))
    setSelectedIds(new Set())
    setBulkDeleting(false)
    setShowBulkConfirm(false)
  }

  const selectedCount = selectedIds.size

  return (
    <div className="page-container">
      <header className="app-header">
        <div className="app-header-brand">
          <div className="brand-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 11 12 14 22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>
          <span className="app-title">MyToDo App</span>
        </div>

        <div className="header-right">
          <div className="username-chip">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span>{user}</span>
          </div>
          <button className="btn-icon" onClick={() => setDarkMode((d) => !d)} title="Toggle dark mode">
            {darkMode ? <SunIcon /> : <MoonIcon />}
          </button>
          <button className="btn-secondary" onClick={onLogout}>Log out</button>
        </div>
      </header>

      <main className="main-content">
        <AddTodoForm token={token} onAdd={handleAdd} />

        {loading && <p className="loading">Loading…</p>}
        {error && <p className="error-msg">{error}</p>}

        {selectedCount > 0 && (
          <div className="bulk-bar">
            <span className="bulk-count">{selectedCount} selected</span>
            <button
              className="btn-ghost"
              onClick={() => setSelectedIds(new Set())}
            >
              Clear
            </button>
            <button
              className="btn-complete"
              onClick={handleBulkComplete}
              disabled={bulkCompleting || bulkDeleting}
            >
              Complete {selectedCount}
            </button>
            <button
              className="btn-danger"
              onClick={() => setShowBulkConfirm(true)}
              disabled={bulkDeleting || bulkCompleting}
            >
              <TrashIcon />
              Delete {selectedCount}
            </button>
          </div>
        )}

        {!loading && (
          <TodoList
            todos={todos}
            token={token}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            selectedIds={selectedIds}
            onSelect={handleSelect}
            onSelectAll={handleSelectAll}
          />
        )}
      </main>

      {showBulkConfirm && (
        <ConfirmModal
          title={`Delete ${selectedCount} ${selectedCount === 1 ? 'todo' : 'todos'}?`}
          message={`You are about to permanently delete <strong>${selectedCount} ${selectedCount === 1 ? 'task' : 'tasks'}</strong>. This action cannot be undone.`}
          onConfirm={handleBulkDelete}
          onCancel={() => setShowBulkConfirm(false)}
        />
      )}
    </div>
  )
}
