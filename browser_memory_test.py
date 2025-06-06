#!/usr/bin/env python3
"""
Тестирование системы памяти MCP-Mem0 через браузер
Проверяет Neo4j Browser, Supabase Dashboard, и Memory Server
"""

import time
import json
from datetime import datetime

def test_memory_system_browser():
    """
    Тестирование системы памяти через браузерные интерфейсы
    """
    
    print("🌐 ТЕСТИРОВАНИЕ СИСТЕМЫ ПАМЯТИ ЧЕРЕЗ БРАУЗЕР")
    print("=" * 60)
    
    # URLs для проверки
    urls_to_check = {
        "Memory Server Health": "http://localhost:8051/health",
        "Memory Server Docs": "http://localhost:8051/docs", 
        "Neo4j Browser": "http://localhost:7474",
        "Supabase Dashboard": "https://supabase.com/dashboard/project/your-project",
        "Grafana (если запущен)": "http://localhost:3000",
        "Prometheus (если запущен)": "http://localhost:9090"
    }
    
    print("\n🔗 ССЫЛКИ ДЛЯ ПРОВЕРКИ:")
    print("-" * 30)
    for name, url in urls_to_check.items():
        print(f"📊 {name}: {url}")
    
    # Neo4j запросы для проверки
    neo4j_queries = [
        {
            "name": "Все узлы и связи",
            "query": "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25"
        },
        {
            "name": "Статистика базы данных", 
            "query": "CALL db.stats.retrieve('GRAPH COUNTS')"
        },
        {
            "name": "Схема базы данных",
            "query": "CALL db.schema.visualization()"
        },
        {
            "name": "Поиск пользователей",
            "query": "MATCH (n:Person) RETURN n LIMIT 10"
        },
        {
            "name": "Поиск технологий",
            "query": "MATCH (n:Technology) RETURN n LIMIT 10"
        },
        {
            "name": "Все типы связей",
            "query": "MATCH ()-[r]->() RETURN DISTINCT type(r) as relationship_type"
        }
    ]
    
    print(f"\n🕸️ NEO4J ЗАПРОСЫ ДЛЯ ПРОВЕРКИ (вставить в Neo4j Browser):")
    print("-" * 60)
    for i, query_info in enumerate(neo4j_queries, 1):
        print(f"\n{i}. {query_info['name']}:")
        print(f"   {query_info['query']}")
    
    # Supabase SQL запросы
    supabase_queries = [
        {
            "name": "Все воспоминания",
            "query": "SELECT * FROM memories ORDER BY created_at DESC LIMIT 10;"
        },
        {
            "name": "Статистика воспоминаний",
            "query": "SELECT COUNT(*) as total_memories, COUNT(DISTINCT user_id) as unique_users FROM memories;"
        },
        {
            "name": "Поиск по контенту",
            "query": "SELECT id, content, created_at FROM memories WHERE content ILIKE '%Python%' LIMIT 5;"
        },
        {
            "name": "Анализ метаданных",
            "query": "SELECT metadata->>'category' as category, COUNT(*) FROM memories GROUP BY metadata->>'category';"
        }
    ]
    
    print(f"\n💾 SUPABASE SQL ЗАПРОСЫ ДЛЯ ПРОВЕРКИ:")
    print("-" * 50)
    for i, query_info in enumerate(supabase_queries, 1):
        print(f"\n{i}. {query_info['name']}:")
        print(f"   {query_info['query']}")
    
    # Тестовые данные для проверки
    test_data = [
        {
            "type": "personal_info",
            "content": "Меня зовут Алексей, я Python разработчик из Москвы. Специализируюсь на backend разработке и системах машинного обучения.",
            "expected_neo4j": "Person(Алексей) -[WORKS_WITH]-> Technology(Python)",
            "expected_supabase": "Embedding вектор в таблице memories"
        },
        {
            "type": "tech_stack", 
            "content": "Мой основной стек: FastAPI + PostgreSQL + Redis + Docker. Для ML использую PyTorch и scikit-learn.",
            "expected_neo4j": "Technology узлы и USED_WITH связи",
            "expected_supabase": "Высокое сходство с tech-related queries"
        },
        {
            "type": "current_project",
            "content": "Работаю над MCP-Mem0 - системой долговременной памяти для AI агентов с интеграцией Neo4j и Supabase.",
            "expected_neo4j": "Project(MCP-Mem0) связанный с технологиями",
            "expected_supabase": "Семантическая связь с AI и memory топиками"
        }
    ]
    
    print(f"\n🧪 ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ПРОВЕРКИ:")
    print("-" * 40)
    for i, test in enumerate(test_data, 1):
        print(f"\n{i}. Тип: {test['type']}")
        print(f"   Контент: {test['content']}")
        print(f"   Neo4j ожидание: {test['expected_neo4j']}")
        print(f"   Supabase ожидание: {test['expected_supabase']}")
    
    # Пошаговые инструкции
    steps = [
        "1. 🚀 Запустить систему: make memory-only (или docker-compose up)",
        "2. 🔍 Проверить здоровье: http://localhost:8051/health",
        "3. 📝 Сохранить тестовые данные через MCP инструменты",
        "4. 🕸️ Открыть Neo4j Browser: http://localhost:7474",
        "5. 🔑 Войти в Neo4j (neo4j/graphmemory123)",
        "6. 📊 Выполнить Neo4j запросы выше",
        "7. 💾 Проверить Supabase Dashboard",
        "8. 🔍 Выполнить SQL запросы в Supabase",
        "9. 🔎 Протестировать поиск через MCP инструменты",
        "10. 📈 Проанализировать производительность"
    ]
    
    print(f"\n📋 ПОШАГОВЫЕ ИНСТРУКЦИИ:")
    print("-" * 30)
    for step in steps:
        print(f"   {step}")
    
    # Ожидаемые результаты
    expected_results = {
        "Neo4j Graph": [
            "Узлы типа Person, Technology, Project",
            "Связи типа WORKS_WITH, PREFERS, USES",
            "Кластеры связанных технологий",
            "Путь от пользователя к проектам"
        ],
        "Supabase Vector": [
            "Таблица memories с embedding векторами", 
            "Метаданные с project_id, category, tags",
            "Семантический поиск работает корректно",
            "Высокое сходство для релевантных запросов"
        ],
        "Memory Server": [
            "API endpoints отвечают корректно",
            "Сохранение работает в обе базы",
            "Поиск возвращает релевантные результаты",
            "Метаданные корректно обрабатываются"
        ]
    }
    
    print(f"\n✅ ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
    print("-" * 30)
    for component, results in expected_results.items():
        print(f"\n🔧 {component}:")
        for result in results:
            print(f"   ✓ {result}")
    
    # Возможные проблемы
    potential_issues = [
        "❌ Neo4j не отвечает - проверить Docker контейнер",
        "❌ Supabase connection timeout - проверить API ключи", 
        "❌ Memory Server 500 error - проверить логи",
        "❌ Поиск не находит данные - проверить индексацию",
        "❌ Граф пустой - проверить извлечение сущностей",
        "❌ Дублирующиеся узлы - настроить дедупликацию"
    ]
    
    print(f"\n⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ:")
    print("-" * 30)
    for issue in potential_issues:
        print(f"   {issue}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "test_type": "browser_testing",
        "urls": urls_to_check,
        "neo4j_queries": neo4j_queries,
        "supabase_queries": supabase_queries,
        "test_data": test_data,
        "expected_results": expected_results
    }

if __name__ == "__main__":
    results = test_memory_system_browser()
    
    print(f"\n💾 РЕЗУЛЬТАТЫ СОХРАНЕНЫ В: browser_test_results.json")
    with open("browser_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 ГОТОВО К ТЕСТИРОВАНИЮ!")
    print("Следуйте пошаговым инструкциям выше для полной проверки системы.") 