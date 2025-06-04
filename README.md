# MCP-Mem0: Enhanced Memory System с Гарантированной Точностью

<p align="center">
  <img src="public/Mem0AndMCP.png" alt="Mem0 and MCP Integration" width="600">
</p>

Продвинутая реализация [Model Context Protocol (MCP)](https://modelcontextprotocol.io) сервера с интеграцией [Mem0](https://mem0.ai) для предоставления AI агентам **гарантированно точной и актуальной памяти**.

**Основной принцип: Неточный контекст хуже отсутствия контекста.**

## 🚀 Что Нового в Enhanced Memory System

### ✅ Система Версионирования и Конфликт-Детекции
- Автоматическое обнаружение противоречивой информации
- Версионирование записей с timestamp и audit trail
- Система разрешения конфликтов с manual approval

### ✅ Гарантии Качества Контекста  
- Confidence scoring (1-10) для каждой записи
- Автоматическая фильтрация устаревшей информации
- Валидация актуальности на основе времени и категории

### ✅ Проектное Управление Памятью
- Изоляция памяти по проектам
- Milestone tracking для ключевых решений
- Evolution tracking для понимания прогресса

## Возможности

Система предоставляет **11 инструментов для управления памятью**:

### 🔧 Основные Инструменты Точности
1. **`save_verified_memory`** - Сохранение с автоматическим conflict detection
2. **`get_accurate_context`** - Поиск только проверенной информации  
3. **`validate_project_context`** - Аудит качества памяти проекта
4. **`resolve_context_conflict`** - Разрешение противоречий между записями
5. **`audit_memory_quality`** - Комплексный анализ качества всей базы

### 📊 Проектные Инструменты
6. **`save_project_milestone`** - Ключевые моменты и решения
7. **`get_current_project_state`** - Актуальное состояние проекта
8. **`track_project_evolution`** - История развития понимания

### 📜 Базовые Инструменты (совместимость)
9. **`save_memory`** - Стандартное сохранение в память
10. **`get_all_memories`** - Получение всех записей
11. **`search_memories`** - Семантический поиск

## Быстрый Старт

### Предварительные Требования

- Python 3.12+
- Supabase или PostgreSQL база данных (для векторного хранения)
- API ключи для LLM provider (OpenAI, OpenRouter, или Ollama)
- Docker (рекомендуется)

### Установка

#### Используя uv

```bash
# Установить uv
pip install uv

# Клонировать репозиторий
git clone https://github.com/yourusername/mcp-mem0-enhanced.git
cd mcp-mem0-enhanced

# Установить зависимости
uv pip install -e .

# Настроить окружение
cp .env.example .env
# Отредактировать .env файл с вашими настройками
```

#### Используя Docker (Рекомендуется)

```bash
docker build -t mcp/mem0-enhanced --build-arg PORT=8050 .
```

## Конфигурация

Настройте следующие переменные в `.env` файле:

| Переменная | Описание | Пример |
|------------|----------|---------|
| `TRANSPORT` | Протокол (sse или stdio) | `sse` |
| `HOST` | Хост для SSE | `0.0.0.0` |
| `PORT` | Порт для SSE | `8050` |
| `LLM_PROVIDER` | LLM провайдер | `openai` |
| `LLM_API_KEY` | API ключ | `sk-...` |
| `LLM_CHOICE` | Модель LLM | `gpt-4o-mini` |
| `EMBEDDING_MODEL_CHOICE` | Модель embeddings | `text-embedding-3-small` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |

## Использование Enhanced Memory System

### Пример 1: Сохранение Проверенной Информации

```python
# Вместо обычного save_memory используйте save_verified_memory
await save_verified_memory(
    content="Project uses FastAPI with PostgreSQL database and Redis cache",
    project_id="web_backend",
    category="architecture", 
    confidence_level=9,
    source="code_analysis",
    expires_in_days=180,
    tags="fastapi,postgresql,redis,backend"
)
```

### Пример 2: Получение Точного Контекста

```python
# Получить только проверенную информацию с high confidence
result = await get_accurate_context(
    query="database architecture",
    project_id="web_backend",
    min_confidence=7,
    limit=5
)
```

### Пример 3: Обработка Конфликтов

```python
# Система автоматически обнаружит конфликт
await save_verified_memory(
    content="Project uses MongoDB database",  # Конфликт с PostgreSQL выше
    project_id="web_backend",
    category="architecture",
    confidence_level=8
)
# ⚠️ Вернет предупреждение о конфликте

# Разрешить конфликт
await resolve_context_conflict(
    conflicting_memory_ids="mem_001,mem_002",
    correct_content="Project uses PostgreSQL as primary database, MongoDB for analytics",
    resolution_reason="Architecture review confirmed PostgreSQL for main data, MongoDB for logs"
)
```

### Пример 4: Проектные Milestone

```python
# Сохранить важное архитектурное решение
await save_project_milestone(
    project_id="web_backend",
    milestone_type="architecture_decision",
    content="Decided to implement microservices architecture with API Gateway",
    impact_level=9,
    tags="microservices,api-gateway,architecture"
)

# Получить текущее состояние проекта
current_state = await get_current_project_state("web_backend")
```

### Пример 5: Аудит Качества

```python
# Проверить качество памяти проекта
validation_report = await validate_project_context("web_backend")

# Полный аудит всей базы памяти
quality_audit = await audit_memory_quality()
```

## Запуск Сервера

### SSE Transport

```bash
# Установить TRANSPORT=sse в .env, затем:
uv run src/main.py

# Или с Docker:
docker run --env-file .env -p 8050:8050 mcp/mem0-enhanced
```

### Stdio Transport

Клиент MCP сам запустит сервер при подключении.

## Интеграция с MCP Клиентами

### SSE Конфигурация

```json
{
  "mcpServers": {
    "mem0-enhanced": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

### Stdio Конфигурация

```json
{
  "mcpServers": {
    "mem0-enhanced": {
      "command": "python",
      "args": ["./src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_API_KEY": "YOUR-API-KEY",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

## Тестирование

### Запуск Тестов

```bash
# Установить pytest
uv pip install pytest pytest-asyncio

# Запустить все тесты
pytest tests/ -v

# Запустить только тесты Enhanced Memory
pytest tests/test_enhanced_memory.py -v
```

### Тестовые Сценарии

Система включает comprehensive тесты для:
- ✅ Обнаружения конфликтов
- ✅ Версионирования записей  
- ✅ Валидации качества
- ✅ Фильтрации по точности
- ✅ Проектного контекста

## Миграция с Оригинального mcp-mem0

### Обратная Совместимость

Существующие записи продолжают работать. Новые возможности:

```python
# Старый способ (по-прежнему работает)
await save_memory("Some information")

# Новый способ с гарантиями точности
await save_verified_memory(
    content="Some information",
    project_id="my_project", 
    category="architecture",
    confidence_level=8
)
```

## Продвинутые Возможности

### Confidence Scoring

- **1-3**: Низкая уверенность, требует проверки
- **4-6**: Средняя уверенность, может потребовать валидации
- **7-8**: Высокая уверенность, надежная информация  
- **9-10**: Максимальная уверенность, проверенные факты

### Категории Информации

- **`architecture`** - архитектурные решения и компоненты
- **`problem`** - выявленные проблемы и ограничения
- **`solution`** - реализованные решения
- **`status`** - текущий статус и прогресс
- **`decision`** - принятые решения и их обоснования

### Источники Информации

- **`user_input`** - информация от пользователя
- **`code_analysis`** - анализ кодовой базы
- **`documentation`** - из документации проекта
- **`project_milestone`** - проектные вехи
- **`conflict_resolution`** - результат разрешения конфликтов

## Best Practices

### Для AI Агентов

1. **Используйте get_accurate_context** для production запросов
2. **Указывайте realistic confidence_level** на основе источника
3. **Группируйте по project_id** для изоляции проектов
4. **Регулярно валидируйте** качество контекста

### Для Разработчиков

1. **Мониторьте health_score** через audit_memory_quality
2. **Разрешайте конфликты быстро** для поддержания качества
3. **Используйте appropriate expiration** для time-sensitive данных
4. **Документируйте sources** для audit trail

## Архитектурные Особенности

### Производительность

- PostgreSQL с векторными индексами для fast search
- Connection pooling для concurrent access
- Асинхронная валидация для background quality checks
- Caching для frequently accessed context

### Масштабирование

- Horizontal scaling через Supabase
- Project-based partitioning для large datasets  
- Batch operations для bulk updates
- Streaming responses для large results

## Документация

- 📖 [Детальная документация](docs/ENHANCED_MEMORY_SYSTEM.md)
- 🧪 [Тестовые примеры](tests/test_enhanced_memory.py)
- 🔧 [API Reference](docs/API_REFERENCE.md)

## Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

## Поддержка

Создайте issue в репозитории для:
- 🐛 Баг репорты
- 💡 Feature requests  
- ❓ Вопросы по использованию
- 📝 Улучшения документации

---

**Enhanced Memory System гарантирует, что ваши AI агенты получают только точную, актуальную и проверенную информацию для принятия решений.**
