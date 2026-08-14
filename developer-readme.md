# Developer Guide: FastAPI + React TODO Sample

A small but complete web application used as a DevCapsule sample: a FastAPI
backend, a React single-page frontend, and PostgreSQL for persistence. PyCharm
is the interactive surface and Claude Code is available inside the environment.

This guide assumes you are developing **inside a DevCapsule environment**. The
last section covers running it without DevCapsule.

## What The Project Declares

`.devcapsule/devcapsule.toml` declares what the project needs, and
`.devcapsule/devcapsule.linux-amd64.lock` pins exactly what gets installed:

| Declared | Why |
|---|---|
| `python-ide` (PyCharm) | The interactive surface for this project. |
| `claude-code-agent` | Claude Code, available in the environment terminal. |
| `python`, `node`, `docker-cli` | Backend, frontend toolchain, and the database. |
| `host.docker.mode = host-socket` (recommended) | DevCapsule does not model service dependencies yet, so the PostgreSQL container is started with the Docker CLI. |
| `host.network.mode = host` (recommended) | Lets the backend reach PostgreSQL and lets a host browser open the dev servers without per-port plumbing. |

Both host recommendations are *recommendations*, not automatic grants. You
authorize them explicitly, per checkout, and can inspect the result first.

## First Run

### 1. Authorize and resolve the checkout

From the project root, review what the project asks for:

```bash
devcapsule project config list
```

Authorize the pinned base image, then the recommended host access. Nothing is
granted until you do this:

```bash
devcapsule project config authorize --all-recommended
devcapsule project config resolve
```

`--all-recommended` previews every recommendation and applies them only after
you confirm. To grant them individually instead:

```bash
devcapsule project config authorize docker-daemon host-socket
devcapsule project config authorize network host
devcapsule project config authorize claude-code-download true
```

### 2. Launch the environment

```bash
devcapsule project run
```

PyCharm opens with this project mounted at `/workspace/fastapi-webbapp`. Run the
remaining steps in a terminal **inside** that environment.

### 3. Start PostgreSQL

```bash
docker compose up -d db
docker compose ps
```

Wait for the `db` service to report healthy. The database listens on
`localhost:5432` with user `todo`, password `todo`, database `todo`. Data
survives restarts in the `todo-db-data` volume.

If port 5432 is already taken on your host — another PostgreSQL is a common
cause — choose a different published port and point the backend at it:

```bash
TODO_DB_PORT=55432 docker compose up -d db
export DATABASE_URL="postgresql+psycopg://todo:todo@localhost:55432/todo"
```

### 4. Install dependencies

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.txt
(cd frontend && npm install)
```

In PyCharm, point the project interpreter at `.venv/bin/python` so inspections
and the debugger resolve imports.

### 5. Run the backend

```bash
cd backend
../.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

The API is on `http://localhost:8000`, with interactive documentation at
`http://localhost:8000/docs`. Tables are created at startup, so a clean
database needs no migration step.

### 6. Run the frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to the
backend, so the browser stays on one origin and no CORS configuration is
needed during development.

## Everyday Tasks

Run the backend tests — these use a temporary SQLite database, so they pass
without starting PostgreSQL:

```bash
cd backend && ../.venv/bin/python -m pytest
```

Build the production frontend bundle:

```bash
cd frontend && npm run build
```

Inspect the database:

```bash
docker compose exec db psql -U todo -d todo -c '\dt'
```

`psql` is not installed in the DevCapsule base image, so run it through the
database container as above rather than directly.

Stop the database, keeping its data:

```bash
docker compose down
```

Add `-v` to discard the data volume and start from an empty database.

## Using Claude Code

Claude Code is materialized into the environment at `/opt/claude/bin/claude`
and is on `PATH`. From a terminal inside the environment:

```bash
claude
```

It is acquired during materialization only after you authorize
`claude-code-download`, under Anthropic's commercial terms. It is never
redistributed inside the public DevCapsule base image.

## Layout

```
.devcapsule/         project declaration and platform lock
backend/
  app/
    main.py          FastAPI application and routes
    models.py        SQLAlchemy Todo model
    schemas.py       request/response bodies
    database.py      engine, session factory, request dependency
    config.py        environment-driven settings
  tests/             API tests against temporary SQLite
frontend/
  src/
    App.jsx          TODO list UI
    api.js           fetch wrapper over /api
  vite.config.js     dev server and /api proxy
docker-compose.yml   development PostgreSQL
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://todo:todo@localhost:5432/todo` | SQLAlchemy URL used by the backend. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins allowed to call the API directly. |
| `BACKEND_URL` | `http://localhost:8000` | Where the Vite dev server proxies `/api`. |
| `TODO_DB_PORT` | `5432` | Host port the development database publishes. |

## Without DevCapsule

The project is ordinary Python and Node, so it also runs on a normal machine
with Python 3.12+, Node 20+, and Docker. Follow steps 3 through 6 above and
skip the DevCapsule-specific steps. The `.devcapsule/` directory is simply
ignored.

## Troubleshooting

**The backend cannot connect to the database.** Confirm the container is
healthy with `docker compose ps`. If the environment was launched without host
networking, `localhost:5432` inside the environment is not the database; either
authorize `network host` and relaunch, or point `DATABASE_URL` at the address
the container is actually reachable on.

**The browser cannot open `localhost:5173`.** The dev server already binds all
interfaces. Without host networking you also need the port published from the
environment.

**`docker compose` reports permission denied.** The checkout has not authorized
`docker-daemon host-socket`, or the environment was launched before that
authorization was resolved. Re-run the authorize and resolve steps, then
relaunch.
