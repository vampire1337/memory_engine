#!/usr/bin/env python3
"""
🔥 ПРОСТОЙ ТЕСТ TEMPORAL В КОНТЕЙНЕРЕ
Проверяет работу start_workflow изнутри контейнера
"""

import asyncio
import sys
import os

# Добавляем пути
sys.path.append('/app')
sys.path.append('/app/src')

# Импортируем с debug wrapper
from debug_temporal import patch_temporal_client, TemporalDebugWrapper
patch_temporal_client()

from temporalio.client import Client
from temporalio import workflow

# Workflow classes на module level
@workflow.defn
class SimpleTestWorkflow:
    @workflow.run
    async def run(self, test_arg: str) -> str:
        return f"Test success: {test_arg}"

@workflow.defn
class NoArgsWorkflow:
    @workflow.run
    async def run(self) -> str:
        return "No args test"

async def test_temporal_inside_container():
    """Тестирует Temporal изнутри контейнера"""
    print("🔥 ЗАПУСК ТЕСТА TEMPORAL ИЗНУТРИ КОНТЕЙНЕРА")
    
    try:
        print("✅ Debug wrapper активирован")
        
        print("🔌 Подключение к Temporal...")
        client = await Client.connect("temporal-server:7233")
        print(f"✅ Клиент создан: {type(client)}")
        
        print("🚀 ТЕСТ 1: start_workflow с 1 аргументом")
        try:
            handle = await client.start_workflow(
                SimpleTestWorkflow.run,
                "test_argument",
                id="test-1",
                task_queue="test-queue"
            )
            print("✅ ТЕСТ 1 ПРОШЕЛ!")
        except Exception as e:
            print(f"❌ ТЕСТ 1 ПРОВАЛИЛСЯ: {e}")
            
        print("🚀 ТЕСТ 2: start_workflow БЕЗ аргументов")
        try:
            handle = await client.start_workflow(
                NoArgsWorkflow.run,
                id="test-2",
                task_queue="test-queue"
            )
            print("✅ ТЕСТ 2 ПРОШЕЛ!")
        except Exception as e:
            print(f"❌ ТЕСТ 2 ПРОВАЛИЛСЯ: {e}")
            
        print("🚀 ТЕСТ 3: Попытка воспроизвести проблему (3 аргумента)")
        # Воспроизводим точный вызов из нашего кода
        try:
            handle = await client.start_workflow(
                SimpleTestWorkflow.run,
                "session_id_test",  # session_id
                "user_id_test",     # user_id  
                "agent_id_test",    # agent_id
                id="test-3",
                task_queue="memory-task-queue"
            )
            print("✅ ТЕСТ 3 ПРОШЕЛ!")
        except Exception as e:
            print(f"❌ ТЕСТ 3 ПРОВАЛИЛСЯ: {e}")
            print(f"Это наша проблема!")
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_temporal_inside_container()) 