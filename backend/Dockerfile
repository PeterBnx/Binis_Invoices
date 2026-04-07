FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

# Install dependencies from the backend folder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from backend/ to /app/
COPY . .

EXPOSE 8000