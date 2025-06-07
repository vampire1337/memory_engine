# 🚀 PRODUCTION DEPLOYMENT GUIDE

## 📋 **СИСТЕМНЫЕ ТРЕБОВАНИЯ**

### 🖥️ **Hardware Requirements:**
- **RAM:** минимум 4GB (рекомендуется 8GB+)
- **CPU:** 2+ cores (рекомендуется 4+ cores)
- **Storage:** 20GB+ свободного места
- **Network:** стабильное интернет-соединение

### 🐳 **Software Dependencies:**
- **Docker:** версия 20.10+
- **Docker Compose:** версия 2.0+
- **Git:** для клонирования репозитория

---

## ⚙️ **КОНФИГУРАЦИЯ ENVIRONMENT VARIABLES**

### 🔑 **Обязательные переменные:**
```bash
# OpenAI API (для Mem0)
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# Supabase Database (порт 5432 - Transaction pooler)
export DATABASE_URL="postgresql://postgres.xxxxx:password@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

# Memgraph Neo4j (для Graph Memory)
export NEO4J_URL="bolt://memgraph:7687"
export NEO4J_USERNAME="memgraph"
export NEO4J_PASSWORD="graphmemory123"

# Redis (для синхронизации и кэширования)
export REDIS_URL="redis://:redispassword@redis:6379/0"
```

### 🔧 **Опциональные переменные:**
```bash
# FastAPI конфигурация
export UVICORN_HOST="0.0.0.0"
export UVICORN_PORT="8000"
export UVICORN_WORKERS="1"
export LOG_LEVEL="info"

# Memory конфигурация
export MEM0_CONFIG_PATH="/app/mem0_config.yaml"
export REDIS_TTL="300"  # 5 минут кэш

# Мониторинг
export ENABLE_METRICS="true"
export METRICS_PORT="9090"
```

---

## 🐳 **DOCKER DEPLOYMENT**

### 1️⃣ **Подготовка окружения:**
```bash
# Клонирование репозитория
git clone https://github.com/your-repo/mcp-mem0
cd mcp-mem0

# Создание .env файла
cat > .env << 'EOF'
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
NEO4J_URL=bolt://memgraph:7687
NEO4J_USERNAME=memgraph
NEO4J_PASSWORD=graphmemory123
REDIS_URL=redis://:redispassword@redis:6379/0
EOF
```

### 2️⃣ **Запуск Production стека:**
```bash
# Сборка и запуск всех сервисов
docker-compose -f docker-compose.production.yml up -d --build

# Проверка статуса контейнеров
docker-compose -f docker-compose.production.yml ps

# Мониторинг логов
docker-compose -f docker-compose.production.yml logs -f mcp-memory-server
```

### 3️⃣ **Проверка работоспособности:**
```bash
# Health check
curl http://localhost:8000/health

# System info
curl http://localhost:8000/

# MCP endpoint
curl http://localhost:8000/mcp

# OpenAPI documentation
open http://localhost:8000/docs
```

---

## 🔍 **TESTING И VALIDATION**

### 🧪 **Manual Testing через HTTP:**
```bash
# 1. Сохранение памяти
curl -X POST "http://localhost:8000/memory/save" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Пользователь Alex предпочитает Python для разработки",
    "user_id": "test_user",
    "metadata": {"category": "preferences"}
  }'

# 2. Поиск памяти
curl -X POST "http://localhost:8000/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "предпочтения программирования",
    "user_id": "test_user",
    "limit": 5
  }'

# 3. Graph memory
curl -X POST "http://localhost:8000/graph/save-memory" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Alex работает с John над проектом API",
    "user_id": "test_user"
  }'

# 4. Получение всех воспоминаний
curl -X POST "http://localhost:8000/memory/get-all" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

### 🎯 **MCP Inspector Testing:**
```bash
# Установка MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Запуск Inspector
npx @modelcontextprotocol/inspector

# В браузере перейти на:
# http://localhost:3000

# Подключение к MCP серверу:
# URL: http://localhost:8000/mcp

