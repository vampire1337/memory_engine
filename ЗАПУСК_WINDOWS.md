# 🚀 ЗАПУСК НА WINDOWS - ПОДРОБНАЯ ИНСТРУКЦИЯ

## ❌ ИСПРАВЛЕННЫЕ ПРОБЛЕМЫ

### 1. **Ошибка `embedding_dims`**
- **Проблема**: Mem0 новой версии не поддерживает параметр `embedding_dims`
- **Исправление**: Удален из всех конфигураций

### 2. **Неправильный путь к utils.py в Docker**
- **Проблема**: Dockerfile.unified копировал `utils.py` из корня вместо `src/utils.py`
- **Исправление**: Исправлен путь в Dockerfile.unified

### 3. **Проблемы с Make на Windows**
- **Решение**: Создана полная инструкция для запуска через Docker напрямую

---

## 🎯 БЫСТРЫЙ ЗАПУСК (5 МИНУТ)

### Шаг 1: Подготовка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# ======== ОСНОВНЫЕ НАСТРОЙКИ ========
OPENAI_API_KEY=your_openai_api_key_here

# ======== БАЗЫ ДАННЫХ ========
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphmemory123

POSTGRES_URL=postgresql://postgres:postgres123@localhost:5432/unified_memory

# ======== СЕРВЕР ========
MEMORY_SERVER_PORT=8051
LOG_LEVEL=info
ENVIRONMENT=production
```

### Шаг 2: Запуск системы

Откройте **PowerShell как Администратор** и выполните:

```powershell
# Перейти в папку проекта
cd C:\Users\mihai\Heist_master_PC\Documents\GitHub\mcp-mem0

# Остановить все контейнеры (если запущены)
docker-compose -f docker-compose.unified.yml down

# Очистить старые образы
docker system prune -f

# Запустить unified систему
docker-compose -f docker-compose.unified.yml up -d --build
```

### Шаг 3: Проверка запуска

```powershell
# Проверить статус контейнеров
docker-compose -f docker-compose.unified.yml ps

# Проверить логи memory-server
docker-compose -f docker-compose.unified.yml logs -f memory-server

# Проверить health check
curl http://localhost:8051/health
```

---

## 🔧 ВАРИАНТЫ ЗАПУСКА

### 1. **МИНИМАЛЬНАЯ КОНФИГУРАЦИЯ** (только память + Neo4j)

```powershell
docker-compose -f docker-compose.unified.yml up -d neo4j postgres memory-server
```

### 2. **ПОЛНАЯ КОНФИГУРАЦИЯ** (с мониторингом)

```powershell
docker-compose -f docker-compose.unified.yml --profile monitoring up -d
```

### 3. **ТОЛЬКО ГРАФОВАЯ ПАМЯТЬ**

```powershell
docker-compose -f docker-compose.unified.yml up -d neo4j memory-server
```

### 4. **РАЗРАБОТЧЕСКАЯ КОНФИГУРАЦИЯ**

```powershell
# Запуск с живыми логами
docker-compose -f docker-compose.unified.yml up --build
```

---

## 🛠️ ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ПРОБЛЕМ

### Проблема: Ошибка embedding_dims

```powershell
# ПРИНУДИТЕЛЬНАЯ ПЕРЕСБОРКА (исправляет embedding_dims)
.\запуск_windows.ps1 -ForceRebuild

# Или вручную:
docker-compose -f docker-compose.unified.yml down
docker system prune -af
docker-compose -f docker-compose.unified.yml build --no-cache
docker-compose -f docker-compose.unified.yml up -d
```

### Проблема: Контейнер memory-server не запускается

```powershell
# 1. Проверить логи детально
docker-compose -f docker-compose.unified.yml logs memory-server

# 2. Проверить переменные окружения
docker-compose -f docker-compose.unified.yml exec memory-server env | grep -E "(OPENAI|NEO4J)"

