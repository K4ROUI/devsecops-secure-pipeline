"""FastAPI Task API used to demonstrate a secure CI/CD pipeline."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response, status

from app.database import get_connection, initialize_database, row_to_dict
from app.schemas import HealthResponse, TaskCreate, TaskResponse, TaskUpdate

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/tasks.db"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database(DB_PATH)
    yield


app = FastAPI(
    title="Secure DevSecOps Task API",
    description="A small API for demonstrating automated testing and security gates.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    with get_connection(DB_PATH) as connection:
        rows = connection.execute(
            "SELECT id, title, description, completed, created_at "
            "FROM tasks ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [row_to_dict(row) for row in rows]


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(task: TaskCreate) -> dict:
    with get_connection(DB_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
            (task.title, task.description, int(task.completed)),
        )
        row = connection.execute(
            "SELECT id, title, description, completed, created_at FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return row_to_dict(row)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: int) -> dict:
    with get_connection(DB_PATH) as connection:
        row = connection.execute(
            "SELECT id, title, description, completed, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_dict(row)


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: int, task: TaskUpdate) -> dict:
    updates = task.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="At least one field is required")
    if any(value is None for value in updates.values()):
        raise HTTPException(status_code=422, detail="Updated fields cannot be null")

    with get_connection(DB_PATH) as connection:
        cursor = connection.execute(
            "UPDATE tasks SET title = COALESCE(?, title), "
            "description = COALESCE(?, description), "
            "completed = COALESCE(?, completed) WHERE id = ?",
            (updates.get("title"), updates.get("description"), updates.get("completed"), task_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        row = connection.execute(
            "SELECT id, title, description, completed, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return row_to_dict(row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int) -> Response:
    with get_connection(DB_PATH) as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
