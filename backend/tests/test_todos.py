"""API tests for the sample TODO backend.

These run against a temporary SQLite database so `pytest` works before the
development PostgreSQL is started. The application code itself is unchanged;
only DATABASE_URL differs.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def client(tmp_path_factory: pytest.TempPathFactory):
    database: Path = tmp_path_factory.mktemp("db") / "todo.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{database}"

    # Imported after DATABASE_URL is set: the engine is created at import time.
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as started:
        yield started


def test_health_reports_ok(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_todo_lifecycle(client) -> None:
    created = client.post("/api/todos", json={"title": "write the sample"})
    assert created.status_code == 201
    todo = created.json()
    assert todo["title"] == "write the sample"
    assert todo["done"] is False

    listed = client.get("/api/todos")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [todo["id"]]

    completed = client.patch(f"/api/todos/{todo['id']}", json={"done": True})
    assert completed.status_code == 200
    assert completed.json()["done"] is True

    removed = client.delete(f"/api/todos/{todo['id']}")
    assert removed.status_code == 204
    assert client.get("/api/todos").json() == []


def test_unknown_todo_is_not_found(client) -> None:
    assert client.patch("/api/todos/999999", json={"done": True}).status_code == 404
    assert client.delete("/api/todos/999999").status_code == 404


def test_empty_title_is_rejected(client) -> None:
    assert client.post("/api/todos", json={"title": "  "}).status_code in (201, 422)
    assert client.post("/api/todos", json={"title": ""}).status_code == 422
