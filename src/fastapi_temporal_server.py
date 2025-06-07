"""
🏗️ NEXT LEVEL MCP-MEM0 SERVER с TEMPORAL.IO
==============================================

УЛЬТИМАТИВНАЯ АРХИТЕКТУРА:
- 17 Enterprise Memory Tools через MCP Protocol
- Temporal.io: Workflows + Activities + Signals + Queries
- Vector Store: Семантический поиск (Supabase/Qdrant)
- Graph Store: Связи и отношения (Memgraph)
- FastAPI: RESTful API + MCP integration

ЗАМЕНА Redis → Temporal для максимальной надежности и простоты
"""

import logging
import asyncio
import os
import json
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel, Field

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp-mem0-temporal")

# Импорт модулей
try:
    from .memory_client import EnterpriseMemoryClient
    from .temporal_memory_service import TemporalMemoryService, get_temporal_service, close_temporal_service
    logger.info("✅ Temporal Memory Service импортирован (относительный импорт)")
except ImportError as e:
    logger.error(f"❌ Ошибка относительного импорта: {e}")
    # Fallback для Docker контейнера
    try:
        from src.memory_client import EnterpriseMemoryClient
        from src.temporal_memory_service import TemporalMemoryService, get_temporal_service, close_temporal_service
        logger.info("✅ Использован абсолютный импорт (Temporal включен)")
    except ImportError as e2:
        logger.error(f"❌ Ошибка абсолютного импорта: {e2}")
        # Последний fallback
        import sys
        sys.path.append('/app/src')
        from memory_client import EnterpriseMemoryClient
        from temporal_memory_service import TemporalMemoryService, get_temporal_service, close_temporal_service
        logger.info("✅ Использован sys.path импорт (Temporal включен)")


# =================== PYDANTIC MODELS ===================

class MemoryRequest(BaseModel):
    """Запрос на сохранение памяти"""
    content: str = Field(..., description="Контент для сохранения")
    user_id: str = Field(default="user", description="ID пользователя")
    agent_id: Optional[str] = Field(None, description="ID агента")
    session_id: Optional[str] = Field(None, description="ID сессии")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class SearchRequest(BaseModel):
    """Запрос на поиск в памяти"""
    query: str = Field(..., description="Поисковый запрос")
    user_id: str = Field(default="user", description="ID пользователя")
    agent_id: Optional[str] = Field(None, description="ID агента")
    session_id: Optional[str] = Field(None, description="ID сессии")
    limit: int = Field(default=5, description="Максимальное количество результатов")


class EntityRequest(BaseModel):
    """Запрос на анализ сущности"""
    entity_name: str = Field(..., description="Имя сущности для анализа")
    user_id: str = Field(default="user", description="ID пользователя")


class GetMemoriesRequest(BaseModel):
    """Запрос на получение воспоминаний"""
    user_id: str = Field(default="user", description="ID пользователя")
    agent_id: Optional[str] = Field(None, description="ID агента")
    session_id: Optional[str] = Field(None, description="ID сессии")


class VerifiedMemoryRequest(BaseModel):
    """Запрос на сохранение проверенной памяти"""
    content: str = Field(..., description="Проверенный контент")
    confidence: float = Field(default=0.9, description="Уровень уверенности")
    source: str = Field(default="verified", description="Источник информации")
    user_id: str = Field(default="user", description="ID пользователя")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")


class ProjectMilestoneRequest(BaseModel):
    """Запрос на сохранение milestone проекта"""
    milestone_name: str = Field(..., description="Название milestone")
    description: str = Field(..., description="Описание milestone")
    project_id: str = Field(..., description="ID проекта")
    user_id: str = Field(default="user", description="ID пользователя")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")


# =================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===================

memory_client: Optional[EnterpriseMemoryClient] = None
temporal_service: Optional[TemporalMemoryService] = None


# =================== LIFECYCLE MANAGEMENT ===================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения с Temporal"""
    global memory_client, temporal_service
    
    logger.info("🚀 Запуск NEXT LEVEL MCP-Mem0 Server с Temporal.io...")
    
    try:
        # Инициализация Temporal Service (ЗАМЕНА Redis)
        temporal_service = await get_temporal_service()
        logger.info("✅ Temporal Memory Service подключен")
        
        # Инициализация Memory Client
        memory_client = EnterpriseMemoryClient()
        await memory_client.initialize()
        logger.info("✅ Memory Client инициализирован")
        
        # Проверка всех компонентов
        logger.info("🎯 NEXT LEVEL ПАМЯТЬ АКТИВИРОВАНА:")
        logger.info(f"   🏛️ Temporal Workflows: АКТИВНО")
        logger.info(f"   📊 Graph Support: {memory_client.graph_support}")
        logger.info(f"   🔍 Vector Support: {memory_client.vector_support}")
        logger.info("   🚀 Все 17 Enterprise Tools готовы!")
            
        yield
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        yield
    finally:
        # Cleanup
        if memory_client:
            await memory_client.close()
        if temporal_service:
            await close_temporal_service()
        logger.info("🔒 NEXT LEVEL Server остановлен")


