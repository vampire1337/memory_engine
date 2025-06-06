#!/bin/bash

# Setup Neo4j для Graph Memory
echo "🚀 Настройка Neo4j для Graph Memory..."

# Создаем директорию для данных Neo4j
mkdir -p ./neo4j/data
mkdir -p ./neo4j/logs
mkdir -p ./neo4j/import
mkdir -p ./neo4j/plugins

# Запускаем Neo4j в Docker
echo "📦 Запуск Neo4j контейнера..."
docker run -d \
    --name neo4j-graph-memory \
    -p 7474:7474 \
    -p 7687:7687 \
    -v $(pwd)/neo4j/data:/data \
    -v $(pwd)/neo4j/logs:/logs \
    -v $(pwd)/neo4j/import:/var/lib/neo4j/import \
    -v $(pwd)/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/graphmemory123 \
    --env NEO4J_PLUGINS='["apoc"]' \
    --env NEO4J_dbms_security_procedures_unrestricted=apoc.* \
    --env NEO4J_dbms_security_procedures_allowlist=apoc.* \
    neo4j:5.15

echo "⏳ Ожидание запуска Neo4j..."
sleep 30

# Проверяем статус
echo "🔍 Проверка статуса Neo4j..."
docker logs neo4j-graph-memory

echo "✅ Neo4j настроен!"
echo "🌐 Web интерфейс: http://localhost:7474"
echo "🔌 Bolt подключение: bolt://localhost:7687"
echo "👤 Логин: neo4j"
echo "🔑 Пароль: graphmemory123"

# Создаем .env файл с настройками
echo "📝 Создание .env настроек..."
cat >> .env << EOF

# Neo4j Graph Store Configuration
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphmemory123
EOF

echo "🎯 Готово! Теперь можно запускать Graph Memory сервер." 