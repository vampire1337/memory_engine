# 🏗️ ENTERPRISE MCP-MEM0 DOCKERFILE
# Multi-stage production build для максимальной производительности и безопасности
# Поддержка: FastAPI-MCP + Mem0 Graph Memory + Redis + Full monitoring

# =================== STAGE 1: BUILDER ===================
FROM python:3.11-slim as builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv для быстрой установки зависимостей
RUN pip install uv

# Рабочая директория для сборки
WORKDIR /build

# Копирование файлов зависимостей
COPY requirements.txt pyproject.toml ./

# Создание виртуального окружения и установка зависимостей
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка всех зависимостей в виртуальное окружение
RUN uv pip install -r requirements.txt

# =================== STAGE 2: RUNTIME ===================
FROM python:3.11-slim as runtime

# Метаданные образа
LABEL maintainer="Enterprise MCP-Mem0 Team"
LABEL version="2.0.0"
LABEL description="Production-ready MCP Server with 17 Enterprise Memory Tools"

# Установка только runtime зависимостей
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создание пользователя для безопасности (non-root)
RUN groupadd -r mcpmem0 && useradd -r -g mcpmem0 mcpmem0

# Рабочая директория
WORKDIR /app

# Копирование виртуального окружения из builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование исходного кода
COPY src/ ./src/
COPY *.md ./
COPY *.yml ./

# Создание необходимых директорий
RUN mkdir -p logs monitoring backups \
    && chown -R mcpmem0:mcpmem0 /app

# Переключение на non-root пользователя
USER mcpmem0

# Переменные окружения для production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000
ENV UVICORN_WORKERS=1
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Открываем порт
EXPOSE 8000

# Запуск сервера
CMD ["python", "-m", "uvicorn", "src.fastapi_mcp_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]

# =================== VOLUME MOUNTS ===================
# Логи
VOLUME ["/app/logs"]
# Мониторинг метрик
VOLUME ["/app/monitoring"]
# Backup данные
VOLUME ["/app/backups"] 