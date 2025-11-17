# backend/app.py
from fastapi import FastAPI, HTTPException
from typing import List
from models import TaskCreate, TaskUpdate, TaskResponse # validacia
from database import test_db_connection
from crud import (
    create_task_db,
    get_all_tasks_db,
    get_task_by_id_db,
    update_task_db,
    delete_task_db
)

app = FastAPI(
    title="Task Manager API",
    description="Simple task management API with PostgreSQL",
    version="1.0.0"
)

# ============= HEALTH ENDPOINTS =============

@app.get("/")
def read_root():
    """Root endpoint - základný health check"""
    return {"status": "healthy", "message": "Task Manager API is running"}

@app.get("/health")
def health_check():
    """Health check s DB testom"""
    db_status = test_db_connection()
    
    if db_status:
        return {"status": "ok", "database": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Database connection failed")

# ============= TASK CRUD ENDPOINTS =============

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate):
    """Vytvorí nový task"""
    try:
        result = create_task_db(task) # ← Dostane DICT z crud.py
        # result = {'id': 5, 'task_name': 'Learn Docker', ...}

        # FastAPI automaticky konvertuje na JSON pre HTTP response

        # vytvoríš novú inštanciu (nový objekt) typu TaskCreate.
        return TaskResponse(**result)  # Pydantic object ← Vytvorí TaskResponse z toho dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks():
    """Vráti všetky tasky"""
    try:
        tasks = get_all_tasks_db()
        return [TaskResponse(**task) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Vráti konkrétny task podľa ID"""
    try:
        task = get_task_by_id_db(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        return TaskResponse(**task)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch task: {str(e)}")


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    """Updatne existujúci task"""
    try:
        # Check if any fields to update
        if not task.model_dump(exclude_unset=True):
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = update_task_db(task_id, task)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        return TaskResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Zmaže task"""
    try:
        deleted_task = delete_task_db(task_id)
        
        if not deleted_task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        return {"message": "Task deleted successfully", "id": deleted_task['id']}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")