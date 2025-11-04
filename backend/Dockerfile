FROM python:3.12-slim

WORKDIR /backend

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]



