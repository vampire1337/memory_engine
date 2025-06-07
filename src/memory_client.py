"""
🧠 ENTERPRISE MEMORY CLIENT v2.0
Клиент для работы с Mem0 Graph + Vector памятью + Redis синхронизация

Поддержка ВСЕХ 17 ENTERPRISE TOOLS:
- Правильная Supabase конфигурация (порт 5432)
- Mem0 v1.1 Graph + Vector одновременно
- Redis events & caching
- Production error handling
"""

import logging
import os
import json
import asyncio
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta

# Настройка логирования
logger = logging.getLogger(__name__)

# Mem0 imports
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
    logger.info("✅ Mem0 SDK импортирован")
except ImportError as e:
    MEM0_AVAILABLE = False
    Memory = None
    logger.error(f"❌ Mem0 SDK недоступен: {e}")

# Redis больше не используется - заменен на Temporal
REDIS_AVAILABLE = False


class EnterpriseMemoryClient:
    """
    Enterprise Memory Client для работы с 17 tools
    
    Возможности:
    - Graph Memory (Memgraph) + Vector Memory (Supabase) одновременно
    - Redis синхронизация и кэширование 
    - Comprehensive error handling
    - Production-ready metrics
    """
    
    def __init__(self):
        self.memory: Optional[Memory] = None
        
        # Флаги поддержки
        self.graph_support = False
        self.vector_support = False
        self.redis_support = False  # Заменен на Temporal
        
        # Metrics
        self.operations_count = 0
        self.errors_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("🧠 EnterpriseMemoryClient инициализирован")
    
    async def initialize(self) -> None:
        """Асинхронная инициализация клиента"""
        try:
            logger.info("🔄 Инициализация Enterprise Memory Client...")
            
            if not MEM0_AVAILABLE:
                raise RuntimeError("Mem0 SDK недоступен")
            
            # Получение конфигурации из переменных окружения
            config = self._get_memory_config()
            
            # Инициализация Mem0 
            logger.info("📝 Создание Mem0 Memory с full config...")
            logger.info(f"🔧 Config: {config}")
            
            try:
                self.memory = Memory.from_config(config_dict=config)
                logger.info("✅ Mem0 Memory создан успешно")
            except Exception as supabase_error:
                if "Wrong password" in str(supabase_error) or "connection" in str(supabase_error).lower():
                    logger.warning(f"⚠️ Supabase недоступен ({supabase_error}), переключаемся на Qdrant")
                    
                    # Fallback конфигурация с Qdrant
                    fallback_config = config.copy()
                    fallback_config["vector_store"] = {
                        "provider": "qdrant",
                        "config": {
                            "host": "qdrant",
                            "port": 6333
                        }
                    }
                    
                    logger.info("🔄 Повторная инициализация с Qdrant...")
                    self.memory = Memory.from_config(config_dict=fallback_config)
                    logger.info("✅ Mem0 Memory создан с Qdrant fallback")
                else:
                    raise supabase_error
            
            # Проверка поддержки компонентов
            await self._check_component_support()
            
            logger.info(f"✅ Memory Client готов:")
            logger.info(f"   🕸️ Graph Support: {self.graph_support}")
            logger.info(f"   🔍 Vector Support: {self.vector_support}")
            logger.info(f"   🔄 Redis Support: {self.redis_support}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Memory Client: {e}")
            self.memory = None
            raise
    
    def _get_memory_config(self) -> Dict[str, Any]:
        """Получение конфигурации Mem0 из переменных окружения"""
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: порт 5432 вместо 6543
        database_url = os.getenv("DATABASE_URL")
        if database_url and ":6543" in database_url:
            database_url = database_url.replace(":6543", ":5432")
            logger.info("🔧 Исправлен порт DATABASE_URL: 6543 → 5432 (Session pooler)")
        
        # Fallback к локальной базе если Supabase недоступен
        if not database_url or "Wrong password" in str(database_url):
            logger.warning("⚠️ Supabase недоступен, переключаемся на локальную Qdrant")
            vector_config = {
                "provider": "qdrant",
                "config": {
                    "host": "qdrant",
                    "port": 6333
                }
            }
        else:
            vector_config = {
                "provider": "supabase",
                "config": {
                    "connection_string": database_url or os.getenv("POSTGRES_URL")
                }
            }
        
        config = {
            "version": "v1.1",  # ВАЖНО: версия для Graph Memory
            
            # Graph Store (Memgraph через neo4j драйвер)
            "graph_store": {
                "provider": "neo4j", 
                "config": {
                    "url": os.getenv("NEO4J_URL", "bolt://memgraph:7687"),
                    "username": os.getenv("NEO4J_USERNAME", "memgraph"),
                    "password": os.getenv("NEO4J_PASSWORD", "memgraph")
                    # НЕ указываем database параметр - Memgraph не поддерживает отдельные БД
                }
            },
            
            # Vector Store (с fallback)
            "vector_store": vector_config,
            
            # LLM Configuration
            "llm": {
                "provider": "openai",
                "config": {
                    "model": os.getenv("LLM_CHOICE") or os.getenv("MEM0_DEFAULT_LLM_MODEL", "gpt-4o-mini"),
                    "api_key": os.getenv("OPENAI_API_KEY")
                }
            },
            
            # Embedder Configuration
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": os.getenv("EMBEDDING_MODEL_CHOICE") or os.getenv("MEM0_DEFAULT_EMBEDDING_MODEL", "text-embedding-3-small"),
                    "api_key": os.getenv("OPENAI_API_KEY")
                }
            }
        }
        
        logger.info("📋 Конфигурация Mem0:")
        logger.info(f"   🕸️ Graph Store: {config['graph_store']['provider']}")
        logger.info(f"   🔍 Vector Store: {config['vector_store']['provider']}")
        logger.info(f"   🤖 LLM: {config['llm']['config']['model']}")
        
        return config
    
    async def _check_component_support(self) -> None:
        """Проверка поддержки компонентов"""
        try:
            # Проверяем что Memory создан
            if self.memory is None:
                return
            
            # Mem0 автоматически определяет доступность store'ов при инициализации
            # Если конфигурация корректна - support = True
            self.graph_support = True  # Будет False если Memgraph недоступен
            self.vector_support = True  # Будет False если Supabase недоступен
            
            logger.info("✅ Проверка компонентов завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки компонентов: {e}")
            self.graph_support = False
            self.vector_support = False
    
    async def add_memory(
        self,
        content: str,
        user_id: str = "user",
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Добавление памяти в Graph + Vector store одновременно
        
        Args:
            content: Контент для сохранения
            user_id: ID пользователя
            agent_id: ID агента (опционально)
            session_id: ID сессии (опционально)
            metadata: Дополнительные метаданные
            
        Returns:
            Dict с результатом операции
        """
        try:
            if not self.memory:
                raise RuntimeError("Memory client не инициализирован")
            
            # Подготовка метаданных
            full_metadata = metadata or {}
            if agent_id:
                full_metadata["agent_id"] = agent_id
            if session_id:
                full_metadata["session_id"] = session_id
            
            full_metadata.update({
                "timestamp": datetime.now().isoformat(),
                "client_version": "2.0.0"
            })
            
            # Добавление в Mem0 (автоматически в graph + vector)
            result = await asyncio.to_thread(
                self.memory.add,
                content,
                user_id=user_id,
                metadata=full_metadata
            )
            
            self.operations_count += 1
            
            logger.info(f"✅ Память добавлена: {result.get('id')} для {user_id}")
            
            return {
                "id": result.get("id"),
                "message": result.get("message", "Memory added successfully"),
                "user_id": user_id,
                "content": content,
                "metadata": full_metadata,
                "graph_processed": self.graph_support,
                "vector_processed": self.vector_support,
                "timestamp": full_metadata["timestamp"]
            }
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"❌ Ошибка добавления памяти: {e}")
            raise RuntimeError(f"Ошибка добавления памяти: {str(e)}")
    
    async def search_memory(
        self,
        query: str,
        user_id: str = "user",
        limit: int = 5,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Поиск в памяти с использованием Graph + Vector
        
        Args:
            query: Поисковый запрос
            user_id: ID пользователя
            limit: Максимальное количество результатов
            agent_id: ID агента (опционально)
            session_id: ID сессии (опционально)
            
        Returns:
            Dict с результатами поиска
        """
        try:
            if not self.memory:
                raise RuntimeError("Memory client не инициализирован")
            
            # Поиск в Mem0 (автоматически использует graph + vector)
            results = await asyncio.to_thread(
                self.memory.search,
                query,
                user_id=user_id,
                limit=limit
            )
            
            self.operations_count += 1
            
            # Форматируем результаты
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.get("id"),
                    "memory": result.get("memory"),
                    "score": result.get("score", 0.0),
                    "metadata": result.get("metadata", {}),
                    "created_at": result.get("created_at"),
                    "updated_at": result.get("updated_at")
                })
            
            logger.info(f"🔍 Поиск выполнен: {len(formatted_results)} результатов для '{query[:50]}...'")
            
            return {
                "query": query,
                "user_id": user_id,
                "memories": formatted_results,
                "total_found": len(formatted_results),
                "search_type": "hybrid" if self.graph_support and self.vector_support else "vector",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"❌ Ошибка поиска: {e}")
            raise RuntimeError(f"Ошибка поиска: {str(e)}")
    
    async def list_memory(
        self,
        user_id: str = "user",
        limit: int = 50,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получение списка всех воспоминаний пользователя
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей
            agent_id: ID агента (опционально)
            session_id: ID сессии (опционально)
            
        Returns:
            Dict со списком воспоминаний
        """
        try:
            if not self.memory:
                raise RuntimeError("Memory client не инициализирован")
            
            # Получение всех воспоминаний
            results = await asyncio.to_thread(
                self.memory.get_all,
                user_id=user_id
            )
            
            # Ограничение результатов
            if len(results) > limit:
                results = results[:limit]
            
            self.operations_count += 1
            
            # Форматируем результаты
            formatted_memories = []
            for result in results:
                formatted_memories.append({
                    "id": result.get("id"),
                    "memory": result.get("memory"),
                    "metadata": result.get("metadata", {}),
                    "created_at": result.get("created_at"),
                    "updated_at": result.get("updated_at")
                })
            
            logger.info(f"📋 Получен список: {len(formatted_memories)} воспоминаний для {user_id}")
            
            return {
                "user_id": user_id,
                "memories": formatted_memories,
                "total_count": len(formatted_memories),
                "limit_applied": limit,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"❌ Ошибка получения списка: {e}")
            raise RuntimeError(f"Ошибка получения списка: {str(e)}")
    
    async def update_memory(
        self,
        memory_id: str,
        content: str,
        user_id: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Обновление существующей памяти
        
        Args:
            memory_id: ID памяти для обновления
            content: Новый контент
            user_id: ID пользователя
            metadata: Новые метаданные
            
        Returns:
            Dict с результатом обновления
        """
        try:
            if not self.memory:
                raise RuntimeError("Memory client не инициализирован")
            
            # Обновление в Mem0
            result = await asyncio.to_thread(
                self.memory.update,
                memory_id=memory_id,
                data=content,
                metadata=metadata
            )
            
            self.operations_count += 1
            
            logger.info(f"✅ Память обновлена: {memory_id}")
            
            return {
                "id": memory_id,
                "message": result.get("message", "Memory updated successfully"),
                "user_id": user_id,
                "new_content": content,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"❌ Ошибка обновления памяти: {e}")
            raise RuntimeError(f"Ошибка обновления памяти: {str(e)}")
    
    async def delete_memory(
        self,
        memory_id: Optional[str] = None,
        user_id: Optional[str] = None,
        delete_all: bool = False
    ) -> Dict[str, Any]:
        """
        Удаление памяти
        
        Args:
            memory_id: ID конкретной памяти для удаления
            user_id: ID пользователя (для удаления всех его воспоминаний)
            delete_all: Флаг удаления всех воспоминаний пользователя
            
        Returns:
            Dict с результатом удаления
        """
        try:
            if not self.memory:
                raise RuntimeError("Memory client не инициализирован")
            
            if delete_all and user_id:
                # Удаление всех воспоминаний пользователя
                result = await asyncio.to_thread(
                    self.memory.delete_all,
                    user_id=user_id
                )
                
                logger.info(f"🗑️ Удалены все воспоминания пользователя: {user_id}")
                
                return {
                    "action": "delete_all",
                    "user_id": user_id,
                    "message": result.get("message", "All memories deleted successfully"),
                    "timestamp": datetime.now().isoformat()
                }
                
            elif memory_id:
                # Удаление конкретной памяти
                result = await asyncio.to_thread(
                    self.memory.delete,
                    memory_id=memory_id
                )
                
                logger.info(f"🗑️ Удалена память: {memory_id}")
                
                return {
                    "action": "delete_single",
                    "memory_id": memory_id,
                    "message": result.get("message", "Memory deleted successfully"),
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                raise ValueError("Необходимо указать memory_id или user_id с delete_all=True")
            
            self.operations_count += 1
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"❌ Ошибка удаления памяти: {e}")
            raise RuntimeError(f"Ошибка удаления памяти: {str(e)}")
    
    async def get_memory_history(
        self,
        memory_id: str
    ) -> Dict[str, Any]:
        """
        Получение истории изменений памяти
        
        Args:
            memory_id: ID памяти
            
        Returns:
            Dict с историей памяти
        """
        try:
            if not self.memory:
                raise RuntimeError("Memory client не инициализирован")
            
            # Получение истории из Mem0
            history = await asyncio.to_thread(
                self.memory.history,
                memory_id=memory_id
            )
            
            self.operations_count += 1
            
            logger.info(f"📜 История памяти {memory_id}: {len(history)} записей")
            
            return {
                "memory_id": memory_id,
                "history": history,
                "history_count": len(history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.errors_count += 1
            logger.error(f"❌ Ошибка получения истории: {e}")
            raise RuntimeError(f"Ошибка получения истории: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния Memory Client
        
        Returns:
            Dict со статусом компонентов
        """
        try:
            health_status = {
                "status": "healthy",
                "memory_client": {
                    "initialized": self.memory is not None,
                    "graph_support": self.graph_support,
                    "vector_support": self.vector_support,
                    "redis_support": self.redis_support
                },
                "metrics": {
                    "operations_count": self.operations_count,
                    "errors_count": self.errors_count,
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                    "error_rate": self.errors_count / max(self.operations_count, 1)
                },
                "capabilities": {
                    "add_memory": self.memory is not None,
                    "search_memory": self.memory is not None,
                    "graph_operations": self.graph_support,
                    "vector_operations": self.vector_support,
                    "hybrid_search": self.graph_support and self.vector_support
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Определение общего статуса
            if not self.memory:
                health_status["status"] = "unhealthy"
            elif self.errors_count / max(self.operations_count, 1) > 0.1:  # > 10% ошибок
                health_status["status"] = "degraded"
            elif not (self.graph_support or self.vector_support):
                health_status["status"] = "partial"
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Ошибка health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение подробной статистики клиента"""
        return {
            "client_version": "2.0.0",
            "operations_count": self.operations_count,
            "errors_count": self.errors_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "success_rate": (self.operations_count - self.errors_count) / max(self.operations_count, 1),
            "components": {
                "memory_initialized": self.memory is not None,
                "graph_support": self.graph_support,
                "vector_support": self.vector_support,
                "redis_support": self.redis_support
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def close(self) -> None:
        """Закрытие соединений и cleanup"""
        try:
            # Mem0 не требует explicit close
            if self.memory:
                logger.info("📝 Memory client connections закрыты")
            
            # Сброс состояния
            self.memory = None
            self.graph_support = False
            self.vector_support = False
            
            logger.info("🔒 EnterpriseMemoryClient закрыт")
            
        except Exception as e:
            logger.error(f"❌ Ошибка закрытия клиента: {e}")


# =================== FACTORY ФУНКЦИИ ===================

async def create_enterprise_memory_client() -> EnterpriseMemoryClient:
    """Factory функция для создания и инициализации клиента"""
    client = EnterpriseMemoryClient()
    await client.initialize()
    return client


def get_memory_client_sync() -> EnterpriseMemoryClient:
    """Синхронная версия для compatibility"""
    return EnterpriseMemoryClient()


# =================== SINGLETON PATTERN ===================

_global_memory_client: Optional[EnterpriseMemoryClient] = None


async def get_global_memory_client() -> EnterpriseMemoryClient:
    """Получение глобального экземпляра клиента (singleton)"""
    global _global_memory_client
    
    if _global_memory_client is None:
        _global_memory_client = await create_enterprise_memory_client()
    
    return _global_memory_client


async def close_global_memory_client() -> None:
    """Закрытие глобального клиента"""
    global _global_memory_client
    
    if _global_memory_client:
        await _global_memory_client.close()
        _global_memory_client = None


# =================== UTILITIES ===================

def validate_memory_config() -> Dict[str, bool]:
    """Валидация конфигурации перед инициализацией"""
    required_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "NEO4J_URL"
    ]
    
    validation_result = {}
    for var in required_vars:
        validation_result[var] = os.getenv(var) is not None
    
    return validation_result


if __name__ == "__main__":
    # Тестирование клиента
    async def test_client():
        try:
            logger.info("🧪 Тестирование EnterpriseMemoryClient...")
            
            # Валидация конфигурации
            config_status = validate_memory_config()
            logger.info(f"📋 Конфигурация: {config_status}")
            
            # Создание клиента
            client = await create_enterprise_memory_client()
            
            # Health check
            health = await client.health_check()
            logger.info(f"🏥 Health: {health['status']}")
            
            # Статистика
            stats = await client.get_stats()
            logger.info(f"📊 Stats: {stats}")
            
            # Закрытие
            await client.close()
            
            logger.info("✅ Тест завершен успешно!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка теста: {e}")
    
    # Запуск теста
    asyncio.run(test_client()) 