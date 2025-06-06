# MCP-Mem0 - Production Memory System
# Управление различными конфигурациями памяти

.PHONY: help install dev prod test clean logs status health
.DEFAULT_GOAL := help

# Переменные
COMPOSE_FILE_UNIFIED = docker-compose.unified.yml
COMPOSE_FILE_SIMPLE = docker-compose.yml
SERVER_PORT = 8051
PYTHON = python3
PIP = pip3

# Цвета для вывода
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)MCP-Mem0 Memory System - Production Ready$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(BLUE)🚀 РЕЖИМЫ ЗАПУСКА:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)📋 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:$(NC)"
	@echo "  make install     # Установить зависимости"
	@echo "  make dev        # Запуск для разработки"
	@echo "  make prod       # Полный продакшен режим"
	@echo "  make memory-only # Только память без мониторинга"
	@echo "  make health     # Проверить состояние системы"

install: ## Установить все зависимости
	@echo "$(GREEN)📦 Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements_graph.txt
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

dev: ## Запуск в режиме разработки (локально)
	@echo "$(GREEN)🛠️ Запуск в режиме разработки...$(NC)"
	$(PYTHON) src/main.py

prod: ## Полный продакшен со всеми сервисами
	@echo "$(GREEN)🚀 Запуск полной продакшен системы...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) --profile monitoring up -d
	@echo "$(GREEN)✅ Система запущена:$(NC)"
	@echo "  - Memory Server: http://localhost:$(SERVER_PORT)"
	@echo "  - Neo4j Browser: http://localhost:7474"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"

memory-only: ## Только система памяти без мониторинга
	@echo "$(GREEN)🧠 Запуск системы памяти...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) up -d neo4j postgres memory-server redis
	@echo "$(GREEN)✅ Система памяти запущена:$(NC)"
	@echo "  - Memory Server: http://localhost:$(SERVER_PORT)"
	@echo "  - Neo4j Browser: http://localhost:7474"

graph-only: ## Только граф память + сервер
	@echo "$(GREEN)🕸️ Запуск граф памяти...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) up -d neo4j memory-server
	@echo "$(GREEN)✅ Граф память запущена:$(NC)"
	@echo "  - Memory Server: http://localhost:$(SERVER_PORT)"
	@echo "  - Neo4j Browser: http://localhost:7474"

simple: ## Простой режим (основной Docker Compose)
	@echo "$(GREEN)⚡ Запуск простой конфигурации...$(NC)"
	docker-compose -f $(COMPOSE_FILE_SIMPLE) up -d
	@echo "$(GREEN)✅ Простая конфигурация запущена$(NC)"

stop: ## Остановить все сервисы
	@echo "$(YELLOW)⏹️ Остановка всех сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) down
	docker-compose -f $(COMPOSE_FILE_SIMPLE) down
	@echo "$(GREEN)✅ Все сервисы остановлены$(NC)"

clean: ## Очистить все данные и контейнеры
	@echo "$(RED)🧹 Очистка системы...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) down -v --remove-orphans
	docker-compose -f $(COMPOSE_FILE_SIMPLE) down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✅ Система очищена$(NC)"

restart: stop memory-only ## Перезапуск системы памяти

logs: ## Показать логи сервера памяти
	@echo "$(BLUE)📋 Логи Memory Server:$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) logs -f memory-server

logs-all: ## Показать логи всех сервисов
	@echo "$(BLUE)📋 Логи всех сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) logs -f

status: ## Показать статус всех сервисов
	@echo "$(BLUE)📊 Статус сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) ps

health: ## Проверить здоровье системы
	@echo "$(BLUE)🏥 Проверка здоровья системы...$(NC)"
	@echo ""
	@echo "$(YELLOW)Memory Server:$(NC)"
	@curl -s http://localhost:$(SERVER_PORT)/health | jq . || echo "$(RED)❌ Memory Server недоступен$(NC)"
	@echo ""
	@echo "$(YELLOW)Neo4j:$(NC)"
	@curl -s http://localhost:7474 > /dev/null && echo "$(GREEN)✅ Neo4j работает$(NC)" || echo "$(RED)❌ Neo4j недоступен$(NC)"
	@echo ""
	@echo "$(YELLOW)PostgreSQL:$(NC)"
	@docker exec unified-memory-postgres pg_isready -U postgres -d unified_memory > /dev/null 2>&1 && echo "$(GREEN)✅ PostgreSQL работает$(NC)" || echo "$(RED)❌ PostgreSQL недоступен$(NC)"

