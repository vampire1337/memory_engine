# 🧠 COMPREHENSIVE TOOLS GUIDE - 17 ENTERPRISE MEMORY TOOLS

## 📖 **ОБЗОР СИСТЕМЫ**

**MCP-Mem0 Enterprise Server v2.0** предоставляет 17 производственных инструментов для работы с памятью AI агентов через Model Context Protocol (MCP).

### 🏗️ **АРХИТЕКТУРА:**
- **FastAPI-MCP Integration** - автоматическая генерация MCP tools из FastAPI endpoints
- **Mem0 Graph + Vector Memory** - гибридное хранение с графовыми связями и семантическим поиском
- **Redis Synchronization** - события, кэширование и distributed locking
- **Enterprise Error Handling** - comprehensive monitoring и logging
- **Background Tasks** - асинхронная обработка heavy operations

### 📊 **КАТЕГОРИИ TOOLS:**
- **📚 Базовые Memory Tools (11)** - основные операции с памятью
- **🕸️ Graph Memory Tools (4)** - работа с графовыми связями
- **⚙️ Системные Tools (2)** - мониторинг и диагностика

---

## 📚 **БАЗОВЫЕ MEMORY TOOLS (11 инструментов)**

### 1️⃣ **save_memory** - Сохранение памяти

**Назначение:** Сохраняет информацию в Graph и Vector память одновременно с Redis синхронизацией.

**Параметры:**
```json
{
  "content": "string (обязательно) - Контент для сохранения",
  "user_id": "string (по умолчанию: 'user') - ID пользователя", 
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии",
  "metadata": "object (опционально) - Дополнительные метаданные"
}
```

**Пример использования:**
```json
{
  "content": "Пользователь предпочитает Python для разработки и работает в команде из 5 человек",
  "user_id": "dev_alex",
  "agent_id": "coding_assistant", 
  "session_id": "session_2024_001",
  "metadata": {
    "category": "preferences",
    "priority": "high",
    "source": "conversation"
  }
}
```

