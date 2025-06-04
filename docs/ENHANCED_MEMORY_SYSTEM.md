# Enhanced Memory System - Гарантированно Точный Контекст

## Обзор

Система Enhanced Memory построена на базе оригинального mcp-mem0 сервера и добавляет критически важные функции для обеспечения **актуального, правдивого и точного контекста** для AI агентов.

**Основной принцип**: Неточный контекст хуже отсутствия контекста.

## Ключевые Улучшения

### 1. Система Версионирования Памяти
- ✅ Каждая запись имеет версию и timestamp
- ✅ При обновлении создается новая версия, старая помечается как deprecated  
- ✅ Автоматическое обнаружение конфликтов при противоречивой информации
- ✅ Трекинг superseded_by связей между версиями

### 2. Система Валидации Контекста
- ✅ Проверка актуальности сохраненной информации
- ✅ Обнаружение устаревших данных на основе времени и категории
- ✅ Confidence scores (1-10) для оценки достоверности
- ✅ Обязательные поля: источник, уровень достоверности, дата актуальности

### 3. Контекстуальная Фильтрация
- ✅ Возврат только проверенной и актуальной информации
- ✅ Фильтрация по времени для быстро меняющихся данных
- ✅ Система приоритетов: свежая информация имеет приоритет

## Новые Инструменты

### Основные Инструменты Точности

#### 1. `save_verified_memory`
Расширенная версия save_memory с автоматическим обнаружением конфликтов.

```python
await save_verified_memory(
    content="Project uses PostgreSQL database",
    project_id="web_app", 
    category="architecture",
    confidence_level=9,
    source="code_analysis",
    expires_in_days=90,
    tags="database,postgres,architecture"
)
```

**Параметры:**
- `content` - информация для сохранения
- `project_id` - идентификатор проекта 
- `category` - тип информации (architecture/problem/solution/status/decision)
- `confidence_level` - уровень уверенности (1-10)
- `source` - источник (user_input/code_analysis/documentation)
- `expires_in_days` - срок актуальности в днях (опционально)
- `tags` - теги через запятую (опционально)

**Поведение при конфликтах:**
- Автоматически обнаруживает похожую информацию
- Помечает конфликтующие записи
- Требует ручного разрешения через resolve_context_conflict

#### 2. `get_accurate_context`
Замена search_memories с фокусом на точность.

```python
await get_accurate_context(
    query="database architecture",
    project_id="web_app",
    min_confidence=7,
    limit=5
)
```

**Фильтрация:**
- ❌ Исключает expired записи
- ❌ Исключает deprecated записи  
- ❌ Исключает conflicted записи
- ❌ Исключает записи с confidence < min_confidence
- ✅ Сортирует по confidence и актуальности

#### 3. `validate_project_context`
Проверяет всю информацию по проекту на актуальность.

```python
await validate_project_context("web_app")
```

**Анализирует:**
- Expired memories (просроченные)
- Conflicted memories (конфликтующие)
- Low confidence memories (низкая достоверность)
- Memories needing validation (требующие проверки)

**Возвращает:**
```json
{
  "project_id": "web_app",
  "total_memories": 15,
  "analysis": {
    "expired_memories": 2,
    "conflicted_memories": 1, 
    "low_confidence_memories": 3,
    "needs_validation": 4
  },
  "recommendations": [
    "⚠️ 1 memories have conflicts - use resolve_context_conflict",
    "🔍 3 memories have low confidence - verify accuracy"
  ]
}
```

#### 4. `resolve_context_conflict`
Разрешает конфликты между записями памяти.

```python
await resolve_context_conflict(
    conflicting_memory_ids="mem_001,mem_002",
    correct_content="Project uses PostgreSQL database exclusively",
    resolution_reason="PostgreSQL confirmed by latest architecture review"
)
```

**Процесс:**
1. Помечает конфликтующие записи как deprecated
2. Создает consolidated_memory с правильной информацией
3. Устанавливает высокий confidence_level (10)
4. Записывает reason для audit trail

#### 5. `audit_memory_quality`
Комплексный аудит качества всей базы памяти.

```python
await audit_memory_quality(project_id="web_app")  # или без project_id для всей базы
```

**Анализ:**
- Health Score (0-100) на основе ratio проблем
- Распределение по confidence levels
- Распределение по категориям  
- Анализ возраста записей
- Приоритизированные рекомендации

### Инструменты для Проектного Контекста

#### 6. `save_project_milestone`
Сохраняет ключевые моменты проекта с автоматическим версионированием.

```python
await save_project_milestone(
    project_id="web_app",
    milestone_type="architecture_decision",
    content="Decided to use microservices architecture",
    impact_level=9,
    tags="microservices,architecture"
)
```