# =================== FASTAPI APPLICATION ===================

app = FastAPI(
    title="🏛️ NEXT LEVEL MCP-Mem0 Server с Temporal.io",
    description="17 Production-ready Memory Tools for AI Agents + Temporal Workflows",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP будет инициализирован ПОСЛЕ определения всех endpoints


# =================== DEPENDENCY INJECTION ===================

async def get_memory_client() -> EnterpriseMemoryClient:
    if not memory_client:
        raise HTTPException(status_code=503, detail="Memory client недоступен")
    return memory_client


async def get_temporal() -> TemporalMemoryService:
    if not temporal_service:
        raise HTTPException(status_code=503, detail="Temporal service недоступен")
    return temporal_service


# =================== ОСНОВНЫЕ MEMORY TOOLS с TEMPORAL ===================

@app.post("/memory/save", 
          operation_id="save_memory",
          summary="Сохранить память", 
          description="Сохраняет информацию в Graph и Vector память через Temporal Workflows")
async def save_memory(
    request: MemoryRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        # Создание или получение сессии
        session_id = request.session_id or f"auto-session-{request.user_id}"
        
        # Выполнение через Temporal Workflow
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="save",
            user_id=request.user_id,
            content=request.content,
            agent_id=request.agent_id,
            metadata=request.metadata
        )
        
        logger.info(f"✅ Memory save operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "session_id": session_id,
            "message": "Memory save operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения памяти через Temporal: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения памяти: {str(e)}")


@app.post("/memory/search",
          operation_id="search_memories", 
          summary="Поиск воспоминаний",
          description="Hybrid поиск по Graph и Vector памяти через Temporal Activities")
async def search_memories(
    request: SearchRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        # Создание или получение сессии
        session_id = request.session_id or f"auto-session-{request.user_id}"
        
        # Выполнение через Temporal Workflow
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="search",
            user_id=request.user_id,
            query=request.query,
            agent_id=request.agent_id,
            metadata={"limit": request.limit}
        )
        
        logger.info(f"✅ Memory search operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "session_id": session_id,
            "query": request.query,
            "message": "Memory search operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка поиска памяти через Temporal: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка поиска памяти: {str(e)}")


@app.post("/memory/get-all",
          operation_id="get_all_memories",
          summary="Получить все воспоминания",
          description="Получить все сохраненные воспоминания пользователя")
async def get_all_memories(
    request: GetMemoriesRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        result = await client.list_memory(
            user_id=request.user_id,
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        logger.info(f"✅ Получены все воспоминания для {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения воспоминаний: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения воспоминаний: {str(e)}")


@app.post("/memory/save-verified",
          operation_id="save_verified_memory",
          summary="Сохранить проверенную память",
          description="Сохраняет проверенную информацию с уровнем уверенности")
async def save_verified_memory(
    request: VerifiedMemoryRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        # Создание метаданных для проверенной памяти
        metadata = {
            **(request.metadata or {}),
            "confidence": request.confidence,
            "source": request.source,
            "verified": True,
            "verification_timestamp": datetime.now().isoformat()
        }
        
        session_id = f"verified-session-{request.user_id}"
        
        # Выполнение через Temporal Workflow
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="save",
            user_id=request.user_id,
            content=request.content,
            metadata=metadata
        )
        
        logger.info(f"✅ Verified memory save operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "confidence": request.confidence,
            "source": request.source,
            "message": "Verified memory save operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения проверенной памяти: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения проверенной памяти: {str(e)}")


@app.post("/memory/get-context",
          operation_id="get_accurate_context",
          summary="Получить точный контекст",
          description="Получает максимально релевантный контекст для запроса")
async def get_accurate_context(
    request: SearchRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        session_id = request.session_id or f"context-session-{request.user_id}"
        
        # Выполнение через Temporal Workflow с специальными метаданными
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="search",
            user_id=request.user_id,
            query=request.query,
            agent_id=request.agent_id,
            metadata={
                "limit": request.limit,
                "context_focused": True,
                "accuracy_priority": True
            }
        )
        
        logger.info(f"✅ Accurate context operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "session_id": session_id,
            "query": request.query,
            "context_type": "accurate",
            "message": "Accurate context operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения точного контекста: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения точного контекста: {str(e)}")


# =================== GRAPH MEMORY TOOLS с TEMPORAL ===================

@app.post("/graph/save-memory",
          operation_id="save_graph_memory",
          summary="Сохранить графовую память",
          description="Сохраняет память с извлечением графовых сущностей и связей")
async def save_graph_memory(
    request: MemoryRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        session_id = request.session_id or f"graph-session-{request.user_id}"
        
        # Выполнение через Temporal Workflow для графовых операций
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="save_graph",
            user_id=request.user_id,
            content=request.content,
            agent_id=request.agent_id,
            metadata={
                **(request.metadata or {}),
                "graph_focused": True,
                "extract_entities": True,
                "extract_relationships": True
            }
        )
        
        logger.info(f"✅ Graph memory save operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "session_id": session_id,
            "operation_type": "graph_save",
            "message": "Graph memory save operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения графовой памяти: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения графовой памяти: {str(e)}")


@app.post("/graph/search",
          operation_id="search_graph_memory",
          summary="Поиск по графовой памяти",
          description="Выполняет семантический поиск с использованием графовых связей")
async def search_graph_memory(
    request: SearchRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        session_id = request.session_id or f"graph-search-session-{request.user_id}"
        
        # Выполнение через Temporal Workflow для графового поиска
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="search_graph",
            user_id=request.user_id,
            query=request.query,
            agent_id=request.agent_id,
            metadata={
                "limit": request.limit,
                "graph_focused": True,
                "relationship_aware": True
            }
        )
        
        logger.info(f"✅ Graph memory search operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "session_id": session_id,
            "query": request.query,
            "operation_type": "graph_search",
            "message": "Graph memory search operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка поиска по графовой памяти: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка поиска по графовой памяти: {str(e)}")


# =================== ДОПОЛНИТЕЛЬНЫЕ ENTERPRISE MEMORY TOOLS ===================

@app.post("/memory/update",
          operation_id="update_memory",
          summary="Обновить память",
          description="Обновляет существующую память по ID")
async def update_memory(
    memory_id: str,
    content: str,
    user_id: str = "user",
    metadata: Optional[Dict[str, Any]] = None,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        result = await client.update_memory(
            memory_id=memory_id,
            content=content,
            user_id=user_id,
            metadata=metadata
        )
        
        logger.info(f"✅ Память обновлена: {memory_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка обновления памяти: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления памяти: {str(e)}")


@app.delete("/memory/delete/{memory_id}",
           operation_id="delete_memory",
           summary="Удалить память",
           description="Удаляет память по ID")
async def delete_memory(
    memory_id: str,
    user_id: str = "user",
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        result = await client.delete_memory(memory_id=memory_id, user_id=user_id)
        
        logger.info(f"✅ Память удалена: {memory_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка удаления памяти: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления памяти: {str(e)}")


@app.get("/memory/history/{memory_id}",
         operation_id="get_memory_history",
         summary="История памяти",
         description="Получает историю изменений памяти")
async def get_memory_history(
    memory_id: str,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        result = await client.get_memory_history(memory_id)
        
        logger.info(f"✅ История памяти получена: {memory_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения истории памяти: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории памяти: {str(e)}")


@app.get("/memory/stats",
         operation_id="get_memory_stats",
         summary="Статистика памяти",
         description="Получает статистику использования памяти")
async def get_memory_stats(
    user_id: str = "user",
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        result = await client.get_stats()
        
        logger.info(f"✅ Статистика памяти получена для {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@app.post("/memory/bulk-save",
          operation_id="bulk_save_memories",
          summary="Массовое сохранение памяти",
          description="Сохраняет несколько воспоминаний одновременно")
async def bulk_save_memories(
    memories: List[str],
    user_id: str = "user",
    agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        session_id = session_id or f"bulk-session-{user_id}"
        
        # Массовая операция через Temporal
        operations = []
        for content in memories:
            operation_id = await temporal.execute_memory_operation(
                session_id=session_id,
                operation_type="save",
                user_id=user_id,
                content=content,
                agent_id=agent_id,
                metadata=metadata
            )
            operations.append(operation_id)
        
        logger.info(f"✅ Bulk save operations sent via Temporal: {len(operations)} items")
        
        return {
            "success": True,
            "operations": operations,
            "session_id": session_id,
            "count": len(memories),
            "message": f"Bulk save operations submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка массового сохранения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка массового сохранения: {str(e)}")


@app.post("/analytics/entity-analysis",
          operation_id="analyze_entity",
          summary="Анализ сущности",
          description="Анализирует сущность и её связи в графе памяти")
async def analyze_entity(
    request: EntityRequest,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        session_id = f"entity-analysis-{request.user_id}"
        
        # Анализ сущности через Temporal
        operation_id = await temporal.execute_memory_operation(
            session_id=session_id,
            operation_type="analyze_entity",
            user_id=request.user_id,
            content=request.entity_name,
            metadata={
                "analysis_type": "entity",
                "entity_name": request.entity_name
            }
        )
        
        logger.info(f"✅ Entity analysis operation sent via Temporal: {operation_id}")
        
        return {
            "success": True,
            "operation_id": operation_id,
            "session_id": session_id,
            "entity_name": request.entity_name,
            "operation_type": "entity_analysis",
            "message": "Entity analysis operation submitted to Temporal workflow",
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка анализа сущности: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа сущности: {str(e)}")


# =================== TEMPORAL STATUS & MONITORING ===================

@app.get("/temporal/session/{session_id}",
         operation_id="get_temporal_session_state",
         summary="Статус Temporal сессии",
         description="Получает состояние Temporal workflow сессии")
async def get_temporal_session_state(
    session_id: str,
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        session_state = await temporal.get_session_state(session_id)
        
        if not session_state:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "session_state": session_state,
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния сессии: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения состояния сессии: {str(e)}")


@app.get("/temporal/health",
         operation_id="get_temporal_health",
         summary="Статус здоровья Temporal",
         description="Проверяет состояние Temporal workflows и activities")
async def get_temporal_health(
    temporal: TemporalMemoryService = Depends(get_temporal)
) -> Dict[str, Any]:
    try:
        health_status = await temporal.get_health_status()
        
        return {
            "success": True,
            "temporal_health": health_status,
            "temporal_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса здоровья Temporal: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса здоровья: {str(e)}")


# =================== СИСТЕМНЫЕ ENDPOINTS ===================

@app.get("/health")
async def health() -> Dict[str, Any]:
    """Комплексная проверка состояния всех компонентов"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "fastapi": "healthy",
                "temporal": "checking...",
                "memory_client": "checking...",
                "graph_store": "unknown",
                "vector_store": "unknown"
            },
            "architecture": "NEXT_LEVEL",
            "version": "3.0.0"
        }
        
        # Проверка Memory Client
        try:
            if memory_client:
                client_health = await memory_client.health_check()
                health_data["components"]["memory_client"] = "healthy"
                health_data["components"]["graph_store"] = "healthy" if memory_client.graph_support else "unavailable"
                health_data["components"]["vector_store"] = "healthy" if memory_client.vector_support else "unavailable"
            else:
                health_data["components"]["memory_client"] = "unavailable"
        except Exception as e:
            health_data["components"]["memory_client"] = f"unhealthy: {str(e)}"
        
        # Проверка Temporal
        try:
            if temporal_service:
                temporal_health = await temporal_service.get_health_status()
                health_data["components"]["temporal"] = "healthy" if temporal_health.get("status") != "error" else "unhealthy"
                health_data["temporal_details"] = temporal_health
            else:
                health_data["components"]["temporal"] = "unavailable"
        except Exception as e:
            health_data["components"]["temporal"] = f"unhealthy: {str(e)}"
        
        # Определение общего статуса
        if any("unhealthy" in str(status) or "unavailable" in str(status) 
               for status in health_data["components"].values()):
            health_data["status"] = "degraded"
        
        return health_data
        
    except Exception as e:
        logger.error(f"❌ Ошибка health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "architecture": "NEXT_LEVEL",
            "version": "3.0.0"
        }


@app.get("/")
async def root() -> Dict[str, Any]:
    """Информация о системе"""
    return {
        "title": "🏛️ NEXT LEVEL MCP-Mem0 Server с Temporal.io",
        "description": "Ультимативная память для AI агентов",
        "version": "3.0.0",
        "architecture": {
            "workflow_engine": "Temporal.io",
            "vector_store": "Supabase/Qdrant",
            "graph_store": "Memgraph",
            "api_protocol": "MCP + REST",
            "reliability": "NEXT_LEVEL"
        },
        "features": [
            "17 Enterprise Memory Tools",
            "Temporal Workflows для coordination",
            "Temporal Activities для operations", 
            "Temporal Signals для real-time communication",
            "Vector + Graph unified memory",
            "MCP Protocol support",
            "Production-ready reliability"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "mcp": "/mcp",
            "temporal_health": "/temporal/health"
        },
        "timestamp": datetime.now().isoformat()
    }


# =================== MCP INTEGRATION ===================

# Создание MCP сервера ПОСЛЕ определения всех endpoints
from fastapi_mcp import FastApiMCP

mcp = FastApiMCP(app)

# Монтирование MCP эндпоинта
mcp.mount()

logger.info("✅ FastAPI-MCP интегрирован: /mcp endpoint активен")
logger.info("🎯 Все 17 Enterprise Memory Tools экспортированы в MCP Protocol")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_temporal_server:app",
        host="0.0.0.0",
        port=8051,
        reload=True,
        log_level="info"
    )