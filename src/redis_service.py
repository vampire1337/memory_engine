"""
🚀 Redis Service для MCP-Mem0
==========================

Обеспечивает:
- Event-driven синхронизацию между Memgraph и Supabase
- Кэширование для производительности  
- Distributed locking для ACID операций
- Message queue для асинхронных задач
- Session management
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import redis
import redis.asyncio as aioredis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class RedisEventTypes:
    """Типы событий для синхронизации"""
    
    # Memgraph события
    ENTITY_CREATED = "entity_created"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_DELETED = "entity_deleted"
    RELATIONSHIP_CREATED = "relationship_created"
    RELATIONSHIP_UPDATED = "relationship_updated"
    RELATIONSHIP_DELETED = "relationship_deleted"
    
    # Supabase события
    VECTOR_UPDATED = "vector_updated"
    SEARCH_PERFORMED = "search_performed"
    
    # Системные события
    SYSTEM_STATUS = "system_status"
    CACHE_INVALIDATED = "cache_invalidated"


class RedisService:
    """
    🚀 Основной Redis сервис для MCP-Mem0
    
    Функциональность:
    - Event-driven синхронизация
    - Интеллектуальное кэширование  
    - Distributed locking
    - Message queues
    - Session management
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        password: Optional[str] = None,
        max_connections: int = 100,
        decode_responses: bool = True,
        default_ttl: int = 300,  # 5 минут
        session_ttl: int = 3600,  # 1 час
        lock_timeout: int = 30,   # 30 секунд
    ):
        self.redis_url = redis_url
        self.password = password
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.default_ttl = default_ttl
        self.session_ttl = session_ttl
        self.lock_timeout = lock_timeout
        
        self.redis: Optional[Redis] = None
        self.pubsub: Optional[Any] = None
        self._connected = False
        self._subscribers: Dict[str, List[callable]] = {}
        
        # Метрики
        self.cache_hits = 0
        self.cache_misses = 0
        self.events_published = 0
        self.events_received = 0
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def connect(self) -> None:
        """Подключение к Redis с retry логикой"""
        try:
            self.redis = redis.from_url(
                self.redis_url,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=self.decode_responses,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Проверка подключения
            await self.redis.ping()
            self._connected = True
            
            # Инициализация pub/sub
            self.pubsub = self.redis.pubsub()
            
            logger.info("✅ Redis подключен успешно")
            
        except (RedisConnectionError, RedisError) as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Graceful отключение от Redis"""
        try:
            if self.pubsub:
                await self.pubsub.close()
            
            if self.redis:
                await self.redis.close()
            
            self._connected = False
            logger.info("✅ Redis отключен gracefully")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отключении Redis: {e}")
    
    def is_connected(self) -> bool:
        """Проверка статуса подключения"""
        return self._connected and self.redis is not None
    
    # =====================================
    # 🚀 EVENT-DRIVEN СИНХРОНИЗАЦИЯ
    # =====================================
    
    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        channel: str = "mem0_events",
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Публикация события для синхронизации
        
        Args:
            event_type: Тип события (см. RedisEventTypes)
            data: Данные события
            channel: Канал для pub/sub
            timestamp: Временная метка
            
        Returns:
            bool: Успешность публикации
        """
        if not self.is_connected():
            logger.warning("⚠️ Redis не подключен для публикации событий")
            return False
        
        try:
            event = {
                "event_type": event_type,
                "data": data,
                "timestamp": (timestamp or datetime.utcnow()).isoformat(),
                "event_id": str(uuid4()),
                "source": "mcp_mem0"
            }
            
            # Публикация события
            subscribers = await self.redis.publish(
                channel, 
                json.dumps(event, ensure_ascii=False)
            )
            
            self.events_published += 1
            logger.debug(f"📤 Событие опубликовано: {event_type} -> {subscribers} подписчиков")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации события {event_type}: {e}")
            return False
    
    async def subscribe_to_events(
        self,
        callback: callable,
        channels: List[str] = None,
        event_types: List[str] = None
    ) -> None:
        """
        Подписка на события с фильтрацией
        
        Args:
            callback: Функция обработки события
            channels: Список каналов для прослушивания
            event_types: Фильтр по типам событий
        """
        if not self.is_connected():
            logger.warning("⚠️ Redis не подключен для подписки")
            return
        
        if channels is None:
            channels = ["mem0_events"]
        
        try:
            # Подписка на каналы
            await self.pubsub.subscribe(*channels)
            
            logger.info(f"📥 Подписка на каналы: {channels}")
            
            # Обработка событий
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        event = json.loads(message["data"])
                        
                        # Фильтрация по типам событий
                        if event_types and event.get("event_type") not in event_types:
                            continue
                        
                        # Вызов callback
                        await callback(event)
                        self.events_received += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка обработки события: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Ошибка подписки на события: {e}")
    
    # =====================================
    # 💾 INTELLIGENT CACHING
    # =====================================
    
    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "cache"
    ) -> bool:
        """
        Установка значения в кэш с TTL
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Time to live в секундах
            namespace: Пространство имен для ключа
            
        Returns:
            bool: Успешность операции
        """
        if not self.is_connected():
            return False
        
        try:
            full_key = f"{namespace}:{key}"
            ttl = ttl or self.default_ttl
            
            # Сериализация значения
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            # Установка с TTL
            result = await self.redis.setex(full_key, ttl, value)
            
            logger.debug(f"💾 Кэш установлен: {full_key} (TTL: {ttl}s)")
            return bool(result)
            
        except Exception as e:
            logger.error(f"❌ Ошибка установки кэша {key}: {e}")
            return False
    
    async def cache_get(
        self,
        key: str,
        namespace: str = "cache",
        deserialize_json: bool = True
    ) -> Optional[Any]:
        """
        Получение значения из кэша
        
        Args:
            key: Ключ кэша
            namespace: Пространство имен
            deserialize_json: Автоматическая десериализация JSON
            
        Returns:
            Any: Значение из кэша или None
        """
        if not self.is_connected():
            return None
        
        try:
            full_key = f"{namespace}:{key}"
            value = await self.redis.get(full_key)
            
            if value is None:
                self.cache_misses += 1
                logger.debug(f"💨 Кэш промах: {full_key}")
                return None
            
            self.cache_hits += 1
            logger.debug(f"🎯 Кэш попадание: {full_key}")
            
            # Десериализация JSON если нужно
            if deserialize_json and isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            return value
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения кэша {key}: {e}")
            return None
    
    async def cache_delete(
        self,
        key: str,
        namespace: str = "cache"
    ) -> bool:
        """Удаление ключа из кэша"""
        if not self.is_connected():
            return False
        
        try:
            full_key = f"{namespace}:{key}"
            result = await self.redis.delete(full_key)
            
            logger.debug(f"🗑️ Кэш удален: {full_key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления кэша {key}: {e}")
            return False
    
    async def cache_clear_namespace(self, namespace: str) -> int:
        """Очистка всего namespace в кэше"""
        if not self.is_connected():
            return 0
        
        try:
            pattern = f"{namespace}:*"
            keys = await self.redis.keys(pattern)
            
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"🧹 Очищен namespace {namespace}: {deleted} ключей")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки namespace {namespace}: {e}")
            return 0
    
    # =====================================
    # 🔒 DISTRIBUTED LOCKING
    # =====================================
    
    @asynccontextmanager
    async def distributed_lock(
        self,
        resource: str,
        timeout: Optional[int] = None,
        blocking_timeout: Optional[int] = None
    ):
        """
        Distributed lock для ACID операций
        
        Args:
            resource: Имя ресурса для блокировки
            timeout: Время удержания блокировки
            blocking_timeout: Время ожидания блокировки
        """
        if not self.is_connected():
            raise RuntimeError("Redis не подключен для locking")
        
        timeout = timeout or self.lock_timeout
        lock_key = f"lock:{resource}"
        
        lock = Lock(
            self.redis,
            lock_key,
            timeout=timeout,
            blocking_timeout=blocking_timeout
        )
        
        try:
            logger.debug(f"🔒 Попытка захвата блокировки: {resource}")
            
            # Захват блокировки
            acquired = await lock.acquire()
            
            if not acquired:
                raise RedisError(f"Не удалось захватить блокировку: {resource}")
            
            logger.debug(f"✅ Блокировка захвачена: {resource}")
            yield lock
            
        finally:
            try:
                await lock.release()
                logger.debug(f"🔓 Блокировка освобождена: {resource}")
            except Exception as e:
                logger.error(f"❌ Ошибка освобождения блокировки {resource}: {e}")
    
    # =====================================
    # 📨 MESSAGE QUEUE
    # =====================================
    
    async def enqueue_task(
        self,
        queue_name: str,
        task_data: Dict[str, Any],
        priority: int = 0
    ) -> bool:
        """
        Добавление задачи в очередь
        
        Args:
            queue_name: Имя очереди
            task_data: Данные задачи
            priority: Приоритет (больше = выше приоритет)
            
        Returns:
            bool: Успешность добавления
        """
        if not self.is_connected():
            return False
        
        try:
            task = {
                "id": str(uuid4()),
                "data": task_data,
                "created_at": datetime.utcnow().isoformat(),
                "priority": priority
            }
            
            # Добавление в sorted set по приоритету
            await self.redis.zadd(
                f"queue:{queue_name}",
                {json.dumps(task, ensure_ascii=False): priority}
            )
            
            logger.debug(f"📨 Задача добавлена в очередь {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления задачи в очередь {queue_name}: {e}")
            return False
    
    async def dequeue_task(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """
        Извлечение задачи из очереди (с наивысшим приоритетом)
        
        Args:
            queue_name: Имя очереди
            
        Returns:
            Dict: Данные задачи или None
        """
        if not self.is_connected():
            return None
        
        try:
            # Извлечение элемента с наивысшим приоритетом
            result = await self.redis.zpopmax(f"queue:{queue_name}")
            
            if not result:
                return None
            
            task_json, priority = result[0]
            task = json.loads(task_json)
            
            logger.debug(f"📥 Задача извлечена из очереди {queue_name}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения задачи из очереди {queue_name}: {e}")
            return None
    
    # =====================================
    # 🔧 SESSION MANAGEMENT
    # =====================================
    
    async def create_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Создание пользовательской сессии"""
        ttl = ttl or self.session_ttl
        return await self.cache_set(
            session_id,
            data,
            ttl=ttl,
            namespace="sessions"
        )
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение данных сессии"""
        return await self.cache_get(session_id, namespace="sessions")
    
    async def update_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        extend_ttl: bool = True
    ) -> bool:
        """Обновление данных сессии"""
        if extend_ttl:
            # Продление TTL при обновлении
            await self.redis.expire(f"sessions:{session_id}", self.session_ttl)
        
        return await self.cache_set(
            session_id,
            data,
            ttl=self.session_ttl,
            namespace="sessions"
        )
    
    async def delete_session(self, session_id: str) -> bool:
        """Удаление сессии"""
        return await self.cache_delete(session_id, namespace="sessions")
    
    # =====================================
    # 📊 МОНИТОРИНГ И МЕТРИКИ
    # =====================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики Redis сервиса"""
        if not self.is_connected():
            return {"status": "disconnected"}
        
        try:
            info = await self.redis.info()
            
            return {
                "status": "connected",
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "cache_hit_ratio": self.cache_hits / max(self.cache_hits + self.cache_misses, 1),
                "events_published": self.events_published,
                "events_received": self.events_received,
                "uptime_seconds": info.get("uptime_in_seconds")
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики Redis: {e}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check для мониторинга"""
        try:
            start_time = time.time()
            
            # Проверка ping
            pong = await self.redis.ping()
            ping_time = time.time() - start_time
            
            # Проверка записи/чтения
            test_key = f"health_check:{int(time.time())}"
            await self.redis.setex(test_key, 10, "test")
            test_value = await self.redis.get(test_key)
            await self.redis.delete(test_key)
            
            return {
                "status": "healthy",
                "ping": pong,
                "response_time_ms": round(ping_time * 1000, 2),
                "read_write_test": test_value == "test",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# =====================================
# 🚀 SINGLETON INSTANCE
# =====================================

# Глобальный экземпляр Redis сервиса
redis_service: Optional[RedisService] = None


async def get_redis_service() -> RedisService:
    """Получение глобального экземпляра Redis сервиса"""
    global redis_service
    
    if redis_service is None:
        # Создание и подключение Redis сервиса
        redis_service = RedisService()
        await redis_service.connect()
    
    return redis_service


async def init_redis_service(
    redis_url: str = "redis://localhost:6379/0",
    password: Optional[str] = None,
    **kwargs
) -> RedisService:
    """Инициализация Redis сервиса с кастомными параметрами"""
    global redis_service
    
    redis_service = RedisService(
        redis_url=redis_url,
        password=password,
        **kwargs
    )
    
    await redis_service.connect()
    return redis_service


async def close_redis_service() -> None:
    """Закрытие глобального Redis сервиса"""
    global redis_service
    
    if redis_service:
        await redis_service.disconnect()
        redis_service = None 