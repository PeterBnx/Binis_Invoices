FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

# Just install the python package first
RUN pip install playwright

# Use Playwright's own dependency manager to install system libs + browser
RUN playwright install-deps chromium
RUN playwright install chromium

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# 4. Copy project
COPY . .

EXPOSE 8000