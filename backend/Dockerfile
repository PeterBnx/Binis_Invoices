FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev libxslt-dev gcc python3-dev libpq-dev \
    libnss3 libnspr4 libgbm1 libasound2 libpangocairo-1.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxi6 libxrandr2 libxrender1 libxtst6 fonts-liberation fonts-unifont \
    libappindicator3-1 libcups2 libxss1 liblsan0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


RUN playwright install chromium

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:10000"]