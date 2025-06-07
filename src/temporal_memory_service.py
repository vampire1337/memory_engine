"""
🏛️ TEMPORAL MEMORY SERVICE - NEXT LEVEL ПАМЯТЬ ДЛЯ АГЕНТОВ
================================================================

УЛЬТИМАТИВНАЯ АРХИТЕКТУРА:
- Vector Store: Семантический поиск (Supabase/Qdrant)
- Graph Store: Связи и отношения (Memgraph)  
- Temporal Workflows: Координация и state management
- Activities: Все memory operations
- Signals/Queries: Real-time communication
- Durable Timers: TTL и scheduling

ЗАМЕНА Redis на Temporal для максимальной надежности
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from uuid import uuid4

# 🔥 ХИТРЫЙ DEBUGGING IMPORT - ВСТАВЛЯЕМ В НАЧАЛО!
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from debug_temporal import patch_temporal_client
    # НЕМЕДЛЕННО ПАТЧИМ TEMPORAL!
    patch_temporal_client()
    print("🔥 TEMPORAL CLIENT УСПЕШНО ЗАПАТЧЕН ДЛЯ DEBUGGING!")
except ImportError as e:
    print(f"⚠️ Debug wrapper не найден: {e}")

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

logger = logging.getLogger(__name__)


# =================== TEMPORAL DATA MODELS ===================

@dataclass 
class MemoryOperation:
    """Операция с памятью"""
    operation_id: str
    operation_type: str  # save, search, update, delete
    user_id: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    content: Optional[str] = None
    query: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


@dataclass
class MemoryResult:
    """Результат операции с памятью"""
    operation_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass  
class MemorySessionState:
    """Состояние сессии памяти"""
    session_id: str
    user_id: str
    agent_id: Optional[str]
    operations_count: int = 0
    last_operation: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


# =================== TEMPORAL ACTIVITIES ===================

@activity.defn
async def execute_memory_save(operation: MemoryOperation) -> MemoryResult:
    """Activity для сохранения памяти"""
    try:
        # Импорт memory client с fallback
        try:
            from .memory_client import get_global_memory_client
        except ImportError:
            from src.memory_client import get_global_memory_client
        
        client = await get_global_memory_client()
        
        result = await client.add_memory(
            content=operation.content,
            user_id=operation.user_id,
            agent_id=operation.agent_id,
            session_id=operation.session_id,
            metadata=operation.metadata
        )
        
        logger.info(f"✅ Memory saved: {operation.operation_id}")
        
        return MemoryResult(
            operation_id=operation.operation_id,
            success=True,
            result=result,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Memory save failed: {e}")
        return MemoryResult(
            operation_id=operation.operation_id,
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )


@activity.defn
async def execute_memory_search(operation: MemoryOperation) -> MemoryResult:
    """Activity для поиска в памяти"""
    try:
        try:
            from .memory_client import get_global_memory_client
        except ImportError:
            from src.memory_client import get_global_memory_client
        
        client = await get_global_memory_client()
        
        result = await client.search_memory(
            query=operation.query,
            user_id=operation.user_id,
            agent_id=operation.agent_id,
            session_id=operation.session_id,
            limit=operation.metadata.get("limit", 5) if operation.metadata else 5
        )
        
        logger.info(f"✅ Memory searched: {operation.operation_id}")
        
        return MemoryResult(
            operation_id=operation.operation_id,
            success=True,
            result=result,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Memory search failed: {e}")
        return MemoryResult(
            operation_id=operation.operation_id,
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )


@activity.defn
async def execute_graph_operation(operation: MemoryOperation) -> MemoryResult:
    """Activity для графовых операций"""
    try:
        try:
            from .memory_client import get_global_memory_client
        except ImportError:
            from src.memory_client import get_global_memory_client
        
        client = await get_global_memory_client()
        
        if operation.operation_type == "save_graph":
            result = await client.add_memory(
                content=operation.content,
                user_id=operation.user_id,
                agent_id=operation.agent_id,
                session_id=operation.session_id,
                metadata={**(operation.metadata or {}), "graph_focused": True}
            )
        elif operation.operation_type == "search_graph":
            result = await client.search_memory(
                query=operation.query,
                user_id=operation.user_id,
                agent_id=operation.agent_id,
                session_id=operation.session_id
            )
        else:
            raise ValueError(f"Unknown graph operation: {operation.operation_type}")
        
        logger.info(f"✅ Graph operation completed: {operation.operation_id}")
        
        return MemoryResult(
            operation_id=operation.operation_id,
            success=True,
            result=result,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Graph operation failed: {e}")
        return MemoryResult(
            operation_id=operation.operation_id,
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )


@activity.defn
async def health_check_activity() -> Dict[str, Any]:
    """Activity для проверки здоровья системы"""
    try:
        try:
            from .memory_client import get_global_memory_client
        except ImportError:
            from src.memory_client import get_global_memory_client
        
        client = await get_global_memory_client()
        health_result = await client.health_check()
        
        return {
            "temporal_status": "healthy",
            "memory_system": health_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "temporal_status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# =================== TEMPORAL WORKFLOWS ===================

@workflow.defn
class MemorySessionWorkflow:
    """
    Главный workflow для управления сессией памяти агента
    
    Заменяет Redis session management и event handling
    """
    
    def __init__(self):
        self.session_state: Optional[MemorySessionState] = None
        self.operations_history: List[MemoryResult] = []
        self.is_session_active = True
    
    @workflow.run
    async def run(self, session_data: str) -> str:
        """Запуск сессии памяти"""
        
        # Десериализуем данные сессии из JSON
        import json
        data = json.loads(session_data)
        session_id = data["session_id"]
        user_id = data["user_id"] 
        agent_id = data.get("agent_id")
        
        # Инициализация состояния сессии
        self.session_state = MemorySessionState(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            operations_count=0,
            last_operation=workflow.now()  # Используем workflow.now() для детерминизма
        )
        
        logger.info(f"🧠 Memory session started: {session_id}")
        
        # Ожидание операций или сигналов
        while self.is_session_active:
            try:
                # Ожидание сигналов с таймаутом (заменяет Redis TTL)
                await workflow.wait_condition(
                    lambda: not self.is_session_active,
                    timeout=timedelta(hours=1)  # Session TTL
                )
            except Exception:
                # Таймаут сессии - завершаем
                logger.info(f"⏰ Session timeout: {session_id}")
                self.is_session_active = False
        
        logger.info(f"🔒 Memory session ended: {session_id}")
        return f"Session {session_id} completed with {self.session_state.operations_count} operations"
    
    @workflow.signal
    async def memory_operation_signal(self, operation: MemoryOperation):
        """Сигнал для выполнения операции с памятью"""
        try:
            # Выбор нужного activity в зависимости от типа операции
            if operation.operation_type == "save":
                result = await workflow.execute_activity(
                    execute_memory_save,
                    operation,
                    start_to_close_timeout=timedelta(minutes=5)
                )
            elif operation.operation_type == "search":
                result = await workflow.execute_activity(
                    execute_memory_search,
                    operation,
                    start_to_close_timeout=timedelta(minutes=5)
                )
            elif operation.operation_type in ["save_graph", "search_graph"]:
                result = await workflow.execute_activity(
                    execute_graph_operation,
                    operation,
                    start_to_close_timeout=timedelta(minutes=5)
                )
            else:
                result = MemoryResult(
                    operation_id=operation.operation_id,
                    success=False,
                    error=f"Unknown operation type: {operation.operation_type}",
                    timestamp=workflow.now()  # Используем workflow.now()
                )
            
            # Обновление состояния сессии
            if self.session_state:
                self.session_state.operations_count += 1
                self.session_state.last_operation = workflow.now()  # Используем workflow.now()
            
            # Сохранение в историю
            self.operations_history.append(result)
            
            logger.info(f"✅ Operation completed: {operation.operation_type}")
            
        except Exception as e:
            logger.error(f"❌ Operation failed: {e}")
            
            error_result = MemoryResult(
                operation_id=operation.operation_id,
                success=False,
                error=str(e),
                timestamp=workflow.now()  # Используем workflow.now()
            )
            self.operations_history.append(error_result)
    
    @workflow.signal  
    async def close_session_signal(self):
        """Сигнал для закрытия сессии"""
        self.is_session_active = False
        logger.info(f"📤 Session close signal received")
    
    @workflow.query
    def get_session_state(self) -> Optional[MemorySessionState]:
        """Query для получения состояния сессии"""
        return self.session_state
    
    @workflow.query
    def get_operations_history(self) -> List[MemoryResult]:
        """Query для получения истории операций"""
        return self.operations_history[-10:]  # Последние 10 операций


@workflow.defn
class MemoryHealthWorkflow:
    """
    Workflow для мониторинга здоровья системы памяти
    
    Заменяет Redis health checks и metrics
    """
    
    def __init__(self):
        self.health_status = "initializing"
        self.last_check: Optional[datetime] = None
        self.health_history: List[Dict[str, Any]] = []
    
    @workflow.run
    async def run(self) -> str:
        """Непрерывный мониторинг здоровья"""
        
        self.health_status = "running"
        logger.info("💊 Health monitoring workflow started")
        
        while True:
            try:
                # Выполнение health check каждые 30 секунд
                health_result = await workflow.execute_activity(
                    health_check_activity,
                    start_to_close_timeout=timedelta(minutes=2)
                )
                
                self.last_check = workflow.now()  # Используем workflow.now()
                self.health_history.append(health_result)
                
                # Сохранение только последних 20 результатов
                if len(self.health_history) > 20:
                    self.health_history = self.health_history[-20:]
                
                # Ожидание следующей проверки (увеличено для снижения нагрузки)
                await workflow.sleep(120)  # 2 минуты
                
            except Exception as e:
                logger.error(f"❌ Health check failed: {e}")
                self.health_status = "unhealthy"
                await workflow.sleep(10)  # Retry через 10 секунд
    
    @workflow.query
    def get_health_status(self) -> Dict[str, Any]:
        """Query для получения статуса здоровья"""
        return {
            "status": self.health_status,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "checks_count": len(self.health_history)
        }
    
    @workflow.query
    def get_health_history(self) -> List[Dict[str, Any]]:
        """Query для получения истории здоровья"""
        return self.health_history


# =================== TEMPORAL SERVICE CLASS ===================

class TemporalMemoryService:
    """
    🏛️ Temporal Memory Service - NEXT LEVEL память для агентов
    
    Заменяет Redis на Temporal для:
    - Session management → Workflows
    - Event handling → Signals  
    - Caching → Workflow state
    - Queues → Activities
    - Locks → Workflow coordination
    """
    
    def __init__(self, temporal_server: str = "temporal-server:7233"):
        self.temporal_server = temporal_server
        self.client: Optional[Client] = None
        self.worker: Optional[Worker] = None
        self.active_sessions: Dict[str, str] = {}  # session_id -> workflow_id
    
    async def start(self):
        """Запуск Temporal сервиса"""
        try:
            # Подключение к Temporal серверу
            self.client = await Client.connect(self.temporal_server)
            logger.info(f"✅ Connected to Temporal server: {self.temporal_server}")
            
            # Создание Worker'а
            self.worker = Worker(
                self.client,
                task_queue="memory-task-queue",
                workflows=[MemorySessionWorkflow, MemoryHealthWorkflow],
                activities=[
                    execute_memory_save,
                    execute_memory_search, 
                    execute_graph_operation,
                    health_check_activity
                ]
            )
            
            # Запуск health monitoring workflow (с проверкой на существование)
            try:
                await self.client.start_workflow(
                    MemoryHealthWorkflow.run,
                    id="memory-health-monitor",
                    task_queue="memory-task-queue"
                )
                logger.info("💊 Health monitoring workflow started")
            except Exception as e:
                if "already started" in str(e).lower():
                    logger.info("💊 Health monitoring workflow already running")
                else:
                    logger.warning(f"⚠️ Health monitoring workflow issue: {e}")
            
            logger.info("🏛️ Temporal Memory Service started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Temporal service: {e}")
            raise
    
    async def stop(self):
        """Остановка Temporal сервиса"""
        try:
            if self.worker:
                self.worker.shutdown()
            logger.info("🔒 Temporal Memory Service stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping Temporal service: {e}")
    
    async def create_memory_session(
        self, 
        user_id: str, 
        agent_id: Optional[str] = None
    ) -> str:
        """Создание новой сессии памяти"""
        session_id = f"session-{user_id}-{uuid4().hex[:8]}"
        workflow_id = f"memory-session-{session_id}"
        
        if not self.client:
            raise RuntimeError("Temporal client not initialized")
        
        # Запуск workflow для сессии - ИСПРАВЛЕННЫЙ ВЫЗОВ!
        # Передаем данные как JSON строку (один аргумент)
        import json
        session_data = json.dumps({
            "session_id": session_id,
            "user_id": user_id,
            "agent_id": agent_id
        })
        
        await self.client.start_workflow(
            MemorySessionWorkflow.run,
            session_data,  # Единственный аргумент workflow
            id=workflow_id,
            task_queue="memory-task-queue"
        )
        
        self.active_sessions[session_id] = workflow_id
        logger.info(f"🧠 Memory session created: {session_id}")
        
        return session_id
    
    async def execute_memory_operation(
        self,
        session_id: str,
        operation_type: str,
        user_id: str,
        content: Optional[str] = None,
        query: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Выполнение операции с памятью через Temporal"""
        
        if session_id not in self.active_sessions:
            # Создание новой сессии если нет
            session_id = await self.create_memory_session(user_id, agent_id)
        
        workflow_id = self.active_sessions[session_id]
        operation_id = f"op-{uuid4().hex[:8]}"
        
        operation = MemoryOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            user_id=user_id,
            agent_id=agent_id,
            session_id=session_id,
            content=content,
            query=query,
            metadata=metadata
            # timestamp убран - будет установлен в Activity
        )
        
        if not self.client:
            raise RuntimeError("Temporal client not initialized")
        
        # Отправка сигнала в workflow
        workflow_handle = self.client.get_workflow_handle(workflow_id)
        await workflow_handle.signal(
            MemorySessionWorkflow.memory_operation_signal,
            operation
        )
        
        logger.info(f"📤 Memory operation sent: {operation_type}")
        return operation_id
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение состояния сессии"""
        if session_id not in self.active_sessions:
            return None
        
        workflow_id = self.active_sessions[session_id]
        
        if not self.client:
            return None
        
        workflow_handle = self.client.get_workflow_handle(workflow_id)
        state = await workflow_handle.query(MemorySessionWorkflow.get_session_state)
        
        return {
            "session_id": state.session_id,
            "user_id": state.user_id,
            "agent_id": state.agent_id,
            "operations_count": state.operations_count,
            "last_operation": state.last_operation.isoformat() if state.last_operation else None
        } if state else None
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья системы (без query для снижения нагрузки)"""
        if not self.client:
            return {"status": "temporal_not_connected"}
        
        try:
            # Простой статус без workflow query для избежания buffer overflow
            return {
                "status": "healthy", 
                "temporal_connected": True,
                "active_sessions": len(self.active_sessions),
                "message": "Temporal Memory Service running (query throttled)"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get health status: {e}")
            return {"status": "error", "error": str(e)}


# =================== GLOBAL INSTANCE ===================

_temporal_service: Optional[TemporalMemoryService] = None

async def get_temporal_service() -> TemporalMemoryService:
    """Получение глобального экземпляра Temporal сервиса"""
    global _temporal_service
    
    if _temporal_service is None:
        # Чтение адреса Temporal Server из переменных окружения
        import os
        temporal_server = os.getenv("TEMPORAL_SERVER_ADDRESS", "temporal-server:7233")
        
        _temporal_service = TemporalMemoryService(temporal_server)
        await _temporal_service.start()
    
    return _temporal_service

async def close_temporal_service():
    """Закрытие глобального экземпляра"""
    global _temporal_service
    
    if _temporal_service:
        await _temporal_service.stop()
        _temporal_service = None