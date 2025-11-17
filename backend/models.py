# backend/models.py

# Jasná separácia dátových modelov
# Môžeš ich reusovať v iných častiach aplikácie


from pydantic import BaseModel

from typing import Optional
from datetime import date


# POST request body model
class TaskCreate(BaseModel):
    task_name: str
    task_desc: Optional[str] = None
    accomplish_time: int


# GET request response model
class TaskResponse(BaseModel):
    id: int
    task_name: str
    task_desc: Optional[str] = None
    creation_date: date
    done: bool
    accomplish_time: int


# PUT request body model
class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    done: Optional[bool] = None
    accomplish_time: Optional[int] = None


