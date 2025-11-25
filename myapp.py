"""
FastAPI-based microservice for managing tasks.

This service provides endpoints to:
- Create a new task
- Update task status by task ID
- Delete task by task ID
- List all tasks
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Initialize FastAPI app
app = FastAPI(
    title="Task Management Microservice",
    description="API for managing tasks with create, update, and delete operations",
    version="1.0.0"
)

# Enums for task status
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Pydantic models for request/response
class TaskCreate(BaseModel):
    """Model for creating a new task"""
    description: str
    status: TaskStatus = TaskStatus.PENDING
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Complete project documentation",
                "status": "pending"
            }
        }

class TaskUpdate(BaseModel):
    """Model for updating task status"""
    status: TaskStatus
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed"
            }
        }

class Task(BaseModel):
    """Model for task response"""
    id: int
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "description": "Complete project documentation",
                "status": "pending",
                "created_at": "2025-11-25T10:30:00",
                "updated_at": "2025-11-25T10:30:00"
            }
        }

# In-memory task storage
tasks_db: dict = {}
task_id_counter: int = 0

# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Task Management Microservice is running",
        "version": "1.0.0"
    }

# Create task endpoint
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task: TaskCreate):
    """
    Create a new task.
    
    - **description**: Task description (required)
    - **status**: Task status (optional, defaults to 'pending')
    
    Returns the created task with a unique ID.
    """
    global task_id_counter
    task_id_counter += 1
    
    now = datetime.now()
    new_task = Task(
        id=task_id_counter,
        description=task.description,
        status=task.status,
        created_at=now,
        updated_at=now
    )
    
    tasks_db[task_id_counter] = new_task
    return new_task

# Get all tasks endpoint
@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks():
    """Get all tasks from the system"""
    return list(tasks_db.values())

# Get task by ID endpoint
@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: int):
    """Get a specific task by its ID"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return tasks_db[task_id]

# Update task status endpoint
@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task_status(task_id: int, task_update: TaskUpdate):
    """
    Update the status of an existing task by its ID.
    
    - **task_id**: The ID of the task to update (path parameter)
    - **status**: New status for the task (request body)
    
    Returns the updated task.
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    existing_task = tasks_db[task_id]
    updated_task = Task(
        id=existing_task.id,
        description=existing_task.description,
        status=task_update.status,
        created_at=existing_task.created_at,
        updated_at=datetime.now()
    )
    
    tasks_db[task_id] = updated_task
    return updated_task

# Delete task endpoint
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(task_id: int):
    """
    Delete a task by its ID.
    
    - **task_id**: The ID of the task to delete (path parameter)
    
    Returns 204 No Content on successful deletion.
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    del tasks_db[task_id]
    return None

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