# 3. Проверить подключение к базам
docker-compose -f docker-compose.unified.yml exec neo4j cypher-shell -u neo4j -p graphmemory123 "RETURN 'Neo4j works!' as status"
```

### Проблема: Спам контейнеров

```powershell
# Остановить все и очистить
docker-compose -f docker-compose.unified.yml down
docker system prune -af
docker volume prune -f

# Перезапустить чисто
docker-compose -f docker-compose.unified.yml up -d --build
```

### Проблема: Ошибки API ключей

```powershell
# Проверить .env файл
Get-Content .env

# Убедиться что ключ установлен
$env:OPENAI_API_KEY = "your_key_here"
docker-compose -f docker-compose.unified.yml up -d --build
```

---

## 🔍 ПРОВЕРКА РАБОТОСПОСОБНОСТИ

### Проверка Health API

```powershell
# Базовый health check
curl http://localhost:8051/health

# Подробный статус системы
curl http://localhost:8051/graph/status

# Тест сохранения памяти
curl -X POST http://localhost:8051/memory/save `
  -H "Content-Type: application/json" `
  -d '{"content": "Тестовая память", "user_id": "test"}'
```

### Проверка Neo4j Web UI

1. Откройте http://localhost:7474
2. Войдите: `neo4j` / `graphmemory123`
3. Выполните: `MATCH (n) RETURN count(n) as total_nodes`

### Проверка PostgreSQL

```powershell
# Подключение к PostgreSQL
docker-compose -f docker-compose.unified.yml exec postgres psql -U postgres -d unified_memory -c "SELECT version();"
```

---

## 📊 МОНИТОРИНГ (ОПЦИОНАЛЬНО)

### Запуск с мониторингом

```powershell
docker-compose -f docker-compose.unified.yml --profile monitoring up -d
```

### Доступ к интерфейсам:

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Neo4j Browser**: http://localhost:7474
- **Memory API**: http://localhost:8051/docs

---

## 🚨 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ

### Если ничего не работает:

```powershell
# 1. Полная очистка Docker
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -q)
docker volume rm $(docker volume ls -q)
docker network prune -f

# 2. Перезагрузка Docker Desktop
# Перезапустите Docker Desktop через трей

# 3. Чистый запуск
cd C:\Users\mihai\Heist_master_PC\Documents\GitHub\mcp-mem0
docker-compose -f docker-compose.unified.yml up -d --build
```

### Если есть конфликты портов:

```powershell
# Найти процессы на портах
netstat -ano | findstr :8051
netstat -ano | findstr :7474
netstat -ano | findstr :7687

# Остановить процесс (замените PID)
taskkill /PID <PID> /F
```

---

## ✅ ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После успешного запуска вы должны увидеть:

```
✅ unified-memory-neo4j      healthy
✅ unified-memory-postgres   healthy  
✅ unified-memory-server     healthy
✅ unified-memory-redis      healthy
```

### Тестирование системы:

```powershell
# Тест базовой памяти
curl -X POST http://localhost:8051/memory/save -H "Content-Type: application/json" -d '{"content": "Windows запуск работает!", "user_id": "windows_user"}'

# Тест поиска
curl -X POST http://localhost:8051/memory/search -H "Content-Type: application/json" -d '{"query": "Windows", "user_id": "windows_user"}'

# Тест графовой памяти
curl -X POST http://localhost:8051/graph/save-memory -H "Content-Type: application/json" -d '{"content": "Neo4j граф работает", "user_id": "graph_user"}'
```

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. **Настройка MCP клиента** (cursor_mcp_config.json)
2. **Тестирование всех 15 инструментов памяти**
3. **Настройка мониторинга производительности**
4. **Бэкап и восстановление данных**

---

**ВАЖНО**: Если проблемы продолжаются, проверьте:
- Windows Defender не блокирует Docker
- Hyper-V включен
- WSL2 настроен корректно
- Достаточно RAM (минимум 8GB) 