FROM python:3.12-slim

WORKDIR /backend

# file from HOST to CONTAINER
COPY requirements.txt . 

RUN pip install -r requirements.txt

# src backend/ -> dst /backend
COPY . . 

# app (subor app.py) : app (objekt app=FastAPI())
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