# Тестирование всех 17 tools:
# 1. List Tools
# 2. Тестировать каждый tool по очереди
```

### 📊 **Automated Testing Script:**
```bash
#!/bin/bash
# test_all_tools.sh

BASE_URL="http://localhost:8000"
USER_ID="test_$(date +%s)"

echo "🧪 Testing all 17 Enterprise Memory Tools..."
echo "User ID: $USER_ID"

# Test 1: save_memory
echo "1️⃣ Testing save_memory..."
curl -s -X POST "$BASE_URL/memory/save" \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Test memory for $USER_ID\",\"user_id\":\"$USER_ID\"}" \
  | jq '.message'

# Test 2: search_memories
echo "2️⃣ Testing search_memories..."
curl -s -X POST "$BASE_URL/memory/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"test\",\"user_id\":\"$USER_ID\"}" \
  | jq '.total_found'

# Test 3: get_all_memories
echo "3️⃣ Testing get_all_memories..."
curl -s -X POST "$BASE_URL/memory/get-all" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\"}" \
  | jq '.total_count'

# ... continue for all 17 tools

echo "✅ All tools tested successfully!"
```

---

## 🔧 **CURSOR MCP INTEGRATION**

### 📝 **Cursor Configuration:**
```json
{
  "mcpServers": {
    "mcp-mem0-enterprise": {
      "url": "http://localhost:8000/mcp",
      "name": "Enterprise Memory System",
      "description": "17 production-ready memory tools for AI agents"
    }
  }
}
```

### 🎯 **Testing в Cursor:**
```
1. Открыть Cursor
2. Настроить MCP server (Tools -> MCP Servers)
3. Добавить конфигурацию выше
4. Перезапустить Cursor
5. Проверить доступность tools в @mcp-mem0-enterprise
6. Протестировать каждый tool:
   - @mcp-mem0-enterprise.save_memory
   - @mcp-mem0-enterprise.search_memories
   - ... все 17 tools
```

---

## 📊 **МОНИТОРИНГ И OBSERVABILITY**

### 🔍 **Logs Monitoring:**
```bash
# Все логи
docker-compose -f docker-compose.production.yml logs -f

# Только MCP сервер
docker-compose -f docker-compose.production.yml logs -f mcp-memory-server

# Только Redis
docker-compose -f docker-compose.production.yml logs -f redis

# Только Memgraph
docker-compose -f docker-compose.production.yml logs -f memgraph
```

### 📈 **Metrics Collection:**
```bash
# Проверка метрик Redis
docker exec -it $(docker ps -qf "name=redis") redis-cli INFO memory

# Проверка метрик приложения
curl http://localhost:8000/health | jq '.components.memory.metrics'

# Проверка использования ресурсов
docker stats $(docker ps -qf "name=mcp-memory-server")
```

### 🚨 **Health Monitoring:**
```bash
#!/bin/bash
# health_monitor.sh

while true; do
  STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
  
  if [ "$STATUS" != "healthy" ]; then
    echo "🚨 ALERT: System status is $STATUS"
    # Отправить уведомление (email, Slack, etc.)
  else
    echo "✅ System is healthy"
  fi
  
  sleep 30
done
```

---

## 🔧 **TROUBLESHOOTING**

### ❌ **Общие проблемы и решения:**

#### 1. **Database Connection Error**
```bash
# Проверка URL
echo $DATABASE_URL

# Тест подключения
docker run --rm postgres:15 psql $DATABASE_URL -c "\l"

# Решение: Проверить порт (5432 вместо 6543)
```

#### 2. **Redis Connection Error**
```bash
# Проверка Redis
docker exec -it $(docker ps -qf "name=redis") redis-cli ping

# Решение: Проверить пароль в REDIS_URL
```

#### 3. **Graph Memory Not Working**
```bash
# Проверка Memgraph
docker exec -it $(docker ps -qf "name=memgraph") mgconsole

# Решение: Проверить NEO4J_URL и credentials
```

#### 4. **Memory Client Initialization Error**
```bash
# Проверка логов
docker-compose -f docker-compose.production.yml logs mcp-memory-server | grep ERROR

