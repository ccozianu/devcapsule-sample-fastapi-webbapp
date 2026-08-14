// All backend calls go through the Vite dev-server proxy at /api, so the
// browser only ever talks to the origin that served the page.

async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${options.method ?? "GET"} /api${path} failed: ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

export const listTodos = () => request("/todos");

export const createTodo = (title) =>
  request("/todos", { method: "POST", body: JSON.stringify({ title }) });

export const setTodoDone = (id, done) =>
  request(`/todos/${id}`, { method: "PATCH", body: JSON.stringify({ done }) });

export const deleteTodo = (id) => request(`/todos/${id}`, { method: "DELETE" });
