"""
🔧 TEMPORAL WORKER - ИСПОЛНИТЕЛЬ MEMORY ACTIVITIES 
===================================================

Dedicated Worker для выполнения всех Temporal Activities
Обрабатывает: memory operations, graph operations, health checks
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from temporalio.client import Client
from temporalio.worker import Worker

# Импорт Activities и Workflows
from temporal_memory_service import (
    execute_memory_save,
    execute_memory_search, 
    execute_graph_operation,
    health_check_activity,
    MemorySessionWorkflow,
    MemoryHealthWorkflow
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск Temporal Worker"""
    
    # Получение адреса Temporal Server из переменных окружения
    temporal_address = os.getenv("TEMPORAL_SERVER_ADDRESS", "localhost:7233")
    
    # Подключение к Temporal Server с повторными попытками
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            client = await Client.connect(temporal_address)
            logger.info(f"🔗 Connected to Temporal Server at {temporal_address}")
            break
        except Exception as e:
            logger.error(f"❌ Failed to connect to Temporal (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏰ Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 30)  # Exponential backoff
            else:
                logger.error("🚫 Max retries reached. Exiting.")
                return
    
    # Создание Worker
    worker = Worker(
        client,
        task_queue="memory-task-queue",
        workflows=[
            MemorySessionWorkflow,
            MemoryHealthWorkflow
        ],
        activities=[
            execute_memory_save,
            execute_memory_search,
            execute_graph_operation,
            health_check_activity
        ]
    )
    
    logger.info("🚀 Starting Temporal Worker...")
    logger.info("📋 Registered Workflows: MemorySessionWorkflow, MemoryHealthWorkflow")
    logger.info("⚡ Registered Activities: memory_save, memory_search, graph_operation, health_check")
    logger.info("🎯 Task Queue: memory-task-queue")
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("🛑 Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Worker error: {e}")
    finally:
        await client.close()
        logger.info("🔚 Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main()) 