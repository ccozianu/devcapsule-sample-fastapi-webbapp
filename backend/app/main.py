"""FastAPI application exposing a small TODO API backed by PostgreSQL."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_session
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # A real service would use Alembic migrations. Creating the tables at
    # startup keeps this sample runnable from a clean database in one step.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="DevCapsule Sample TODO API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/todos", response_model=list[TodoRead])
def list_todos(session: Session = Depends(get_session)) -> list[Todo]:
    return list(session.scalars(select(Todo).order_by(Todo.created_at.desc())))


@app.post("/api/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, session: Session = Depends(get_session)) -> Todo:
    todo = Todo(title=payload.title)
    session.add(todo)
    session.commit()
    return todo


@app.patch("/api/todos/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    session: Session = Depends(get_session),
) -> Todo:
    todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    if payload.title is not None:
        todo.title = payload.title
    if payload.done is not None:
        todo.done = payload.done
    session.commit()
    return todo


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: Session = Depends(get_session)) -> None:
    todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    session.delete(todo)
    session.commit()
