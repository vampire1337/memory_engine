#!/usr/bin/env python3
"""
🔥 МИНИМАЛЬНЫЙ ТЕСТ TEMPORAL START_WORKFLOW
Проверяет правильность работы Temporal Client.start_workflow()
"""

import asyncio
from temporalio import activity, workflow
from temporalio.client import Client


# Простой workflow для тестирования
@workflow.defn
class TestWorkflow:
    @workflow.run
    async def run(self, user_id: str, agent_id: str = None) -> str:
        return f"SUCCESS: {user_id}, {agent_id}"


async def test_temporal_start_workflow():
    """Тестирует правильность вызова start_workflow"""
    print("🧪 Тестирование Temporal Client.start_workflow()...")
    
    try:
        # Подключение к Temporal
        client = await Client.connect("localhost:7233")
        print("✅ Подключение к Temporal успешно")
        
        # ПРАВИЛЬНЫЙ способ вызова start_workflow
        print("\n🔥 Тест 1: ПРАВИЛЬНЫЙ СИНТАКСИС")
        workflow_handle = await client.start_workflow(
            TestWorkflow.run,  # workflow method (позиционный аргумент 1)
            "test_user",       # аргументы workflow (позиционный аргумент 2+)  
            "test_agent",      # еще один аргумент workflow
            id="test-workflow-correct",  # workflow ID (keyword argument)
            task_queue="test-queue"      # task queue (keyword argument)
        )
        result = await workflow_handle.result()
        print(f"✅ Результат: {result}")
        
        # НЕПРАВИЛЬНЫЙ способ - передача параметров как keyword args workflow
        print("\n❌ Тест 2: НЕПРАВИЛЬНЫЙ СИНТАКСИС (как в нашем коде)")
        try:
            workflow_handle = await client.start_workflow(
                TestWorkflow.run,         # workflow method
                user_id="test_user",      # ❌ НЕПРАВИЛЬНО - это keyword workflow arg!
                agent_id="test_agent",    # ❌ НЕПРАВИЛЬНО - это keyword workflow arg!
                id="test-workflow-wrong", # правильный keyword arg для start_workflow
                task_queue="test-queue"   # правильный keyword arg для start_workflow
            )
        except Exception as e:
            print(f"❌ Ошибка (ожидаемая): {e}")
            
        print("\n🎯 ДИАГНОСТИКА ЗАВЕРШЕНА!")
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_temporal_start_workflow()) 