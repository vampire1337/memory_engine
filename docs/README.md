# **Memory Engine (Mem0)**

<div align="center">

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![MCP](https://img.shields.io/badge/MCP-Latest-purple.svg)
![Mem0](https://img.shields.io/badge/Mem0-1.1+-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Production](https://img.shields.io/badge/Production-Ready-green.svg)

**17 Production-Ready Memory Tools для AI Agents через Model Context Protocol**

</div>

---

## **ЧТО ЭТО ТАКОЕ?**

**Enterprise MCP-Mem0 Server** - это production-ready система управления памятью для AI агентов, предоставляющая **17 enterprise tools** через Model Context Protocol (MCP).

###  **Ключевые особенности:**
-  **FastAPI-MCP Integration** - автоматическая генерация MCP tools из FastAPI endpoints
-  **Hybrid Memory System** - Graph (Memgraph) + Vector (Supabase) память одновременно
-  **Redis Synchronization** - события, кэширование и distributed locking
-  **Enterprise Grade** - comprehensive error handling, monitoring, logging
-  **Background Tasks** - асинхронная обработка heavy operations
-  **Production Ready** - Docker, security, scalability

---

##  **17 ENTERPRISE TOOLS**

###  **Memory Tools (11):**
1. **save_memory** - сохранение памяти с Graph+Vector processing
2. **search_memories** - hybrid поиск с Redis кэшированием
3. **get_all_memories** - получение всех воспоминаний пользователя
4. **save_verified_memory** - сохранение проверенной информации
5. **get_accurate_context** - получение релевантного контекста
6. **validate_project_context** - валидация проектного контекста
7. **resolve_context_conflict** - разрешение противоречий в памяти
8. **audit_memory_quality** - анализ качества памяти
9. **save_project_milestone** - сохранение milestone проекта
10. **get_current_project_state** - текущее состояние проекта
11. **track_project_evolution** - эволюция проекта во времени

###  **Graph Memory Tools (4):**
12. **save_graph_memory** - сохранение с извлечением сущностей и связей
13. **search_graph_memory** - поиск с графовым контекстом
14. **get_entity_relationships** - анализ связей сущности
15. **graph_status** - статус графовой системы

### ⚙ **System Tools (2):**
16. **health** - комплексная проверка здоровья системы
17. **root** - информация о системе и endpoints

---

##  **БЫСТРЫЙ СТАРТ**

###  **Установка и настройка:**
```bash
# Клонирование репозитория
git clone https://github.com/your-repo/mcp-mem0
cd mcp-mem0

# Создание environment файла
cat > .env << 'EOF'
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
NEO4J_URL=bolt://memgraph:7687
NEO4J_USERNAME=memgraph
NEO4J_PASSWORD=graphmemory123
REDIS_URL=redis://:redispassword@redis:6379/0
EOF
```

### **Запуск production системы:**
```bash
# Сборка и запуск всех сервисов
docker-compose -f docker-compose.production.yml up -d --build

# Проверка состояния
docker-compose -f docker-compose.production.yml ps

# Проверка здоровья
curl http://localhost:8000/health
```

### **Тестирование MCP tools:**
```bash
# Сохранение памяти
curl -X POST "http://localhost:8000/memory/save" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Пользователь Alex предпочитает Python",
    "user_id": "test_user"
  }'

# Поиск памяти
curl -X POST "http://localhost:8000/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "предпочтения программирования",
    "user_id": "test_user"
  }'
```

---

## **ИНТЕГРАЦИЯ С CURSOR**

### **Конфигурация MCP:**
```json
{
  "mcpServers": {
    "mcp-mem0-enterprise": {
      "url": "http://localhost:8000/mcp",
      "name": "Enterprise Memory System",
      "description": "17 production-ready memory tools"
    }
  }
}
```

###  **Использование в Cursor:**
```
@mcp-mem0-enterprise.save_memory content="Пользователь любит Python" user_id="dev_alex"
@mcp-mem0-enterprise.search_memories query="языки программирования" user_id="dev_alex"
@mcp-mem0-enterprise.save_graph_memory content="Alex работает с John над проектом API"
```

---

##  **АРХИТЕКТУРА СИСТЕМЫ**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │  FastAPI-MCP    │    │   Memory        │
│   (Cursor)      │◄──►│   Server        │◄──►│   Client        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis         │    │   Mem0 v1.1     │
                       │   (Events &     │    │   (Graph +      │
                       │    Cache)       │    │    Vector)      │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                               ┌────────┴────────┐
                                               ▼                 ▼
                                    ┌─────────────────┐ ┌─────────────────┐
                                    │   Memgraph      │ │   Supabase      │
                                    │   (Graph)       │ │   (Vector)      │
                                    └─────────────────┘ └─────────────────┘
```

###  **Data Flow:**
1. **AI Agent** вызывает MCP tool
2. **FastAPI-MCP** автоматически генерирует tool из endpoint
3. **Memory Client** обрабатывает запрос через Mem0
4. **Mem0** сохраняет в Graph (Memgraph) и Vector (Supabase) одновременно
5. **Redis** обеспечивает синхронизацию и кэширование
6. **Response** возвращается через MCP обратно к AI Agent

---

##  **СТРУКТУРА ПРОЕКТА**

```
mcp-mem0/
├──  Dockerfile                    # Production multi-stage build
├──  docker-compose.production.yml # Production deployment
├──  requirements.txt              # Python dependencies
├──  pyproject.toml               # Project configuration
├── .env.example                 # Environment template
│
├──  src/                         # Source code
│   ├──  fastapi_mcp_server.py   # Main MCP server (17 tools)
│   ├──  memory_client.py         # Enterprise memory client
│   ├──  redis_service.py         # Redis integration
│   ├──  utils.py                # Utilities
│   └──  __init__.py              # Package init
│
├──  docs/                        # Documentation
│   ├──  COMPREHENSIVE_TOOLS_GUIDE.md  # All 17 tools detailed
│   ├──  DEPLOYMENT_GUIDE.md           # Production deployment
│   ├── 🏗 ENTERPRISE_ARCHITECTURE.md   # Architecture overview
│   └──  IMPLEMENTATION_LOG.md         # Development history
│
└──  monitoring/                  # Monitoring & logs
    ├──  logs/                   # Application logs
    └──  backups/                # Data backups
```

---

##  **ТЕХНИЧЕСКИЙ СТЕК**

###  **Backend:**
- **FastAPI 0.104+** - modern web framework
- **FastAPI-MCP** - automatic MCP tools generation
- **Mem0 1.1+** - hybrid memory system
- **Redis** - caching & synchronization
- **Pydantic** - data validation

###  **Storage:**
- **Supabase PostgreSQL** - vector embeddings storage
- **Memgraph** - graph relationships storage
- **Redis** - distributed cache

###  **Infrastructure:**
- **Docker** - containerization
- **Docker Compose** - multi-service orchestration
- **Uvicorn** - ASGI server
- **Multi-stage builds** - optimized images

###  **Integrations:**
- **Model Context Protocol (MCP)** - AI agent communication
- **OpenAI API** - embeddings generation
- **Neo4j Driver** - graph database access

---

##  **FEATURES & CAPABILITIES**

###  **Memory Management:**
-  **Hybrid Storage** - Graph + Vector simultaneously
-  **Semantic Search** - embedding-based relevance
-  **Graph Traversal** - relationship-aware queries
-  **Context Validation** - quality assurance
-  **Conflict Resolution** - contradiction handling

###  **Real-time Synchronization:**
-  **Redis Events** - cross-component communication
-  **Background Tasks** - non-blocking operations
-  **Distributed Locking** - consistency guarantees
-  **Cache Management** - intelligent TTL policies

###  **Enterprise Features:**
-  **Multi-tenancy** - user/agent/session isolation
-  **Error Recovery** - comprehensive exception handling
-  **Monitoring** - metrics collection & health checks
-  **Logging** - structured logging with correlation IDs
-  **Security** - input validation & sanitization

###  **Production Readiness:**
-  **Docker Deployment** - containerized architecture
-  **Health Checks** - automated monitoring
-  **Graceful Shutdown** - proper resource cleanup
-  **Resource Limits** - controlled resource usage
-  **Non-root Execution** - security best practices

---

##  **ДОКУМЕНТАЦИЯ**

###  **Основные руководства:**
- **[ COMPREHENSIVE_TOOLS_GUIDE.md](COMPREHENSIVE_TOOLS_GUIDE.md)** - подробное описание всех 17 tools
- **[ DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - полное руководство по development
- **[ ENTERPRISE_ARCHITECTURE.md](ENTERPRISE_ARCHITECTURE.md)** - архитектурный обзор
- **[ IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)** - история развития проекта

### **API Documentation:**
- **OpenAPI Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **MCP Endpoint:** `http://localhost:8000/mcp`
- **Health Check:** `http://localhost:8000/health`

---

##  **ТЕСТИРОВАНИЕ**

###  **Manual Testing:**
```bash
# HTTP API Testing
curl -X POST "http://localhost:8000/memory/save" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test memory", "user_id": "test"}'

# MCP Inspector
npx @modelcontextprotocol/inspector
# URL: http://localhost:8000/mcp
```

### **Cursor Testing:**
```
@mcp-mem0-enterprise.save_memory content="Test" user_id="test"
@mcp-mem0-enterprise.search_memories query="test" user_id="test"
@mcp-mem0-enterprise.health
```

###  **Automated Testing:**
```bash
# Health check
curl http://localhost:8000/health

# All endpoints test
bash test_all_tools.sh
```

---

##  **TROUBLESHOOTING**

###  **Общие проблемы:**

####  **Connection Issues:**
```bash
# Database
echo $DATABASE_URL  # Проверить порт 5432 (не 6543!)

# Redis
docker exec redis redis-cli ping

# Memgraph
docker exec memgraph mgconsole
```

####  **Docker Issues:**
```bash
# Rebuild containers
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up --build -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f
```

####  **MCP Issues:**
```bash
# Check MCP endpoint
curl http://localhost:8000/mcp

# Restart MCP server
docker-compose -f docker-compose.production.yml restart mcp-memory-server
```

---

##  **CONTRIBUTING**

###  **Development Workflow:**
1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Code review & merge

###  **Code Standards:**
- **Python 3.11+** with type hints
- **Black** code formatting
- **Pylint** code quality
- **Pytest** for testing
- **Docker** for deployment

---

##  **LICENSE**

MIT License - см. [LICENSE](LICENSE) файл для подробностей.

---

##  **ACKNOWLEDGMENTS**

- **[FastAPI-MCP](https://github.com/tadata-ru/fastapi-mcp)** - MCP integration framework
- **[Mem0](https://mem0.ai/)** - AI memory platform
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - standardized AI-app communication
- **[Memgraph](https://memgraph.com/)** - real-time graph database
- **[Supabase](https://supabase.io/)** - open source Firebase alternative

---

<div align="center">

* Enterprise MCP-Mem0 Server v2.0**

*Production-ready Memory System for AI Agents*

**[🚀 Get Started](DEPLOYMENT_GUIDE.md) | [📖 Documentation](COMPREHENSIVE_TOOLS_GUIDE.md) | [🏗️ Architecture](ENTERPRISE_ARCHITECTURE.md)**

</div>
