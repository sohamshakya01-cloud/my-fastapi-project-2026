
import json
import os
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

FILE_PATH = "tasks.json"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    status: Literal["pending", "in_progress", "completed"] = "pending"


class Task(TaskCreate):
    id: int
    
def load_tasks():
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks):
    with open(FILE_PATH, "w") as file:
        json.dump(tasks, file, indent=4)


@app.get("/")
def home():
    return {"message": "Welcome to Task Management API"}

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):

    tasks = load_tasks()

    new_id = max(
        (item["id"] for item in tasks),
        default=0
    ) + 1

    new_task = Task(
        id=new_id,
        **task.model_dump()
    )

    tasks.append(new_task.model_dump())

    save_tasks(tasks)

    return new_task


@app.get("/tasks", response_model=list[Task])
def get_tasks(
    status: Optional[Literal["pending", "in_progress", "completed"]] = None,
    priority: Optional[Literal["low", "medium", "high"]] = None
):

    tasks = load_tasks()

    if status:
        tasks = [
            task for task in tasks
            if task["status"] == status
        ]

    if priority:
        tasks = [
            task for task in tasks
            if task["priority"] == priority
        ]

    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):

    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskCreate):

    tasks = load_tasks()

    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            updated_data = updated_task.model_dump()
            updated_data["id"] = task_id

            tasks[index] = updated_data

            save_tasks(tasks)

            return tasks[index]

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    tasks = load_tasks()

    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            deleted_task = tasks.pop(index)

            save_tasks(tasks)

            return {
                "message": "Task deleted successfully",
                "deleted_task": deleted_task
            }

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )
