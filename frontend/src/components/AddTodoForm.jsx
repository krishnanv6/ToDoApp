import { useState } from 'react'
import { createTodo } from '../api'

export default function AddTodoForm({ token, onAdd }) {
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState('Medium')
  const [dueDate, setDueDate] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!title.trim()) { setError('Title is required'); return }
    setError(''); setLoading(true)
    try {
      const todo = await createTodo(token, { title: title.trim(), priority, due_date: dueDate || null })
      onAdd(todo)
      setTitle(''); setPriority('Medium'); setDueDate('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="add-form-card">
      <p className="add-form-title">New Task</p>
      <form onSubmit={handleSubmit} className="add-form">
        <input
          className="title-input"
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <select className="priority-select" value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="Low">🟢 Low</option>
          <option value="Medium">🟡 Medium</option>
          <option value="High">🔴 High</option>
        </select>
        <input
          className="date-input"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? '…' : '+ Add'}
        </button>
      </form>
      {error && <p className="error-msg" style={{ marginTop: '0.5rem' }}>{error}</p>}
    </div>
  )
}
