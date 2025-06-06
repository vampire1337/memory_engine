#!/usr/bin/env python3
"""
Comprehensive Test Suite для всех 15 MCP Memory Tools
Тестирует каждый инструмент с реальными примерами и сохраняет результаты
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List
import os
from dataclasses import dataclass

# Конфигурация
BASE_URL = "http://localhost:8051"
TEST_USER_ID = "heist1337"
TEST_PROJECT_ID = "mcp-mem0-prod"

@dataclass
class TestResult:
    tool_name: str
    endpoint: str
    success: bool
    response_data: Any
    execution_time: float
    error_message: str = None

class ComprehensiveMemoryTester:
    """Комплексный тестер всех инструментов памяти"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def log_result(self, result: TestResult):
        """Логировать результат теста"""
        status = "✅" if result.success else "❌"
        print(f"{status} {result.tool_name}: {result.execution_time:.2f}s")
        if not result.success and result.error_message:
            print(f"   Error: {result.error_message}")
        self.results.append(result)
    
    def test_get_endpoint(self, tool_name: str, endpoint: str) -> TestResult:
        """Тестировать GET endpoint"""
        start_time = time.time()
        
        try:
            response = self.session.get(f"{BASE_URL}{endpoint}", timeout=30)
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                return TestResult(
                    tool_name=tool_name,
                    endpoint=endpoint,
                    success=True,
                    response_data=response.json(),
                    execution_time=execution_time
                )
            else:
                return TestResult(
                    tool_name=tool_name,
                    endpoint=endpoint,
                    success=False,
                    response_data=response.text,
                    execution_time=execution_time,
                    error_message=f"HTTP {response.status_code}: {response.text[:200]}"
                )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                tool_name=tool_name,
                endpoint=endpoint,
                success=False,
                response_data=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def test_endpoint(self, tool_name: str, endpoint: str, payload: Dict[str, Any]) -> TestResult:
        """Тестировать один endpoint"""
        start_time = time.time()
        
        try:
            response = self.session.post(f"{BASE_URL}{endpoint}", json=payload, timeout=30)
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                return TestResult(
                    tool_name=tool_name,
                    endpoint=endpoint,
                    success=True,
                    response_data=response.json(),
                    execution_time=execution_time
                )
            else:
                return TestResult(
                    tool_name=tool_name,
                    endpoint=endpoint,
                    success=False,
                    response_data=response.text,
                    execution_time=execution_time,
                    error_message=f"HTTP {response.status_code}: {response.text[:200]}"
                )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                tool_name=tool_name,
                endpoint=endpoint,
                success=False,
                response_data=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def test_all_tools(self):
        """Тестировать все 15 инструментов памяти"""
        print("🚀 Запуск comprehensive тестирования 15 MCP Memory Tools")
        print("=" * 70)
        
        # 1. Проверка здоровья системы
        print("\n📊 СИСТЕМНЫЕ ПРОВЕРКИ")
        health_result = self.test_get_endpoint(
            "Health Check", 
            "/health"
        )
        self.log_result(health_result)
        
        graph_status_result = self.test_get_endpoint(
            "Graph Status",
            "/graph/status"
        )
        self.log_result(graph_status_result)
        
        # 2. БАЗОВЫЕ 11 ИНСТРУМЕНТОВ
        print("\n💾 БАЗОВЫЕ ИНСТРУМЕНТЫ ПАМЯТИ (11)")
        
        # Tool 1: Save Memory
        save_result = self.test_endpoint(
            "Save Memory",
            "/memory/save",
            {
                "content": "Я работаю над проектом mcp-mem0, который объединяет Mem0 SDK с MCP протоколом для создания enterprise-grade системы памяти для AI агентов",
                "user_id": TEST_USER_ID,
                "metadata": {
                    "project": TEST_PROJECT_ID,
                    "category": "project_info",
                    "importance": 9
                }
            }
        )
        self.log_result(save_result)
        
        # Tool 2: Search Memories 
        search_result = self.test_endpoint(
            "Search Memories",
            "/memory/search", 
            {
                "query": "mcp-mem0 проект",
                "user_id": TEST_USER_ID,
                "limit": 5
            }
        )
        self.log_result(search_result)
        
        # Tool 3: Get All Memories
        get_all_result = self.test_endpoint(
            "Get All Memories",
            "/memory/get-all",
            {
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(get_all_result)
        
        # Tool 4: Save Verified Memory
        verified_result = self.test_endpoint(
            "Save Verified Memory",
            "/memory/save-verified",
            {
                "content": "MCP-Mem0 поддерживает 15 инструментов: 11 базовых + 4 графовых. Использует FastAPI + Mem0 SDK + Neo4j для графов.",
                "confidence": 0.95,
                "source": "technical_documentation",
                "user_id": TEST_USER_ID,
                "metadata": {
                    "verified_by": "developer",
                    "project": TEST_PROJECT_ID
                }
            }
        )
        self.log_result(verified_result)
        
        # Tool 5: Get Accurate Context
        context_result = self.test_endpoint(
            "Get Accurate Context",
            "/memory/get-context",
            {
                "query": "архитектура mcp-mem0",
                "user_id": TEST_USER_ID,
                "limit": 3
            }
        )
        self.log_result(context_result)
        
        # Tool 6: Validate Project Context
        validate_result = self.test_endpoint(
            "Validate Project Context",
            "/memory/validate-project-context",
            {
                "query": TEST_PROJECT_ID,
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(validate_result)
        
        # Tool 7: Resolve Context Conflict
        conflict_result = self.test_endpoint(
            "Resolve Context Conflict",
            "/memory/resolve-conflict",
            {
                "query": "конфликт версий API",
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(conflict_result)
        
        # Tool 8: Audit Memory Quality
        audit_result = self.test_endpoint(
            "Audit Memory Quality",
            "/memory/audit-quality",
            {
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(audit_result)
        
        # Tool 9: Save Project Milestone
        milestone_result = self.test_endpoint(
            "Save Project Milestone",
            "/memory/save-milestone",
            {
                "milestone_name": "Production Ready Release",
                "description": "Достигнуто production ready состояние с 15 рабочими инструментами, полной документацией и comprehensive тестами",
                "project_id": TEST_PROJECT_ID,
                "user_id": TEST_USER_ID,
                "metadata": {
                    "version": "1.0.0",
                    "completion_date": datetime.now().isoformat()
                }
            }
        )
        self.log_result(milestone_result)
        
        # Tool 10: Get Current Project State
        project_state_result = self.test_endpoint(
            "Get Current Project State",
            "/memory/get-project-state",
            {
                "query": TEST_PROJECT_ID,
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(project_state_result)
        
        # Tool 11: Track Project Evolution
        evolution_result = self.test_endpoint(
            "Track Project Evolution",
            "/memory/track-evolution",
            {
                "query": TEST_PROJECT_ID,
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(evolution_result)
        
        # 3. ГРАФОВЫЕ 4 ИНСТРУМЕНТА
        print("\n🕸️ ГРАФОВЫЕ ИНСТРУМЕНТЫ ПАМЯТИ (4)")
        
        # Tool 12: Save Graph Memory
        graph_save_result = self.test_endpoint(
            "Save Graph Memory",
            "/graph/save-memory",
            {
                "content": "FastAPI сервер подключается к Neo4j базе данных через Mem0 SDK для хранения графовых связей между сущностями в памяти AI агентов",
                "user_id": TEST_USER_ID,
                "metadata": {
                    "entity_type": "technical_architecture",
                    "relationships": ["FastAPI", "Neo4j", "Mem0", "AI_Agent"]
                }
            }
        )
        self.log_result(graph_save_result)
        
        # Tool 13: Search Graph Memory
        graph_search_result = self.test_endpoint(
            "Search Graph Memory",
            "/graph/search",
            {
                "query": "FastAPI Neo4j связи",
                "user_id": TEST_USER_ID,
                "limit": 5
            }
        )
        self.log_result(graph_search_result)
        
        # Tool 14: Get Entity Relationships
        entity_result = self.test_endpoint(
            "Get Entity Relationships",
            "/graph/entity-relationships",
            {
                "entity_name": "FastAPI",
                "user_id": TEST_USER_ID
            }
        )
        self.log_result(entity_result)
        
        # Tool 15: Graph Status (уже протестировано выше)
        
        # Генерируем отчет
        await self.generate_comprehensive_report()
    
    async def generate_comprehensive_report(self):
        """Генерировать comprehensive отчет о тестировании"""
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        total_tools = len(self.results)
        successful_tools = sum(1 for r in self.results if r.success)
        failed_tools = total_tools - successful_tools
        
        print(f"🎯 Всего протестировано инструментов: {total_tools}")
        print(f"✅ Успешно: {successful_tools}")
        print(f"❌ Неудачно: {failed_tools}")
        print(f"📊 Процент успеха: {(successful_tools/total_tools)*100:.1f}%")
        
        avg_time = sum(r.execution_time for r in self.results) / len(self.results)
        print(f"⏱️ Среднее время выполнения: {avg_time:.2f}s")
        
        # Детальный отчет по категориям
        print(f"\n📈 ДЕТАЛЬНЫЙ АНАЛИЗ ПО КАТЕГОРИЯМ:")
        
        basic_tools = [r for r in self.results if "graph" not in r.endpoint.lower()]
        graph_tools = [r for r in self.results if "graph" in r.endpoint.lower()]
        
        basic_success = sum(1 for r in basic_tools if r.success)
        graph_success = sum(1 for r in graph_tools if r.success)
        
        print(f"💾 Базовые инструменты: {basic_success}/{len(basic_tools)} успешно")
        print(f"🕸️ Графовые инструменты: {graph_success}/{len(graph_tools)} успешно")
        
        # Сохраняем детальный отчет
        report_data = {
            "test_timestamp": datetime.now().isoformat(),
            "total_tools": total_tools,
            "successful_tools": successful_tools,
            "failed_tools": failed_tools,
            "success_rate": (successful_tools/total_tools)*100,
            "average_execution_time": avg_time,
            "detailed_results": [
                {
                    "tool_name": r.tool_name,
                    "endpoint": r.endpoint,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        os.makedirs("test_reports", exist_ok=True)
        report_file = f"test_reports/comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Детальный отчет сохранен: {report_file}")
        
        if failed_tools > 0:
            print(f"\n⚠️ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ:")
            for r in self.results:
                if not r.success:
                    print(f"   ❌ {r.tool_name}: {r.error_message}")
        
        print("\n🎉 Comprehensive тестирование завершено!")
        
        return report_data

async def main():
    """Главная функция для запуска тестов"""
    print("🧪 MCP-Mem0 Comprehensive Test Suite")
    print("Тестируем все 15 инструментов памяти...")
    print()
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code != 200:
            print(f"❌ Сервер недоступен: {BASE_URL}")
            print("Запустите unified_memory_server.py перед тестированием")
            return
    except Exception as e:
        print(f"❌ Не удается подключиться к серверу: {e}")
        print("Запустите unified_memory_server.py перед тестированием")
        return
    
    # Запускаем тесты
    tester = ComprehensiveMemoryTester()
    await tester.test_all_tools()

if __name__ == "__main__":
    asyncio.run(main()) 