# Решение: Проверить OPENAI_API_KEY
```

#### 5. **MCP Tools Not Available**
```bash
# Проверка MCP endpoint
curl http://localhost:8000/mcp

# Решение: Перезапустить FastAPI-MCP сервер
docker-compose -f docker-compose.production.yml restart mcp-memory-server
```

### 🔄 **Recovery Procedures:**

#### 🆘 **Complete System Reset:**
```bash
# Остановка всех сервисов
docker-compose -f docker-compose.production.yml down

# Очистка volumes (ОСТОРОЖНО! Удаляет все данные)
docker-compose -f docker-compose.production.yml down -v

# Пересборка и запуск
docker-compose -f docker-compose.production.yml up --build -d

# Проверка
curl http://localhost:8000/health
```

#### 🔧 **Partial Recovery:**
```bash
# Перезапуск только проблемного сервиса
docker-compose -f docker-compose.production.yml restart mcp-memory-server

# Просмотр логов для диагностики
docker-compose -f docker-compose.production.yml logs -f mcp-memory-server
```

---

## 🔐 **SECURITY BEST PRACTICES**

### 🛡️ **Production Security:**
1. **Изменить все пароли** по умолчанию
2. **Использовать HTTPS** в production
3. **Настроить firewall** для ограничения доступа
4. **Регулярно обновлять** Docker images
5. **Мониторить логи** на подозрительную активность

### 🔑 **API Key Management:**
```bash
# Использовать Docker secrets
echo "sk-xxxxxxxxxxxxxxxxxxxxxxxx" | docker secret create openai_api_key -

# Или переменные окружения в .env файле
# НИКОГДА не коммитить .env в Git!
```

### 📝 **Access Logging:**
```bash
# Включение detailed logging
export LOG_LEVEL="debug"

# Мониторинг API calls
tail -f logs/mcp-server.log | grep "POST\|GET"
```

---

## 🚀 **PRODUCTION OPTIMIZATION**

### ⚡ **Performance Tuning:**
```bash
# Увеличение workers для high load
export UVICORN_WORKERS="4"

# Оптимизация Redis память
docker exec -it $(docker ps -qf "name=redis") redis-cli CONFIG SET maxmemory 1gb

# Настройка connection pooling
export DATABASE_POOL_SIZE="20"
export DATABASE_MAX_OVERFLOW="30"
```

### 📊 **Scaling Configuration:**
```yaml
# docker-compose.production.yml
services:
  mcp-memory-server:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## 🎯 **PRODUCTION CHECKLIST**

### ✅ **Pre-Deployment:**
- [ ] Все environment variables настроены
- [ ] Docker и Docker Compose установлены
- [ ] .env файл создан (не в Git!)
- [ ] Firewall настроен
- [ ] SSL сертификаты готовы (для HTTPS)

### ✅ **Deployment:**
- [ ] `docker-compose up -d --build` выполнен успешно
- [ ] Все контейнеры запущены: `docker ps`
- [ ] Health check проходит: `curl http://localhost:8000/health`
- [ ] MCP endpoint доступен: `curl http://localhost:8000/mcp`
- [ ] Все 17 tools работают

### ✅ **Post-Deployment:**
- [ ] Мониторинг настроен
- [ ] Backup стратегия настроена
- [ ] Логи ротируются
- [ ] Performance metrics собираются
- [ ] Recovery procedures протестированы

### ✅ **Integration Testing:**
- [ ] Cursor MCP integration работает
- [ ] Все 17 tools доступны через MCP
- [ ] Error handling работает корректно
- [ ] Performance приемлемая

---

## 🎉 **ЗАКЛЮЧЕНИЕ**

После выполнения всех шагов у вас будет **production-ready Enterprise MCP-Mem0 Server** с 17 полнофункциональными инструментами памяти, готовыми к интеграции с AI агентами через Model Context Protocol.

**Система поддерживает:**
- ✅ Hybrid Graph + Vector Memory
- ✅ Redis синхронизация и кэширование  
- ✅ Enterprise error handling и monitoring
- ✅ FastAPI-MCP автоматическая генерация tools
- ✅ Production deployment с Docker
- ✅ Comprehensive logging и metrics
- ✅ Security best practices 