**Типы milestone:**
- `architecture_decision` - архитектурные решения
- `problem_identified` - выявленные проблемы
- `solution_implemented` - реализованные решения
- `status_change` - изменения статуса

#### 7. `get_current_project_state`
Возвращает актуальное состояние проекта.

```python
await get_current_project_state("web_app")
```

**Включает:**
- Последние 5 milestones
- Актуальную информацию по категориям
- Исключает deprecated и expired данные
- Сортировка по confidence level

#### 8. `track_project_evolution`
Показывает эволюцию понимания проекта во времени.

```python
await track_project_evolution("web_app", category="architecture")
```

**Timeline включает:**
- Все записи включая deprecated (для истории)
- Версионные связи между записями
- Reasoning для deprecation
- Milestone progression

## Структура Данных

### Расширенные Metadata Поля

```json
{
  "project_id": "web_app",
  "category": "architecture", 
  "confidence_level": 8,
  "source": "code_analysis",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "expires_at": "2025-06-15T10:30:00Z",
  "version": 1,
  "status": "active",
  "superseded_by": null,
  "conflict_with": [],
  "validation_needed": false,
  "tags": ["backend", "database"],
  "accuracy_validated": true,
  "last_accessed": "2025-01-15T10:30:00Z"
}
```

### Статусы Записей

- **`active`** - актуальная информация
- **`deprecated`** - устаревшая, замененная новой версией
- **`conflicted`** - обнаружен конфликт, требует разрешения

## Логика Обработки Конфликтов

### Автоматическое Обнаружение

1. **Семантический анализ** - сравнение content новой записи с существующими
2. **Similarity threshold** - записи с similarity > 0.7 считаются потенциально конфликтующими
3. **Category matching** - проверка на конфликты в рамках одной категории
4. **Project scope** - конфликты ищутся только в рамках одного проекта

### Разрешение Конфликтов

1. **Уведомление** - save_verified_memory возвращает warning о конфликте
2. **Контекст** - предоставляется информация о конфликтующих записях
3. **Ручное решение** - пользователь выбирает правильную информацию
4. **Автоматическое обновление** - система помечает старую информацию как deprecated

## Тестирование

### Обязательные Тесты

Все инструменты покрыты comprehensive тестами в `tests/test_enhanced_memory.py`:

1. **Тест точности контекста** - verify только актуальная информация возвращается
2. **Тест обнаружения конфликтов** - conflicting information детектируется
3. **Тест версионирования** - старые версии помечаются deprecated
4. **Тест валидации** - устаревшие записи находятся автоматически  
5. **Тест приоритизации** - записи сортируются по confidence и актуальности

### Сценарии Точности

- **Conflicting Tech Stack** - разные фреймворки для одного проекта
- **Outdated Status** - устаревшая информация о статусе проекта
- **Version Conflicts** - противоречивая информация о версиях

## Производительность

### Оптимизации

- **Индексы** для быстрого поиска по project_id и timestamps
- **Кеширование** часто запрашиваемого контекста
- **Batch operations** для multiple memory updates
- **Асинхронная валидация** в фоне для больших баз

### Масштабирование

- Supabase PostgreSQL с векторными индексами
- Mem0 embeddings для semantic search
- Pagination для больших результатов
- Connection pooling для concurrent access

## Миграция

### Из Оригинального mcp-mem0

1. **Backward Compatibility** - старые записи продолжают работать
2. **Gradual Migration** - новые записи используют enhanced metadata
3. **Data Enrichment** - старые записи могут быть обогащены через audit tools

## Best Practices

### Для Агентов

1. **Всегда используйте get_accurate_context** вместо search_memories для production
2. **Указывайте high confidence_level** только для проверенной информации
3. **Используйте project_id** для изоляции проектов
4. **Регулярно запускайте validate_project_context** для проверки качества

### Для Разработчиков

1. **Тестируйте conflict scenarios** при добавлении новых category
2. **Мониторьте health_score** для поддержания качества
3. **Используйте proper source attribution** для audit trail
4. **Настройте expiration** для time-sensitive информации

## Результат

✅ **Гарантирует актуальность** - автоматически исключает устаревшую информацию
✅ **Обнаруживает конфликты** - не позволяет противоречивой информации существовать незамеченной  
✅ **Версионирует изменения** - сохраняет историю, но предоставляет актуальную версию
✅ **Валидирует качество** - постоянно проверяет достоверность сохраненного контекста
✅ **Приоритизирует точность** - более достоверная информация имеет приоритет в выдаче

**Система решает проблему неточного контекста через многоуровневую валидацию и контроль качества данных.** 