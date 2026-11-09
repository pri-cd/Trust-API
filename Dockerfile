# Dockerfile (basics only)
# Lightweight Python image + /app as base dir
# Get requirements.txt,
# Install dep,
# Get application,
# Expose port..
# Runnable command..
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]