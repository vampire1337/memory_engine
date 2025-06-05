#!/usr/bin/env python3
"""
Тестирование FastAPI-MCP сервера памяти
Проверка всех 11 инструментов через REST API
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TEST_PROJECT_ID = "fastapi-mcp-test"

def test_api_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Тестирование API эндпоинта"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Неподдерживаемый метод: {method}"}
        
        response.raise_for_status()
        return {
            "status": "success",
            "status_code": response.status_code,
            "data": response.json()
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    """Основная функция тестирования"""
    
    print("🧪 ТЕСТИРОВАНИЕ FastAPI-MCP СЕРВЕРА ПАМЯТИ")
    print("=" * 60)
    print(f"🎯 Базовый URL: {BASE_URL}")
    print(f"📝 Тестовый проект: {TEST_PROJECT_ID}")
    print(f"⏰ Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Тесты для всех 11 инструментов
    tests = [
        {
            "name": "1. Health Check",
            "method": "GET",
            "endpoint": "/",
            "data": None
        },
        {
            "name": "2. Save Memory",
            "method": "POST", 
            "endpoint": "/memory/save",
            "data": {
                "text": f"Тестирование FastAPI-MCP сервера памяти в проекте {TEST_PROJECT_ID}. Дата: {datetime.now().isoformat()}"
            }
        },
        {
            "name": "3. Get All Memories",
            "method": "GET",
            "endpoint": "/memory/all",
            "data": None
        },
        {
            "name": "4. Search Memories",
            "method": "POST",
            "endpoint": "/memory/search", 
            "data": {
                "query": "FastAPI-MCP тестирование",
                "limit": 5
            }
        },
        {
            "name": "5. Save Verified Memory",
            "method": "POST",
            "endpoint": "/memory/save-verified",
            "data": {
                "content": "Проверенная информация о тестировании FastAPI-MCP сервера",
                "project_id": TEST_PROJECT_ID,
                "category": "testing",
                "confidence_level": 9,
                "source": "automated_test",
                "tags": "fastapi,mcp,testing,memory"
            }
        },
        {
            "name": "6. Get Accurate Context",
            "method": "POST", 
            "endpoint": "/memory/get-accurate-context",
            "data": {
                "query": "тестирование FastAPI",
                "project_id": TEST_PROJECT_ID,
                "min_confidence": 5,
                "limit": 3
            }
        },
        {
            "name": "7. Validate Project Context",
            "method": "POST",
            "endpoint": "/memory/validate-project-context",
            "data": {
                "project_id": TEST_PROJECT_ID
            }
        },
        {
            "name": "8. Save Project Milestone", 
            "method": "POST",
            "endpoint": "/memory/save-milestone",
            "data": {
                "project_id": TEST_PROJECT_ID,
                "milestone_type": "testing_complete",
                "content": "Завершено тестирование FastAPI-MCP сервера памяти", 
                "impact_level": 8,
                "tags": "milestone,testing,completion"
            }
        },
        {
            "name": "9. Get Current Project State",
            "method": "POST",
            "endpoint": "/memory/get-project-state",
            "data": {
                "project_id": TEST_PROJECT_ID
            }
        },
        {
            "name": "10. Track Project Evolution",
            "method": "POST", 
            "endpoint": "/memory/track-evolution",
            "data": {
                "project_id": TEST_PROJECT_ID,
                "category": "testing"
            }
        },
        {
            "name": "11. Audit Memory Quality",
            "method": "POST",
            "endpoint": "/memory/audit-quality", 
            "data": {
                "project_id": TEST_PROJECT_ID
            }
        },
        {
            "name": "12. Resolve Context Conflict",
            "method": "POST",
            "endpoint": "/memory/resolve-conflict",
            "data": {
                "conflicting_memory_ids": "test-id-1,test-id-2",
                "correct_content": "FastAPI-MCP сервер работает стабильно и без ошибок",
                "resolution_reason": "Тестовое разрешение конфликта для проверки функциональности"
            }
        }
    ]
    
    # Выполняем тесты
    results = []
    success_count = 0
    
    for i, test in enumerate(tests, 1):
        print(f"🔄 {test['name']}...")
        
        result = test_api_endpoint(test['method'], test['endpoint'], test['data'])
        results.append({
            "test": test['name'],
            "result": result
        })
        
        if result['status'] == 'success':
            print(f"   ✅ Успешно (код: {result['status_code']})")
            success_count += 1
        else:
            print(f"   ❌ Ошибка: {result['error']}")
        
        # Небольшая пауза между тестами
        time.sleep(0.5)
    
    # Результаты тестирования
    print()
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"✅ Успешно: {success_count}/{len(tests)} тестов")
    print(f"❌ Неудачно: {len(tests) - success_count}/{len(tests)} тестов")
    print(f"📈 Процент успеха: {(success_count/len(tests)*100):.1f}%")
    
    if success_count == len(tests):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🚀 FastAPI-MCP сервер полностью функционален")
    else:
        print(f"\n⚠️  {len(tests) - success_count} тестов не прошли")
        print("🔧 Проверьте логи сервера для диагностики")
    
    # Проверяем MCP эндпоинт
    print("\n🔧 ПРОВЕРКА MCP ЭНДПОИНТА")
    print("-" * 30)
    mcp_result = test_api_endpoint("GET", "/mcp", None)
    if mcp_result['status'] == 'success':
        print("✅ MCP эндпоинт доступен")
        print(f"🌐 MCP URL: {BASE_URL}/mcp")
    else:
        print("❌ MCP эндпоинт недоступен")
    
    print()
    print("📝 Детальные результаты:")
    for result in results:
        status_emoji = "✅" if result['result']['status'] == 'success' else "❌"
        print(f"  {status_emoji} {result['test']}")
    
    print()
    print("🔗 Полезные ссылки:")
    print(f"  📖 Swagger UI: {BASE_URL}/docs")
    print(f"  🔧 MCP Server: {BASE_URL}/mcp")
    print(f"  ❤️  Health Check: {BASE_URL}/")

if __name__ == "__main__":
    main() 