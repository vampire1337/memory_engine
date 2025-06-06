# 🚀 БЫСТРЫЙ СТАРТ - FastAPI-MCP Memory Server

## 📋 Пошаговая инструкция

### 1️⃣ Установка зависимостей

```bash
npm run install-deps
```

### 2️⃣ Запуск FastAPI сервера

```bash
npm run server
```

**Сервер запустится на http://localhost:8000**

### 3️⃣ Настройка Cursor (в новом терминале)

```bash
npm run config
```

### 4️⃣ Перезапуск Cursor IDE

Полностью закройте и откройте Cursor снова.

### 5️⃣ Проверка работы

В Claude напишите:

```
Сохрани в память: "Тест FastAPI-MCP сервера"
```

```
Найди в памяти: "тест"
```

```
Покажи все воспоминания
```

## ✅ Что должно работать

- ✅ Сохранение памяти
- ✅ Поиск в памяти  
- ✅ Показ всех воспоминаний
- ✅ Все 11 инструментов доступны

## 🔧 Конфигурация

Автоматически добавляется в Cursor:

```json
{
  "mcpServers": {
    "fastapi-mem0-memory": {
      "transport": "sse",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## 🚨 Альтернатива через npx

Если SSE не работает:

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

## 🔍 Проверка статуса

```bash
npm run health          # Проверка сервера
curl http://localhost:8000/    # Прямая проверка
```

## 📊 Доступные инструменты

1. **save_memory** - сохранить в память
2. **get_all_memories** - все воспоминания  
3. **search_memories** - поиск
4. **save_verified_memory** - сохранить с метаданными
5. **get_accurate_context** - точный контекст
6. **validate_project_context** - валидация проекта
7. **resolve_context_conflict** - разрешить конфликт  
8. **audit_memory_quality** - аудит качества
9. **save_project_milestone** - сохранить этап
10. **get_current_project_state** - состояние проекта
11. **track_project_evolution** - отследить эволюцию

## 🎯 Готово!

После выполнения всех шагов у вас будет работающий MCP сервер памяти с 11 инструментами!

---

**💡 Совет**: Держите FastAPI сервер запущенным в фоне для постоянного доступа к инструментам памяти. 