test: ## Запустить тесты системы
	@echo "$(GREEN)🧪 Запуск тестов...$(NC)"
	$(PYTHON) -m pytest tests/ -v
	$(PYTHON) test_mcp_tools.py

build: ## Собрать Docker образы
	@echo "$(GREEN)🔨 Сборка Docker образов...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) build

pull: ## Обновить Docker образы
	@echo "$(GREEN)⬇️ Обновление Docker образов...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) pull

backup: ## Создать бэкап данных
	@echo "$(GREEN)💾 Создание бэкапа...$(NC)"
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	docker exec unified-memory-neo4j neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/backup.dump
	docker cp unified-memory-neo4j:/var/lib/neo4j/backup.dump backups/$(shell date +%Y%m%d_%H%M%S)/
	docker exec unified-memory-postgres pg_dump -U postgres unified_memory > backups/$(shell date +%Y%m%d_%H%M%S)/postgres_backup.sql
	@echo "$(GREEN)✅ Бэкап создан в backups/$(shell date +%Y%m%d_%H%M%S)/$(NC)"

# Вспомогательные команды для разработки
format: ## Форматировать код
	@echo "$(GREEN)🎨 Форматирование кода...$(NC)"
	black src/
	isort src/

lint: ## Проверить код линтером
	@echo "$(GREEN)🔍 Проверка кода...$(NC)"
	flake8 src/
	mypy src/

docs: ## Генерировать документацию
	@echo "$(GREEN)📚 Генерация документации...$(NC)"
	cd docs && make html

# Команды для CI/CD
ci-test: install test lint ## Команды для CI pipeline

deploy: build prod health ## Полное развертывание

# Мониторинг
monitor: ## Запуск с мониторингом
	@echo "$(GREEN)📊 Запуск с мониторингом...$(NC)"
	docker-compose -f $(COMPOSE_FILE_UNIFIED) --profile monitoring up -d
	@echo "$(GREEN)✅ Мониторинг доступен на:$(NC)"
	@echo "  - Grafana: http://localhost:3000 (admin/admin123)"
	@echo "  - Prometheus: http://localhost:9090"

# Информация о системе
info: ## Показать информацию о системе
	@echo "$(GREEN)ℹ️ Информация о MCP-Mem0 System:$(NC)"
	@echo "=================================="
	@echo "$(YELLOW)Архитектура:$(NC)"
	@echo "  - 🧠 Neo4j Graph Database (графовые связи)"
	@echo "  - 🔍 PostgreSQL + pgvector (векторный поиск)" 
	@echo "  - ⚡ Redis (кэширование)"
	@echo "  - 🚀 FastAPI Memory Server"
	@echo "  - 📊 Prometheus + Grafana (мониторинг)"
	@echo ""
	@echo "$(YELLOW)Порты:$(NC)"
	@echo "  - 8051: Memory Server"
	@echo "  - 7474: Neo4j Browser"
	@echo "  - 5432: PostgreSQL"
	@echo "  - 6379: Redis"
	@echo "  - 3000: Grafana"
	@echo "  - 9090: Prometheus"

env-check: ## Проверить переменные окружения
	@echo "$(GREEN)🔧 Проверка переменных окружения...$(NC)"
	@echo "$(YELLOW)OPENAI_API_KEY:$(NC) $(if $(OPENAI_API_KEY),✅ установлен,❌ не установлен)"
	@echo "$(YELLOW)NEO4J_URL:$(NC) $(if $(NEO4J_URL),✅ установлен,⚠️ будет использован default)"
	@echo "$(YELLOW)POSTGRES_URL:$(NC) $(if $(POSTGRES_URL),✅ установлен,⚠️ будет использован default)" 