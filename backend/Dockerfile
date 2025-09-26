FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System packages required for scientific dependencies and WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg62-turbo \
    libpng-dev \
    shared-mime-info \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.py ./
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

RUN mkdir -p data/uploads data/exports

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
