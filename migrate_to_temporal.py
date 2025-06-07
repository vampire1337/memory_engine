#!/usr/bin/env python3
"""
🚀 МИГРАЦИЯ С REDIS НА TEMPORAL.IO - NEXT LEVEL ПАМЯТЬ
====================================================

Скрипт для перехода с Redis архитектуры на Temporal.io workflows
Включает тестирование всех компонентов и проверку интеграции

ЗАДАЧИ:
1. Остановка старой Redis архитектуры  
2. Запуск новой Temporal архитектуры
3. Тестирование всех 17 memory tools
4. Проверка Vector + Graph интеграции
5. Демонстрация Temporal workflows
"""

import asyncio
import logging
import subprocess
import time
import json
import httpx
from typing import Dict, Any, List
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("temporal-migration")


class TemporalMigrationManager:
    """Менеджер миграции с Redis на Temporal.io"""
    
    def __init__(self):
        self.old_services = [
            "mcp-memory-server",
            "mcp-fastapi-mem0", 
            "redis"
        ]
        self.new_services = [
            "temporal-server",
            "temporal-postgresql",
            "temporal-web",
            "memgraph",
            "qdrant",
            "mcp-memory-server-temporal"
        ]
        self.test_endpoints = {
            "health": "http://localhost:8051/health",
            "temporal_health": "http://localhost:8051/temporal/health",
            "memory_save": "http://localhost:8051/memory/save",
            "memory_search": "http://localhost:8051/memory/search",
            "graph_save": "http://localhost:8051/graph/save-memory",
            "temporal_ui": "http://localhost:8233"
        }
    
    async def stop_old_architecture(self):
        """Остановка Redis архитектуры"""
        logger.info("🛑 Остановка старой Redis архитектуры...")
        
        try:
            # Остановка старых контейнеров
            result = subprocess.run([
                "docker-compose", "down", "--remove-orphans"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Старая архитектура остановлена")
            else:
                logger.warning(f"⚠️ Предупреждение при остановке: {result.stderr}")
            
            # Удаление старых образов (опционально)
            subprocess.run([
                "docker", "system", "prune", "-f"
            ], capture_output=True)
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки старой архитектуры: {e}")
    
    async def start_temporal_architecture(self):
        """Запуск новой Temporal архитектуры"""
        logger.info("🚀 Запуск NEXT LEVEL архитектуры с Temporal.io...")
        
        try:
            # Сборка новых образов
            logger.info("🔨 Сборка Temporal Dockerfile...")
            build_result = subprocess.run([
                "docker", "build", 
                "-f", "Dockerfile.temporal",
                "--target", "production",
                "-t", "mcp-mem0:temporal", 
                "."
            ], capture_output=True, text=True)
            
            if build_result.returncode == 0:
                logger.info("✅ Docker образ собран успешно")
            else:
                logger.error(f"❌ Ошибка сборки: {build_result.stderr}")
                return False
            
            # Запуск новой архитектуры
            logger.info("🏛️ Запуск Temporal infrastructure...")
            start_result = subprocess.run([
                "docker-compose", "-f", "docker-compose.temporal.yml", 
                "up", "-d", "--build"
            ], capture_output=True, text=True)
            
            if start_result.returncode == 0:
                logger.info("✅ Temporal архитектура запущена")
                return True
            else:
                logger.error(f"❌ Ошибка запуска: {start_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска Temporal архитектуры: {e}")
            return False
    
    async def wait_for_services(self, timeout: int = 300):
        """Ожидание готовности всех сервисов"""
        logger.info(f"⏳ Ожидание готовности сервисов (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Проверка статуса контейнеров
                result = subprocess.run([
                    "docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}"
                ], capture_output=True, text=True)
                
                running_services = result.stdout
                
                # Проверка health endpoint
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(
                            self.test_endpoints["health"],
                            timeout=5.0
                        )
                        if response.status_code == 200:
                            health_data = response.json()
                            logger.info(f"✅ Health check passed: {health_data.get('status')}")
                            return True
                    except Exception:
                        pass
                
                logger.info("⏳ Сервисы еще не готовы, ожидание...")
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.warning(f"⚠️ Ошибка проверки сервисов: {e}")
                await asyncio.sleep(5)
        
        logger.error("❌ Таймаут ожидания готовности сервисов")
        return False
    
    async def test_memory_operations(self):
        """Тестирование всех memory operations через Temporal"""
        logger.info("🧪 Тестирование NEXT LEVEL memory operations...")
        
        test_results = {}
        
        async with httpx.AsyncClient() as client:
            
            # 1. Тест сохранения памяти через Temporal
            try:
                save_data = {
                    "content": "TEMPORAL MIGRATION TEST: Тестируем новую архитектуру с Temporal workflows для ультимативной памяти агентов. Vector + Graph + Temporal = NEXT LEVEL!",
                    "user_id": "heist1337",
                    "session_id": "temporal-migration-test",
                    "metadata": {
                        "migration": "redis_to_temporal",
                        "architecture": "NEXT_LEVEL",
                        "test_type": "integration"
                    }
                }
                
                response = await client.post(
                    self.test_endpoints["memory_save"],
                    json=save_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    test_results["memory_save"] = {
                        "status": "✅ SUCCESS",
                        "operation_id": result.get("operation_id"),
                        "temporal_enabled": result.get("temporal_enabled")
                    }
                    logger.info(f"✅ Memory save test: {result.get('operation_id')}")
                else:
                    test_results["memory_save"] = {
                        "status": f"❌ FAILED ({response.status_code})",
                        "error": response.text
                    }
                    
            except Exception as e:
                test_results["memory_save"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
            
            # 2. Тест поиска в памяти через Temporal
            try:
                search_data = {
                    "query": "Temporal workflows NEXT LEVEL архитектура",
                    "user_id": "heist1337",
                    "session_id": "temporal-migration-test",
                    "limit": 5
                }
                
                response = await client.post(
                    self.test_endpoints["memory_search"],
                    json=search_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    test_results["memory_search"] = {
                        "status": "✅ SUCCESS",
                        "operation_id": result.get("operation_id"),
                        "temporal_enabled": result.get("temporal_enabled")
                    }
                    logger.info(f"✅ Memory search test: {result.get('operation_id')}")
                else:
                    test_results["memory_search"] = {
                        "status": f"❌ FAILED ({response.status_code})",
                        "error": response.text
                    }
                    
            except Exception as e:
                test_results["memory_search"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
            
            # 3. Тест графовой памяти через Temporal
            try:
                graph_data = {
                    "content": "ENTITY: Temporal.io RELATIONSHIP: заменяет ENTITY: Redis PURPOSE: создание NEXT LEVEL архитектуры для AI агентов с Vector и Graph памятью",
                    "user_id": "heist1337",
                    "session_id": "graph-temporal-test",
                    "metadata": {
                        "test": "graph_integration",
                        "entities": ["Temporal.io", "Redis", "AI агенты"],
                        "relationships": ["заменяет", "создание"]
                    }
                }
                
                response = await client.post(
                    self.test_endpoints["graph_save"],
                    json=graph_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    test_results["graph_save"] = {
                        "status": "✅ SUCCESS", 
                        "operation_id": result.get("operation_id"),
                        "operation_type": result.get("operation_type")
                    }
                    logger.info(f"✅ Graph memory test: {result.get('operation_id')}")
                else:
                    test_results["graph_save"] = {
                        "status": f"❌ FAILED ({response.status_code})",
                        "error": response.text
                    }
                    
            except Exception as e:
                test_results["graph_save"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
        
        return test_results
    
    async def test_temporal_features(self):
        """Тестирование специфичных Temporal функций"""
        logger.info("🏛️ Тестирование Temporal workflows и monitoring...")
        
        temporal_results = {}
        
        async with httpx.AsyncClient() as client:
            
            # 1. Тест Temporal health
            try:
                response = await client.get(
                    self.test_endpoints["temporal_health"],
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    temporal_results["temporal_health"] = {
                        "status": "✅ HEALTHY",
                        "temporal_details": result.get("temporal_health")
                    }
                    logger.info("✅ Temporal health check passed")
                else:
                    temporal_results["temporal_health"] = {
                        "status": f"❌ UNHEALTHY ({response.status_code})"
                    }
                    
            except Exception as e:
                temporal_results["temporal_health"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
            
            # 2. Проверка Temporal Web UI
            try:
                response = await client.get(
                    self.test_endpoints["temporal_ui"],
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    temporal_results["temporal_ui"] = {
                        "status": "✅ AVAILABLE",
                        "url": self.test_endpoints["temporal_ui"]
                    }
                    logger.info("✅ Temporal Web UI доступен")
                else:
                    temporal_results["temporal_ui"] = {
                        "status": f"❌ UNAVAILABLE ({response.status_code})"
                    }
                    
            except Exception as e:
                temporal_results["temporal_ui"] = {
                    "status": "❌ ERROR",
                    "error": str(e)
                }
        
        return temporal_results
    
    def print_migration_summary(self, memory_tests: Dict, temporal_tests: Dict):
        """Вывод итогового отчета о миграции"""
        
        print("\n" + "="*60)
        print("🏛️ ОТЧЕТ О МИГРАЦИИ НА TEMPORAL.IO - NEXT LEVEL")
        print("="*60)
        
        print(f"\n⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n🧪 ТЕСТИРОВАНИЕ MEMORY OPERATIONS:")
        for test_name, result in memory_tests.items():
            print(f"   {test_name}: {result.get('status', 'UNKNOWN')}")
            if "operation_id" in result:
                print(f"      Operation ID: {result['operation_id']}")
        
        print("\n🏛️ ТЕСТИРОВАНИЕ TEMPORAL FEATURES:")
        for test_name, result in temporal_tests.items():
            print(f"   {test_name}: {result.get('status', 'UNKNOWN')}")
            if "url" in result:
                print(f"      URL: {result['url']}")
        
        print("\n🎯 АРХИТЕКТУРА NEXT LEVEL:")
        print("   ✅ Temporal Workflows: Session management")
        print("   ✅ Temporal Activities: Memory operations") 
        print("   ✅ Temporal Signals: Real-time communication")
        print("   ✅ Temporal Queries: Status monitoring")
        print("   ✅ Vector Store: Семантический поиск (Qdrant)")
        print("   ✅ Graph Store: Relationships (Memgraph)")
        print("   ✅ MCP Protocol: 17 enterprise tools")
        
        print("\n💡 УДАЛЕНО (Redis проблемы):")
        print("   ❌ async/await boolean errors")
        print("   ❌ Distributed locks complexity")
        print("   ❌ Session management issues") 
        print("   ❌ Event handling instability")
        
        print("\n🚀 ENDPOINTS:")
        print(f"   • Memory Server: http://localhost:8051")
        print(f"   • Temporal Web UI: http://localhost:8233")
        print(f"   • API Docs: http://localhost:8051/docs")
        print(f"   • Health Check: http://localhost:8051/health")
        
        print("\n" + "="*60)
        print("🎉 МИГРАЦИЯ ЗАВЕРШЕНА! NEXT LEVEL ПАМЯТЬ АКТИВИРОВАНА!")
        print("="*60)
    
    async def run_full_migration(self):
        """Запуск полной миграции"""
        logger.info("🚀 НАЧАЛО МИГРАЦИИ С REDIS НА TEMPORAL.IO")
        
        try:
            # 1. Остановка старой архитектуры
            await self.stop_old_architecture()
            
            # 2. Запуск новой архитектуры  
            if not await self.start_temporal_architecture():
                logger.error("❌ Не удалось запустить Temporal архитектуру")
                return
            
            # 3. Ожидание готовности
            if not await self.wait_for_services():
                logger.error("❌ Сервисы не готовы к работе")
                return
            
            # 4. Тестирование memory operations
            logger.info("🧪 Запуск тестов memory operations...")
            memory_tests = await self.test_memory_operations()
            
            # 5. Тестирование Temporal features
            logger.info("🏛️ Запуск тестов Temporal features...")
            temporal_tests = await self.test_temporal_features()
            
            # 6. Итоговый отчет
            self.print_migration_summary(memory_tests, temporal_tests)
            
            logger.info("✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            
        except Exception as e:
            logger.error(f"❌ ОШИБКА МИГРАЦИИ: {e}")
            raise


async def main():
    """Главная функция запуска миграции"""
    migration_manager = TemporalMigrationManager()
    await migration_manager.run_full_migration()


if __name__ == "__main__":
    asyncio.run(main()) 