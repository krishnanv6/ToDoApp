import TodoItem from './TodoItem'

export default function TodoList({ todos, onUpdate, onDelete, selectedIds, onSelect, onSelectAll }) {
  if (todos.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">✅</div>
        <p>You&apos;re all caught up!</p>
        <span>Add a new todo above to get started.</span>
      </div>
    )
  }

  const allSelected = todos.length > 0 && todos.every((t) => selectedIds.has(t.id))

  return (
    <div>
      <div className="list-header">
        <div className="list-header-left">
          <label className="select-all-label">
            <input
              type="checkbox"
              className="select-cb"
              style={{ opacity: 1 }}
              checked={allSelected}
              onChange={() => onSelectAll(allSelected ? [] : todos.map((t) => t.id))}
            />
            {allSelected ? 'Deselect all' : 'Select all'}
          </label>
        </div>
        <span className="list-count">{todos.length} {todos.length === 1 ? 'task' : 'tasks'}</span>
      </div>

      <div className="todo-list">
        {todos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onUpdate={onUpdate}
            onDelete={onDelete}
            selected={selectedIds.has(todo.id)}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  )
}
