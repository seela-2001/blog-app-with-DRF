FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Optional: non-root user for better security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
