# 🕸️ Graph Memory Upgrade Guide

## 🎯 Цель: Превратить нашу систему из 40% в 100% возможностей Mem0

### 📊 Текущее состояние vs Целевое

| Функция | Текущее | Целевое | Улучшение |
|---------|---------|---------|-----------|
| Vector Storage | ✅ Supabase | ✅ Supabase | Без изменений |
| Graph Storage | ❌ Нет | ✅ Neo4j | **+26% accuracy** |
| Entity Extraction | ❌ Нет | ✅ Автоматическое | Multi-hop reasoning |
| Relationships | ❌ Нет | ✅ Автоматическое | Связанные знания |
| User/Agent/Session | ❌ Только user | ✅ Полное разделение | Персонализация |
| Temporal Reasoning | ❌ Базовое | ✅ Продвинутое | Эволюция знаний |

---

## 🚀 Пошаговое внедрение

### PHASE 1: Подготовка инфраструктуры

```bash
# 1. Установка зависимостей
pip install -r requirements_graph.txt

# 2. Запуск Neo4j
chmod +x setup_neo4j_docker.sh
./setup_neo4j_docker.sh

# 3. Проверка Neo4j
# Откройте http://localhost:7474
# Логин: neo4j, Пароль: graphmemory123
```

### PHASE 2: Запуск Graph Memory сервера

```bash
# Запуск расширенного сервера на порту 8052
python src/graph_memory_upgrade.py
```

### PHASE 3: Обновление Cursor конфигурации

```json
{
  "mcpServers": {
    "fastapi-mem0-memory": {
      "url": "http://localhost:8051/mcp"
    },
    "graph-mem0-memory": {
      "url": "http://localhost:8052/mcp"
    }
  }
}
```

---

## 🔧 Новые возможности

### 1. **Entity-Relationship Extraction**
```python
# Автоматически извлекает:
# Entities: [Пользователь, FastAPI, MCP, Supabase, Neo4j]
# Relationships: [использует, интегрирует, хранит_в]
```

### 2. **Multi-hop Reasoning**
```python
# Может отвечать на вопросы типа:
# "Какие технологии использует пользователь для работы с памятью?"
# Граф: Пользователь -> использует -> FastAPI -> интегрирует -> MCP -> хранит_в -> Supabase
```

### 3. **User/Agent/Session Isolation**
```python
# Теперь поддерживается:
save_graph_memory(
    content="...",
    user_id="heist1337",
    agent_id="cursor-assistant", 
    session_id="coding-session-2025"
)
```

### 4. **Temporal Evolution Tracking**
```python
# Отслеживание изменений во времени:
# "Как эволюционировала архитектура проекта?"
```

---

## 📈 Ожидаемые улучшения

### Accuracy Boost
- **+26% точность** согласно исследованию Mem0
- **Лучше понимание контекста** через relationships
- **Multi-hop reasoning** для сложных вопросов

### Performance
- **91% быстрее** чем full-context
- **90% меньше токенов** чем традиционные методы
- **Эффективный поиск** по графу

### Capabilities
- **Entity-centric queries**: "Все что связано с FastAPI"
- **Relationship exploration**: "Как X связан с Y?"
- **Temporal reasoning**: "Что изменилось в проекте?"
- **Knowledge graph visualization**: Визуальное представление знаний

---

## 🧪 Тестирование новых функций

### 1. Проверка Graph Status
```bash
curl http://localhost:8052/graph/status
```

### 2. Сохранение с Entity Extraction
```bash
curl -X POST http://localhost:8052/graph/save-memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Пользователь heist1337 работает с FastAPI-MCP архитектурой, использует Supabase для векторов и Neo4j для графов",
    "user_id": "heist1337",
    "agent_id": "cursor",
    "project_id": "mcp-mem0-system"
  }'
```

### 3. Graph-Enhanced Search
```bash
curl -X POST http://localhost:8052/graph/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "архитектура системы",
    "user_id": "heist1337",
    "limit": 5
  }'
```

### 4. Entity Relationships
```bash
curl -X POST http://localhost:8052/graph/entity-relationships \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "FastAPI",
    "user_id": "heist1337"
  }'
```

---

## 🔍 Мониторинг и отладка

### Neo4j Web Interface
- URL: http://localhost:7474
- Логин: neo4j / graphmemory123
- Cypher queries для анализа графа

### Логи сервера
```bash
# Логи Graph Memory сервера
tail -f graph_memory.log

# Логи Neo4j
docker logs neo4j-graph-memory
```

### Проверка данных
```cypher
// В Neo4j браузере
MATCH (n) RETURN n LIMIT 25;  // Все nodes
MATCH ()-[r]->() RETURN r LIMIT 25;  // Все relationships
```

---

## 🎯 Результат

После внедрения получаем:

✅ **100% возможностей Mem0 SDK**
✅ **Graph Memory с Neo4j**
✅ **Entity & Relationship extraction**
✅ **Multi-hop reasoning**
✅ **User/Agent/Session isolation**
✅ **Temporal reasoning**
✅ **+26% accuracy boost**
✅ **Knowledge graph visualization**

**Наша система станет state-of-the-art memory solution!** 🚀 