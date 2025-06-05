#!/bin/bash

# Unified Memory System - Startup Script
# Профессиональный запуск всей системы памяти

set -e

echo "🚀 UNIFIED MEMORY SYSTEM - STARTUP"
echo "=================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker для продолжения."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не найден. Установите Docker Compose для продолжения."
    exit 1
fi

# Проверяем .env файл
if [ ! -f .env ]; then
    echo "⚠️ .env файл не найден. Создаем базовый файл..."
    cat > .env << EOL
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j Configuration (автоматически настроится Docker)
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphmemory123

# Server Configuration
MEMORY_SERVER_PORT=8051
LOG_LEVEL=info
ENVIRONMENT=development
EOL
    echo "📝 Создан базовый .env файл. Отредактируйте OPENAI_API_KEY!"
fi

# Выбор режима запуска
echo ""
echo "Выберите режим запуска:"
echo "1) Базовая система (Neo4j + Memory Server)"
echo "2) Полная система (Neo4j + PostgreSQL + Memory Server + Redis)"
echo "3) С мониторингом (Полная + Prometheus + Grafana)"
echo "4) Только тестирование (локальный запуск без Docker)"

read -p "Введите номер (1-4): " choice

case $choice in
    1)
        echo "🔧 Запуск базовой системы..."
        docker-compose -f docker-compose.unified.yml up -d neo4j memory-server
        ;;
    2)
        echo "🔧 Запуск полной системы..."
        docker-compose -f docker-compose.unified.yml up -d
        ;;
    3)
        echo "🔧 Запуск с мониторингом..."
        docker-compose -f docker-compose.unified.yml --profile monitoring up -d
        ;;
    4)
        echo "🔧 Локальный запуск для тестирования..."
        # Запускаем только Neo4j в Docker, Memory Server локально
        docker-compose -f docker-compose.unified.yml up -d neo4j
        echo "⏳ Ждем запуска Neo4j..."
        sleep 10
        
        # Устанавливаем зависимости если нужно
        if [ ! -d ".venv" ]; then
            echo "📦 Создаем виртуальное окружение..."
            python -m venv .venv
            source .venv/bin/activate
            pip install -r requirements.txt -r requirements_graph.txt
        else
            source .venv/bin/activate
        fi
        
        echo "🚀 Запуск локального Memory Server..."
        export NEO4J_URL="bolt://localhost:7687"
        export NEO4J_PASSWORD="graphmemory123"
        python src/unified_memory_server.py
        ;;
    *)
        echo "❌ Неверный выбор. Попробуйте снова."
        exit 1
        ;;
esac

if [ $choice -ne 4 ]; then
    # Ждем запуска сервисов
    echo "⏳ Ждем запуска сервисов..."
    sleep 15

    # Проверяем статус
    echo ""
    echo "📊 СТАТУС СЕРВИСОВ:"
    docker-compose -f docker-compose.unified.yml ps

    echo ""
    echo "✅ UNIFIED MEMORY SYSTEM ГОТОВА!"
    echo "================================"
    echo "🌐 Memory Server: http://localhost:8051"
    echo "🔧 MCP Endpoint: http://localhost:8051/mcp"
    echo "📚 API Docs: http://localhost:8051/docs"
    echo "❤️ Health Check: http://localhost:8051/health"
    echo "🗄️ Neo4j Browser: http://localhost:7474"
    
    if [ $choice -eq 3 ]; then
        echo "📈 Prometheus: http://localhost:9090"
        echo "📊 Grafana: http://localhost:3000 (admin/admin123)"
    fi
    
    echo ""
    echo "🔗 Подключение к MCP:"
    echo 'Добавьте в Claude Desktop/Cursor config:'
    echo '{'
    echo '  "mcpServers": {'
    echo '    "unified-memory": {'
    echo '      "url": "http://localhost:8051/mcp"'
    echo '    }'
    echo '  }'
    echo '}'
fi

echo ""
echo "🎯 Система готова к работе! 15 инструментов памяти доступны." 