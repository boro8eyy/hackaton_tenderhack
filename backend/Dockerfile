# syntax=docker/dockerfile:1.4
# Multi-stage build для оптимизации размера
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime AS base

WORKDIR /app

# Устанавливаем системные зависимости для hdbscan и psycopg2
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Скачиваем модель при сборке образа
ARG EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
ENV EMBEDDING_MODEL=${EMBEDDING_MODEL}
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL}')"

# Production stage
FROM base AS production

WORKDIR /app
COPY . .

# Не используем --reload в продакшене
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Development stage  
FROM base AS development

WORKDIR /app
COPY . .

# Используем --reload для разработки
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
