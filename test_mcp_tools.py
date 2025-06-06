#!/usr/bin/env python3
"""
Быстрый тест MCP инструментов
Проверяем что все 15 инструментов работают через HTTP API
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Список всех инструментов для тестирования
TOOLS_TO_TEST = [
    # Базовые инструменты (11)
    {"endpoint": "/memory/save", "method": "POST", "data": {"content": "Тест MCP сервера", "user_id": "test_user"}},
    {"endpoint": "/memory/search", "method": "POST", "data": {"query": "тест", "user_id": "test_user"}},
    {"endpoint": "/memory/get-all", "method": "POST", "data": {"user_id": "test_user"}},
    {"endpoint": "/memory/save-verified", "method": "POST", "data": {"content": "Проверенная информация", "user_id": "test_user"}},
    {"endpoint": "/memory/get-context", "method": "POST", "data": {"query": "контекст", "user_id": "test_user"}},
    {"endpoint": "/memory/validate-project-context", "method": "POST", "data": {"query": "проект", "user_id": "test_user"}},
    {"endpoint": "/memory/resolve-conflict", "method": "POST", "data": {"query": "конфликт", "user_id": "test_user"}},
    {"endpoint": "/memory/audit-quality", "method": "POST", "data": {"user_id": "test_user"}},
    {"endpoint": "/memory/save-milestone", "method": "POST", "data": {"milestone_name": "Тест", "description": "Тестовый milestone", "project_id": "test_project", "user_id": "test_user"}},
    {"endpoint": "/memory/get-project-state", "method": "POST", "data": {"query": "состояние", "user_id": "test_user"}},
    {"endpoint": "/memory/track-evolution", "method": "POST", "data": {"query": "эволюция", "user_id": "test_user"}},
    
    # Графовые инструменты (4)
    {"endpoint": "/graph/save-memory", "method": "POST", "data": {"content": "Граф тест", "user_id": "test_user"}},
    {"endpoint": "/graph/search", "method": "POST", "data": {"query": "граф", "user_id": "test_user"}},
    {"endpoint": "/graph/entity-relationships", "method": "POST", "data": {"entity_name": "Python", "user_id": "test_user"}},
    {"endpoint": "/graph/status", "method": "GET", "data": None}
]

async def test_tool(session, tool):
    """Тестировать один инструмент"""
    url = f"http://localhost:8051{tool['endpoint']}"
    
    try:
        if tool['method'] == 'GET':
            async with session.get(url) as response:
                result = await response.json()
                return {
                    "endpoint": tool['endpoint'],
                    "status": "✅ SUCCESS" if response.status == 200 else f"❌ ERROR {response.status}",
                    "response_code": response.status,
                    "result": result
                }
        else:
            async with session.post(url, json=tool['data']) as response:
                result = await response.json()
                return {
                    "endpoint": tool['endpoint'],
                    "status": "✅ SUCCESS" if response.status == 200 else f"❌ ERROR {response.status}",
                    "response_code": response.status,
                    "result": result
                }
    except Exception as e:
        return {
            "endpoint": tool['endpoint'],
            "status": f"❌ EXCEPTION: {str(e)}",
            "response_code": 0,
            "result": None
        }

async def main():
    """Главная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ MCP ИНСТРУМЕНТОВ")
    print("=" * 50)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Всего инструментов: {len(TOOLS_TO_TEST)}")
    print("=" * 50)
    
    results = []
    success_count = 0
    
    async with aiohttp.ClientSession() as session:
        # Тестируем все инструменты параллельно
        tasks = [test_tool(session, tool) for tool in TOOLS_TO_TEST]
        results = await asyncio.gather(*tasks)
    
    # Выводим результаты
    for result in results:
        print(f"{result['status']:<15} {result['endpoint']}")
        if result['response_code'] == 200:
            success_count += 1
    
    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТ: {success_count}/{len(TOOLS_TO_TEST)} инструментов работает")
    print(f"📈 Процент успеха: {(success_count/len(TOOLS_TO_TEST)*100):.1f}%")
    
    if success_count == len(TOOLS_TO_TEST):
        print("🎉 ВСЕ ИНСТРУМЕНТЫ РАБОТАЮТ! MCP СЕРВЕР ГОТОВ К ПРОДАКШЕНУ!")
    else:
        print("⚠️ Есть неработающие инструменты, требуется доработка")
    
    return success_count == len(TOOLS_TO_TEST)

if __name__ == "__main__":
    asyncio.run(main()) 