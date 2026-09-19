import { useState } from 'react'
import { deleteTodo, updateTodo } from '../api'
import ConfirmModal from './ConfirmModal'

const PRIORITY_COLORS = { High: '#ef4444', Medium: '#f59e0b', Low: '#22c55e' }

function TrashIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
      <path d="M10 11v6M14 11v6" />
      <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
    </svg>
  )
}

function CalIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  )
}

export default function TodoItem({ todo, onUpdate, onDelete, selected, onSelect }) {
  const [loading, setLoading] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  async function handleToggle() {
    setLoading(true)
    try {
      const updated = await updateTodo(todo.id, { completed: !todo.completed })
      onUpdate(updated)
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    setLoading(true)
    try {
      await deleteTodo(todo.id)
      onDelete(todo.id)
    } finally {
      setLoading(false)
      setShowConfirm(false)
    }
  }

  const priorityColor = PRIORITY_COLORS[todo.priority] || '#6366f1'
  const isOverdue = todo.due_date && !todo.completed && new Date(todo.due_date) < new Date()

  return (
    <>
      <div
        className={`todo-card${todo.completed ? ' completed' : ''}${selected ? ' selected' : ''}`}
        style={{ '--priority-color': priorityColor }}
      >
        <div className="select-checkbox-wrap">
          <input
            type="checkbox"
            className="select-cb"
            checked={selected}
            onChange={() => onSelect(todo.id)}
            title="Select for bulk action"
          />
        </div>

        <div className="complete-cb-wrap">
          <input
            type="checkbox"
            className="complete-cb"
            checked={todo.completed}
            onChange={handleToggle}
            disabled={loading}
            title={todo.completed ? 'Mark incomplete' : 'Mark complete'}
          />
        </div>

        <div className="todo-body">
          <span className={`todo-title${todo.completed ? ' struck' : ''}`}>{todo.title}</span>
          <div className="todo-meta">
            <span className="priority-badge" style={{ backgroundColor: priorityColor }}>
              {todo.priority}
            </span>
            {todo.due_date && (
              <span className={`due-date${isOverdue ? ' overdue' : ''}`}>
                <CalIcon />
                {todo.due_date}
                {isOverdue && ' · Overdue'}
              </span>
            )}
          </div>
        </div>

        <button
          className="btn-delete"
          onClick={() => setShowConfirm(true)}
          disabled={loading}
          title="Delete todo"
          aria-label="Delete todo"
        >
          <TrashIcon />
        </button>
      </div>

      {showConfirm && (
        <ConfirmModal
          title="Delete todo?"
          message={`<strong>${todo.title}</strong> will be permanently deleted. This cannot be undone.`}
          onConfirm={handleDelete}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  )
}
