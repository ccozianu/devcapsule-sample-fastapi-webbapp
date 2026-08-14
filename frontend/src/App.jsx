import { useCallback, useEffect, useState } from "react";
import { createTodo, deleteTodo, listTodos, setTodoDone } from "./api.js";

export default function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setTodos(await listTodos());
      setError(null);
    } catch (cause) {
      setError(cause.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function onAdd(event) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    try {
      await createTodo(trimmed);
      setTitle("");
      await refresh();
    } catch (cause) {
      setError(cause.message);
    }
  }

  async function onToggle(todo) {
    try {
      await setTodoDone(todo.id, !todo.done);
      await refresh();
    } catch (cause) {
      setError(cause.message);
    }
  }

  async function onDelete(todo) {
    try {
      await deleteTodo(todo.id);
      await refresh();
    } catch (cause) {
      setError(cause.message);
    }
  }

  return (
    <main className="app">
      <h1>TODO</h1>
      <p className="subtitle">DevCapsule sample: FastAPI + React + PostgreSQL</p>

      <form className="add" onSubmit={onAdd}>
        <input
          aria-label="New task"
          placeholder="What needs doing?"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p className="muted">Loading…</p>}
      {!loading && todos.length === 0 && <p className="muted">Nothing yet.</p>}

      <ul className="list">
        {todos.map((todo) => (
          <li key={todo.id} className={todo.done ? "done" : ""}>
            <label>
              <input
                type="checkbox"
                checked={todo.done}
                onChange={() => onToggle(todo)}
              />
              <span>{todo.title}</span>
            </label>
            <button type="button" onClick={() => onDelete(todo)} aria-label="Delete">
              ×
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