**Возвращает:**
```json
{
  "id": "mem_abc123",
  "message": "Memory added successfully",
  "user_id": "dev_alex",
  "content": "...",
  "metadata": {...},
  "graph_processed": true,
  "vector_processed": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Особенности:**
- Автоматическое извлечение сущностей для графа
- Векторизация для семантического поиска
- Redis events для синхронизации
- Background tasks для heavy processing

---

### 2️⃣ **search_memories** - Поиск воспоминаний

**Назначение:** Hybrid поиск по Graph и Vector памяти с Redis кэшированием.

**Параметры:**
```json
{
  "query": "string (обязательно) - Поисковый запрос",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента", 
  "session_id": "string (опционально) - ID сессии",
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "предпочтения пользователя по языкам программирования",
  "user_id": "dev_alex",
  "limit": 10
}
```

**Возвращает:**
```json
{
  "query": "предпочтения пользователя по языкам программирования",
  "user_id": "dev_alex", 
  "memories": [
    {
      "id": "mem_abc123",
      "memory": "Пользователь предпочитает Python для разработки...",
      "score": 0.95,
      "metadata": {...},
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_found": 3,
  "search_type": "hybrid",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Особенности:**
- Hybrid search (Graph + Vector)
- Redis кэширование результатов (TTL: 5 минут)
- Автоматический scoring relevance
- Графовый traversal для связанных memories

---

### 3️⃣ **get_all_memories** - Получение всех воспоминаний

**Назначение:** Получить все сохраненные воспоминания пользователя.

**Параметры:**
```json
{
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии"
}
```

**Пример использования:**
```json
{
  "user_id": "dev_alex",
  "agent_id": "coding_assistant"
}
```

**Возвращает:**
```json
{
  "user_id": "dev_alex",
  "memories": [
    {
      "id": "mem_abc123",
      "memory": "Пользователь предпочитает Python...",
      "metadata": {...},
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 25,
  "limit_applied": 50,
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Применение:**
- Backup всех воспоминаний пользователя
- Анализ полной истории взаимодействий
- Migration данных между системами

---

### 4️⃣ **save_verified_memory** - Сохранение проверенной памяти

**Назначение:** Сохраняет проверенную информацию с уровнем уверенности.

**Параметры:**
```json
{
  "content": "string (обязательно) - Проверенный контент",
  "confidence": "float (по умолчанию: 0.9) - Уровень уверенности (0.0-1.0)",
  "source": "string (по умолчанию: 'verified') - Источник информации",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "metadata": "object (опционально) - Метаданные"
}
```

**Пример использования:**
```json
{
  "content": "Пользователь Alex работает Senior Python Developer в компании TechCorp",
  "confidence": 0.95,
  "source": "linkedin_profile",
  "user_id": "dev_alex",
  "metadata": {
    "verification_method": "profile_crawl",
    "last_updated": "2024-01-15",
    "verified_by": "hr_system"
  }
}
```

**Возвращает:**
```json
{
  "id": "mem_verified_123",
  "message": "Memory added successfully", 
  "user_id": "dev_alex",
  "new_content": "...",
  "metadata": {
    "verified": true,
    "confidence": 0.95,
    "source": "linkedin_profile",
    "verification_date": "2024-01-15T11:00:00Z"
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Применение:**
- Сохранение проверенных фактов о пользователе
- Документированные данные с источниками
- High-confidence информация для критических решений

---

### 5️⃣ **get_accurate_context** - Получение точного контекста

**Назначение:** Получает максимально релевантный контекст для запроса.

**Параметры:**
```json
{
  "query": "string (обязательно) - Поисковый запрос",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии", 
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "текущий проект пользователя и его роль в команде",
  "user_id": "dev_alex",
  "limit": 3
}
```

**Возвращает:**
```json
{
  "query": "текущий проект пользователя и его роль в команде",
  "user_id": "dev_alex",
  "context_memories": [
    {
      "id": "mem_project_123", 
      "memory": "Пользователь ведет проект интеграции API...",
      "score": 0.92,
      "metadata": {...}
    }
  ],
  "total_context_found": 3,
  "accuracy_level": "high"
}
```

**Особенности:**
- Фильтрация по relevance score > 0.7
- Приоритизация high-confidence воспоминаний
- Expanded search для лучшего контекста

**Применение:**
- Подготовка контекста для AI ответов
- Gathering relevant background information
- Context-aware conversations

---

### 6️⃣ **validate_project_context** - Валидация проектного контекста

**Назначение:** Проверяет корректность и полноту проектного контекста.

**Параметры:**
```json
{
  "query": "string (обязательно) - Запрос о проекте",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии",
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "проект API интеграции",
  "user_id": "dev_alex"
}
```

**Возвращает:**
```json
{
  "query": "проект API интеграции",
  "user_id": "dev_alex",
  "total_memories": 8,
  "validation_score": 0.8,
  "issues": [],
  "recommendations": [
    "Контекст проекта достаточен"
  ]
}
```

**Validation Logic:**
- `score = 0.0` - Нет контекста (0 memories)
- `score = 0.5` - Недостаточно контекста (< 3 memories)  
- `score = 1.0` - Отличный контекст (≥ 10 memories)

**Применение:**
- Quality assurance для project knowledge
- Определение недостающей информации
- Planning knowledge acquisition

---

### 7️⃣ **resolve_context_conflict** - Разрешение конфликтов контекста

**Назначение:** Анализирует и разрешает противоречия в памяти.

**Параметры:**
```json
{
  "query": "string (обязательно) - Запрос для анализа конфликтов",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии",
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "предпочтения языков программирования",
  "user_id": "dev_alex"
}
```

**Возвращает:**
```json
{
  "query": "предпочтения языков программирования",
  "user_id": "dev_alex",
  "conflicts_found": 1,
  "conflicts": [
    {
      "memory1": {
        "id": "mem_123",
        "memory": "Пользователь предпочитает Python"
      },
      "memory2": {
        "id": "mem_456", 
        "memory": "Пользователь не любит Python"
      },
      "conflict_type": "contradiction"
    }
  ],
  "resolved_memories": [...],
  "resolution_strategy": "prioritize_recent"
}
```

**Conflict Detection:**
- Поиск противоположных утверждений
- Анализ отрицаний ("не", "никогда")
- Temporal conflicts (изменения предпочтений)

**Применение:**
- Data quality improvement
- Resolving inconsistent information
- Timeline analysis of changing preferences

---

### 8️⃣ **audit_memory_quality** - Аудит качества памяти

**Назначение:** Анализирует качество и целостность памяти пользователя.

**Параметры:**
```json
{
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии"
}
```

**Пример использования:**
```json
{
  "user_id": "dev_alex"
}
```

**Возвращает:**
```json
{
  "total_memories": 25,
  "duplicates": 2,
  "incomplete": 3,
  "high_quality": 18,
  "average_content_length": 125.5,
  "metadata_coverage": 0.8,
  "quality_score": 0.85,
  "recommendations": [
    "Удалить 2 дубликата",
    "Дополнить 3 неполных записей"
  ]
}
```

**Quality Metrics:**
- **High Quality (40%)** - длина > 50 символов
- **No Duplicates (30%)** - уникальность контента  
- **Completeness (20%)** - отсутствие коротких записей
- **Metadata Coverage (10%)** - наличие метаданных

**Применение:**
- Memory system health monitoring
- Data cleanup recommendations
- Quality improvement planning

---

### 9️⃣ **save_project_milestone** - Сохранение milestone проекта

**Назначение:** Сохраняет важные этапы развития проекта.

**Параметры:**
```json
{
  "milestone_name": "string (обязательно) - Название milestone",
  "description": "string (обязательно) - Описание milestone", 
  "project_id": "string (обязательно) - ID проекта",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "metadata": "object (опционально) - Метаданные"
}
```

**Пример использования:**
```json
{
  "milestone_name": "API Integration MVP",
  "description": "Завершена базовая интеграция с внешним API, покрытие тестами 80%",
  "project_id": "api_integration_2024",
  "user_id": "dev_alex",
  "metadata": {
    "completion_date": "2024-01-15",
    "team_size": 5,
    "sprint": "sprint_8"
  }
}
```

**Возвращает:**
```json
{
  "id": "mem_milestone_123",
  "message": "Memory added successfully",
  "user_id": "dev_alex",
  "content": "MILESTONE: API Integration MVP\nПроект: api_integration_2024\nОписание: Завершена базовая интеграция...",
  "metadata": {
    "type": "project_milestone",
    "milestone_name": "API Integration MVP",
    "project_id": "api_integration_2024", 
    "milestone_date": "2024-01-15T11:00:00Z",
    "importance": "high"
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Применение:**
- Project progress tracking
- Team achievement documentation  
- Historical project analysis
- Performance review preparation

---

### 🔟 **get_current_project_state** - Текущее состояние проекта

**Назначение:** Получает текущее состояние проекта на основе памяти.

**Параметры:**
```json
{
  "query": "string (обязательно) - Запрос о проекте",
  "user_id": "string (по умолчанию: 'user') - ID пользователя", 
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии",
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "api_integration_2024",
  "user_id": "dev_alex"
}
```

**Возвращает:**
```json
{
  "query": "api_integration_2024",
  "user_id": "dev_alex",
  "total_project_memories": 12,
  "milestones": [
    {
      "name": "API Integration MVP",
      "date": "2024-01-15T11:00:00Z",
      "memory_id": "mem_milestone_123"
    }
  ],
  "current_status": "in_progress",
  "last_activity": "2024-01-15T10:30:00Z",
  "completion_estimate": 0.6
}
```

**Status Logic:**
- `planning` - 0 milestones
- `in_progress` - 1-2 milestones
- `advanced` - 3+ milestones

**Completion Estimate:**
- `completion = min(milestones_count / 5.0, 1.0)`

**Применение:**
- Project status reporting
- Progress visualization  
- Planning next milestones
- Stakeholder updates

---

### 1️⃣1️⃣ **track_project_evolution** - Отслеживание эволюции проекта

**Назначение:** Анализирует развитие проекта во времени.

**Параметры:**
```json
{
  "query": "string (обязательно) - Запрос о проекте",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента", 
  "session_id": "string (опционально) - ID сессии",
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "api_integration_2024",
  "user_id": "dev_alex",
  "limit": 20
}
```

**Возвращает:**
```json
{
  "query": "api_integration_2024",
  "user_id": "dev_alex",
  "timeline": [
    {
      "date": "2024-01-15T11:00:00Z",
      "content": "MILESTONE: API Integration MVP Завершена базовая интеграция...",
      "type": "project_milestone"
    },
    {
      "date": "2024-01-10T09:00:00Z", 
      "content": "Началась работа над интеграцией API...",
      "type": "regular"
    }
  ],
  "phases": ["Планирование", "Разработка", "Развитие"],
  "growth_rate": 4.0,
  "key_changes": [],
  "trend": "growing"
}
```

**Trend Analysis:**
- `early_stage` - < 5 memories
- `developing` - 5-9 memories  
- `growing` - ≥ 10 memories

**Phases Logic:**
- ≥ 3 milestones: ["Планирование", "Разработка", "Развитие"]
- ≥ 1 milestone: ["Планирование", "Разработка"]
- 0 milestones: ["Планирование"]

**Применение:**
- Project retrospectives
- Evolution pattern analysis
- Growth rate tracking
- Long-term planning

---

## 🕸️ **GRAPH MEMORY TOOLS (4 инструмента)**

### 1️⃣2️⃣ **save_graph_memory** - Сохранение графовой памяти

**Назначение:** Сохраняет память с извлечением графовых сущностей и связей.

**Параметры:**
```json
{
  "content": "string (обязательно) - Контент для сохранения",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии",
  "metadata": "object (опционально) - Дополнительные метаданные"
}
```

**Пример использования:**
```json
{
  "content": "Alex работает с John над проектом интеграции API. John является тимлидом команды и имеет опыт работы с Python. Mary тестирует их код.",
  "user_id": "dev_alex",
  "metadata": {
    "context": "team_relationships", 
    "extract_entities": true
  }
}
```

**Возвращает:**
```json
{
  "id": "mem_graph_123",
  "message": "Memory added successfully",
  "user_id": "dev_alex",
  "content": "Alex работает с John над проектом...",
  "metadata": {
    "type": "graph_memory",
    "graph_processing": true,
    "entity_extraction": true,
    "timestamp": "2024-01-15T11:00:00Z",
    "client_version": "2.0.0"
  },
  "graph_processed": true,
  "vector_processed": true,
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Graph Processing:**
- Автоматическое извлечение сущностей (Alex, John, Mary)
- Определение отношений (работает_с, является_тимлидом, тестирует)
- Создание связей в Memgraph
- Одновременное векторное индексирование

**Применение:**
- Mapping team relationships
- Project collaboration networks
- Knowledge graphs construction
- Entity relationship tracking

---

### 1️⃣3️⃣ **search_graph_memory** - Поиск по графовой памяти

**Назначение:** Выполняет семантический поиск с использованием графовых связей.

**Параметры:**
```json
{
  "query": "string (обязательно) - Поисковый запрос",
  "user_id": "string (по умолчанию: 'user') - ID пользователя",
  "agent_id": "string (опционально) - ID агента",
  "session_id": "string (опционально) - ID сессии",
  "limit": "integer (по умолчанию: 5) - Максимальное количество результатов"
}
```

**Пример использования:**
```json
{
  "query": "кто работает с Alex в команде",
  "user_id": "dev_alex",
  "limit": 10
}
```

**Возвращает:**
```json
{
  "query": "кто работает с Alex в команде",
  "user_id": "dev_alex",
  "memories": [
    {
      "id": "mem_graph_123",
      "memory": "Alex работает с John над проектом интеграции API...",
      "score": 0.95,
      "metadata": {
        "type": "graph_memory",
        "entities_found": ["Alex", "John"],
        "relationships": ["работает_с"]
      }
    }
  ],
  "total_found": 3,
  "search_type": "graph_enhanced",
  "graph_support": true,
  "relationship_traversal": true,
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Graph Enhancement:**
- Multi-hop relationship traversal
- Entity-centric search
- Connection strength scoring
- Relationship type filtering

**Применение:**
- Finding connected entities
- Relationship discovery
- Network analysis queries
- Context-aware search

---

### 1️⃣4️⃣ **get_entity_relationships** - Получение связей сущности

**Назначение:** Анализирует графовые связи конкретной сущности.

**Параметры:**
```json
{
  "entity_name": "string (обязательно) - Имя сущности для анализа",
  "user_id": "string (по умолчанию: 'user') - ID пользователя"
}
```

**Пример использования:**
```json
{
  "entity_name": "Alex",
  "user_id": "dev_alex"
}
```

**Возвращает:**
```json
{
  "entity_name": "Alex",
  "user_id": "dev_alex",
  "direct_mentions": 5,
  "related_entities": ["John", "Mary", "Python", "API интеграция"],
  "relationship_types": ["personal", "professional", "action"],
  "connection_strength": 0.87,
  "memory_references": [
    {
      "memory_id": "mem_graph_123",
      "relevance": 0.95
    }
  ]
}
```

**Relationship Analysis:**
- **Direct mentions** - количество упоминаний сущности
- **Related entities** - связанные сущности (извлечение через " и ", соседние слова)
- **Relationship types** - типы отношений:
  - `action` - работает, делает, создает
  - `personal` - знает, друг, коллега
  - `professional` - проект, задача, команда
- **Connection strength** - средний relevance score

**Применение:**
- Entity profile building
- Relationship mapping
- Network centrality analysis
- Context understanding

---

### 1️⃣5️⃣ **graph_status** - Статус графовой системы

**Назначение:** Проверяет состояние графовой памяти и связей.

**Параметры:** Нет (GET endpoint)

**Пример использования:** Простой вызов без параметров

**Возвращает:**
```json
{
  "graph_available": true,
  "vector_available": true,
  "graph_store_type": "memgraph",
  "vector_store_type": "supabase",
  "hybrid_mode": true,
  "capabilities": {
    "entity_extraction": true,
    "relationship_mapping": true,
    "semantic_search": true,
    "multi_hop_reasoning": true
  },
  "graph_info": {
    "status": "active",
    "connection": "healthy",
    "features": [
      "entity_extraction",
      "relationship_inference", 
      "graph_traversal"
    ]
  }
}
```

**Status Values:**
- **graph_available** - Memgraph подключен и работает
- **vector_available** - Supabase vector store активен
- **hybrid_mode** - оба store доступны одновременно

**Применение:**
- System health monitoring
- Capability discovery
- Troubleshooting graph issues
- Feature availability checks

---

## ⚙️ **СИСТЕМНЫЕ TOOLS (2 инструмента)**

### 1️⃣6️⃣ **health** - Комплексная проверка здоровья

**Назначение:** Комплексная проверка состояния всех компонентов системы.

**Параметры:** Нет (GET endpoint)

**Пример использования:** Простой вызов без параметров

**Возвращает:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-01-15T11:00:00Z",
  "components": {
    "memory": {
      "status": "healthy",
      "initialized": true,
      "graph_support": true,
      "vector_support": true,
      "redis_support": true,
      "metrics": {
        "operations_count": 150,
        "errors_count": 2,
        "cache_hits": 45,
        "cache_misses": 15,
        "error_rate": 0.013
      },
      "capabilities": {
        "add_memory": true,
        "search_memory": true,
        "graph_operations": true,
        "vector_operations": true,
        "hybrid_search": true
      }
    },
    "redis": {
      "status": "connected",
      "ping_success": true,
      "memory_usage": "2.5MB",
      "connected_clients": 3,
      "operations": {
        "cache_operations": 60,
        "events_published": 12,
        "sessions_active": 5
      }
    },
    "graph": {
      "status": "active"
    },
    "vector": {
      "status": "active"
    }
  }
}
```

**Health Status Values:**
- `healthy` - все компоненты работают нормально
- `degraded` - есть проблемы, но система функционирует
- `partial` - часть компонентов недоступна
- `unhealthy` - критические проблемы

**Применение:**
- Production monitoring
- Automated health checks
- Load balancer health endpoints
- System diagnostics

---

### 1️⃣7️⃣ **root** - Информация о системе

**Назначение:** Предоставляет общую информацию о системе и доступных endpoints.

**Параметры:** Нет (GET endpoint)

**Пример использования:** Простой вызов без параметров

**Возвращает:**
```json
{
  "name": "🧠 Enterprise MCP-Mem0 Server",
  "version": "2.0.0",
  "description": "17 Production-ready Memory Tools for AI Agents",
  "tools_count": 17,
  "features": {
    "memory_tools": 11,
    "graph_tools": 4,
    "system_tools": 2,
    "redis_integration": true,
    "graph_memory": true,
    "vector_memory": true,
    "enterprise_ready": true
  },
  "endpoints": {
    "memory": [
      "/memory/save", "/memory/search", "/memory/get-all",
      "/memory/save-verified", "/memory/get-context",
      "/memory/validate-project-context", "/memory/resolve-conflict",
      "/memory/audit-quality", "/memory/save-milestone",
      "/memory/get-project-state", "/memory/track-evolution"
    ],
    "graph": [
      "/graph/save-memory", "/graph/search",
      "/graph/entity-relationships", "/graph/status"
    ],
    "system": ["/health", "/"]
  },
  "mcp_endpoint": "/mcp",
  "documentation": "/docs"
}
```

**Применение:**
- API discovery
- System capabilities overview
- Documentation generation
- Client configuration

---

## 🚀 **ЗАПУСК И ТЕСТИРОВАНИЕ СИСТЕМЫ**

### 📋 **Prerequisites:**
```bash
# Переменные окружения
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export NEO4J_URL="bolt://memgraph:7687"
export NEO4J_USERNAME="memgraph"
export NEO4J_PASSWORD="graphmemory123"
export REDIS_URL="redis://:password@redis:6379/0"
```

### 🐳 **Docker Deployment:**
```bash
# Сборка и запуск
docker-compose -f docker-compose.production.yml up --build

# Проверка здоровья
curl http://localhost:8000/health

# MCP endpoint
curl http://localhost:8000/mcp
```

### 🧪 **Manual Testing через MCP Inspector:**
```bash
# Установка MCP Inspector
npx @modelcontextprotocol/inspector

# Подключение к серверу
# URL: http://localhost:8000/mcp

# Тестирование tools:
# 1. List Tools -> должно показать все 17 tools
# 2. Выбрать save_memory
# 3. Заполнить параметры
# 4. Run Tool
# 5. Проверить результат
```

### 🔧 **Configuration для Cursor:**
```json
{
  "mcpServers": {
    "mcp-mem0-enterprise": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## 📊 **МОНИТОРИНГ И ЛОГИРОВАНИЕ**

### 📈 **Metrics Tracking:**
- **Operations Count** - общее количество операций
- **Error Rate** - процент ошибок
- **Cache Hit Rate** - эффективность кэширования  
- **Response Time** - время ответа tools
- **Memory Usage** - использование Redis

### 📝 **Logging Levels:**
- **INFO** - обычные операции
- **WARNING** - потенциальные проблемы
- **ERROR** - ошибки операций
- **DEBUG** - детальная отладка

### 🔔 **Redis Events:**
- `vector_updated` - обновление векторной памяти
- `entity_created` - создание новой сущности
- `search_performed` - выполнение поиска
- `verified_memory_added` - добавление проверенной памяти

---

## 🎯 **BEST PRACTICES**

### 💡 **Memory Management:**
1. **Используйте meaningful user_ids** для сегментации данных
2. **Добавляйте rich metadata** для лучшей фильтрации
3. **Регулярно проверяйте качество** через audit_memory_quality
4. **Разрешайте конфликты** через resolve_context_conflict

### 🔐 **Security:**
1. **Валидируйте все входные данные**
2. **Используйте session_id** для изоляции сессий
3. **Мониторьте error rate** для обнаружения атак
4. **Ограничивайте limit** параметры

### ⚡ **Performance:**
1. **Используйте кэширование** для частых запросов
2. **Оптимизируйте limit** параметры
3. **Мониторьте Redis память** 
4. **Используйте background tasks** для heavy operations

### 🔄 **Integration:**
1. **Обрабатывайте все возможные ошибки**
2. **Используйте exponential backoff** для retry
3. **Мониторьте health endpoint**
4. **Логируйте все важные операции**

---

## 🎉 **ЗАКЛЮЧЕНИЕ**

**Enterprise MCP-Mem0 Server v2.0** предоставляет полноценную систему управления памятью для AI агентов с 17 производственными инструментами, covering все аспекты от базовых операций до продвинутого графового анализа.

**Система готова к production deployment** с comprehensive monitoring, error handling, и enterprise-grade архитектурой. 