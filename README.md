# 🚀 FastAPI-MCP Memory Server

Стабильный сервер памяти с 11 инструментами для Cursor через **SSE transport**.

## ⚡ Быстрый старт

```bash
# 1. Установи зависимости
npm run install-deps

# 2. Запусти FastAPI сервер
npm run server

# 3. Настрой Cursor (в новом терминале)
npm run config

# 4. Перезапусти Cursor IDE
# 5. Проверь инструменты памяти в Claude
```

**✅ Готово! Все инструменты памяти работают через MCP SSE**

## 📋 Доступные команды

```bash
npm run install-deps   # Установка Python зависимостей
npm run server         # Запуск FastAPI сервера (основной)
npm run server-dev     # Запуск в режиме разработки
npm run config         # Автонастройка Cursor MCP
npm run test-local     # Локальное тестирование
npm run health         # Проверка состояния сервера
npm start              # Запуск через Docker (для разработки)
npm stop               # Остановка Docker
```

## 📊 11 инструментов памяти

| Инструмент | Описание | Статус |
|------------|----------|--------|
| `save_memory` | Базовое сохранение | ✅ |
| `get_all_memories` | Все воспоминания | ✅ |
| `search_memories` | Семантический поиск | ✅ |
| `save_verified_memory` | С метаданными | ✅ |
| `get_accurate_context` | Точный контекст | ✅ |
| `validate_project_context` | Валидация проекта | ✅ |
| `resolve_context_conflict` | Разрешение конфликтов | ✅ |
| `audit_memory_quality` | Аудит качества | ✅ |
| `save_project_milestone` | Этапы проекта | ✅ |
| `get_current_project_state` | Состояние проекта | ✅ |
| `track_project_evolution` | Эволюция проекта | ✅ |

## 🔧 Использование в Cursor

1. **Запустить сервер**: `npm run server`
2. **Настроить Cursor**: `npm run config` + перезапуск Cursor
3. **Использовать в Claude**:

```
Сохрани в память: "Проект FastAPI-MCP работает отлично"
Найди в памяти: "FastAPI" 
Покажи все воспоминания
```

## 🏗️ Архитектура

```
Cursor IDE ──→ MCP SSE ──→ FastAPI Server ──→ Mem0
              (http://localhost:8000/mcp)
```

**Стек**: Python + FastAPI + FastAPI-MCP + Mem0 + SSE Transport

## 🔗 Endpoints

- **MCP**: `http://localhost:8000/mcp` (для Cursor)
- **REST API**: `http://localhost:8000/docs` (Swagger UI)
- **Health**: `http://localhost:8000/` (проверка статуса)

## 🔥 Преимущества

✅ **SSE Transport** - стандартное MCP подключение  
✅ **Простая настройка** - одна команда  
✅ **Стабильность** - исправлены все ошибки  
✅ **REST + MCP** - доступно через оба протокола  
✅ **Готов к использованию** - всё включено  

## 🛠️ Требования

- **Python** 3.11+
- **Node.js** ≥18 (для настройки)

## 🐳 Docker (опционально)

Для разработки можно использовать Docker:

```bash
npm start     # Запуск в Docker
npm stop      # Остановка
```

## 🚨 Альтернативная настройка через npx

Если SSE не работает, можно использовать npx прокси:

```json
{
  "mcpServers": {
    "fastapi-mem0-memory": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

---

**Простое решение с правильным MCP transport! 🚀**
