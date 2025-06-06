# MCP-Mem0 Project Structure

## Идеальная архитектура проекта

```
mcp-mem0/
├── 📁 src/                          # Основной код
│   ├── 🐍 main.py                   # Главный MCP сервер
│   ├── 🐍 fastapi_memory_server.py  # FastAPI память сервер
│   ├── 🐍 unified_memory_server.py  # Унифицированный сервер
│   ├── 🐍 graph_memory_upgrade.py   # Модуль графовой памяти
│   ├── 🐍 utils.py                  # Утилиты и хелперы
│   └── 🐍 __init__.py              # Инициализация пакета
│
├── 📁 tests/                        # Все тесты
│   ├── 📁 unit/                     # Юнит тесты
│   ├── 📁 integration/              # Интеграционные тесты
│   ├── 📁 fixtures/                 # Тестовые данные
│   ├── 🐍 test_mcp_tools.py        # Тесты MCP инструментов
│   └── 🐍 conftest.py              # Конфигурация pytest
│
├── 📁 docs/                         # Документация
│   ├── 📁 api/                      # API документация
│   ├── 📁 guides/                   # Руководства
│   ├── 📁 examples/                 # Примеры использования
│   └── 📄 README.md                 # Основная документация
│
├── 📁 config/                       # Конфигурации
│   ├── 🔧 development.env           # Разработка
│   ├── 🔧 production.env            # Продакшен
│   ├── 🔧 testing.env               # Тестирование
│   └── 📄 config.example.env        # Пример конфигурации
│
├── 📁 docker/                       # Docker конфигурации
│   ├── 🐳 Dockerfile.base           # Базовый образ
│   ├── 🐳 Dockerfile.dev            # Для разработки
│   ├── 🐳 Dockerfile.prod           # Для продакшена
│   ├── 🐳 docker-compose.dev.yml    # Разработка
│   ├── 🐳 docker-compose.prod.yml   # Продакшен
│   └── 🐳 docker-compose.test.yml   # Тестирование
│
├── 📁 scripts/                      # Скрипты автоматизации
│   ├── 🔧 setup.sh                  # Настройка окружения
│   ├── 🔧 build.sh                  # Сборка проекта
│   ├── 🔧 deploy.sh                 # Развертывание
│   └── 🔧 backup.sh                 # Резервное копирование
│
├── 📁 monitoring/                   # Мониторинг и метрики
│   ├── 📁 grafana/                  # Dashboards Grafana
│   ├── 📁 prometheus/               # Конфигурация Prometheus
│   └── 📁 logs/                     # Логи системы
│
├── 📁 examples/                     # Примеры использования
│   ├── 🐍 basic_usage.py           # Базовое использование
│   ├── 🐍 advanced_features.py     # Продвинутые функции
│   └── 📁 notebooks/               # Jupyter notebooks
│
├── 📁 tools/                        # Инструменты разработки
│   ├── 🐍 memory_inspector.py      # Инспектор памяти
│   ├── 🐍 graph_visualizer.py      # Визуализация графов
│   └── 🐍 performance_test.py      # Тесты производительности
│
├── 📄 Makefile                      # Система управления
├── 📄 pyproject.toml               # Конфигурация Python
├── 📄 requirements.txt             # Основные зависимости
├── 📄 requirements-dev.txt         # Зависимости разработки
├── 📄 README.md                    # Главная документация
├── 📄 CONTRIBUTING.md              # Руководство по вкладу
├── 📄 LICENSE                      # Лицензия
└── 📄 .env.example                 # Пример переменных окружения
```

## Модули системы

### 🧠 Основные компоненты

1. **Main MCP Server** (`src/main.py`)
   - Основной MCP сервер с всеми инструментами памяти
   - Обработка запросов и маршрутизация
   - Управление жизненным циклом

2. **Graph Memory** (`src/graph_memory_upgrade.py`)
   - Интеграция с Neo4j для графовых связей
   - Извлечение сущностей и отношений
   - Граф-ориентированный поиск

3. **Utils** (`src/utils.py`)
   - Вспомогательные функции
   - Обработка метаданных
   - Валидация и фильтрация

### 🗄️ Архитектура хранения

```mermaid
graph TB
    Client[MCP Client] --> Server[Memory Server]
    Server --> Vector[Supabase Vector Store]
    Server --> Graph[Neo4j Graph Store]
    Server --> Cache[Redis Cache]
    
    Vector --> Search[Semantic Search]
    Graph --> Relations[Entity Relations]
    Cache --> FastAccess[Fast Access]
```

### ⚙️ Режимы запуска

1. **Development** (`make dev`)
   - Локальный запуск без Docker
   - Быстрая итерация и отладка
   - Автоматическая перезагрузка

2. **Memory Only** (`make memory-only`)
   - Neo4j + PostgreSQL + Memory Server + Redis
   - Без мониторинга
   - Оптимально для большинства случаев

3. **Graph Only** (`make graph-only`)
   - Только Neo4j + Memory Server
   - Для работы исключительно с графами
   - Минимальные ресурсы

4. **Production** (`make prod`)
   - Полная конфигурация со всеми сервисами
   - Prometheus + Grafana мониторинг
   - Health checks и автовосстановление

5. **Simple** (`make simple`)
   - Базовая конфигурация
   - Для быстрого старта

### 🔧 Переменные окружения

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Neo4j Configuration
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphmemory123

# PostgreSQL Configuration (альтернатива Supabase)
POSTGRES_URL=postgresql://postgres:postgres123@localhost:5432/unified_memory

# Supabase Configuration (если используете вместо локального PostgreSQL)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Server Configuration
MEMORY_SERVER_PORT=8051
LOG_LEVEL=info
ENVIRONMENT=development
```

### 🏗️ Принципы организации

1. **Separation of Concerns**
   - Каждый модуль имеет четкую ответственность
   - Минимальная связанность между компонентами
   - Максимальная когезия внутри модулей

2. **Configuration Management**
   - Все конфигурации в отдельных файлах
   - Переменные окружения для деплоя
   - Валидация конфигураций при старте

3. **Testing Strategy**
   - Юнит тесты для каждого модуля
   - Интеграционные тесты для API
   - E2E тесты для полных сценариев

4. **Documentation**
   - Каждый модуль документирован
   - API документация автогенерируется
   - Примеры использования для всех функций

### 🚀 Быстрый старт

```bash
# 1. Клонировать и установить
git clone <repo>
cd mcp-mem0
make install

# 2. Настроить окружение
cp .env.example .env
# Отредактировать .env файл

# 3. Запустить систему
make memory-only

# 4. Проверить здоровье
make health

# 5. Посмотреть справку
make help
```

### 📊 Мониторинг и наблюдаемость

- **Логи**: Структурированное логирование в JSON формате
- **Метрики**: Prometheus метрики для производительности
- **Traces**: Распределенная трассировка запросов
- **Health Checks**: Автоматические проверки здоровья сервисов

### 🔒 Безопасность

- **Authentication**: Интеграция с FastAPI security
- **Rate Limiting**: Ограничение частоты запросов
- **Input Validation**: Валидация всех входных данных
- **Secure Defaults**: Безопасные настройки по умолчанию 