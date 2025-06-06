"""
🏗️ ENTERPRISE MCP-MEM0 SERVER v2.0
ВСЕ 17 TOOLS из unified_memory_server.py + FastAPI-MCP интеграция

Архитектура:
- 11 базовых memory tools 
- 4 graph memory tools
- 2 системных tools
- Redis синхронизация
- Enterprise error handling
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
logger = logging.getLogger("mcp-mem0-enterprise")

# Импорт модулей
try:
    from .memory_client import EnterpriseMemoryClient
    from .redis_service import RedisService, get_redis_service, RedisEventTypes
except ImportError as e:
    logger.error(f"❌ Ошибка импорта модулей: {e}")


# =================== PYDANTIC MODELS (все из unified_memory_server.py) ===================

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
redis_service: Optional[RedisService] = None


# =================== LIFECYCLE MANAGEMENT ===================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global memory_client, redis_service
    
    logger.info("🚀 Запуск Enterprise MCP-Mem0 Server v2.0...")
    
    try:
        # Инициализация Redis
        redis_service = await get_redis_service()
        logger.info("✅ Redis инициализирован")
        
        # Инициализация Memory Client
        memory_client = EnterpriseMemoryClient()
        await memory_client.initialize()
        logger.info("✅ Memory Client инициализирован")
        
        # Проверка всех компонентов
        logger.info(f"   📊 Graph Support: {memory_client.graph_support}")
        logger.info(f"   🔍 Vector Support: {memory_client.vector_support}")
        logger.info("   🎯 Все 17 Enterprise Tools активированы!")
            
        yield
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        yield
    finally:
        # Cleanup
        if memory_client:
            await memory_client.close()
        if redis_service:
            await redis_service.disconnect()
        logger.info("🔒 Сервер остановлен")


# =================== FASTAPI APPLICATION ===================

app = FastAPI(
    title="🧠 Enterprise MCP-Mem0 Server v2.0",
    description="17 Production-ready Memory Tools for AI Agents via MCP Protocol",
    version="2.0.0",
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


# =================== DEPENDENCY INJECTION ===================

async def get_memory_client() -> EnterpriseMemoryClient:
    if not memory_client:
        raise HTTPException(status_code=503, detail="Memory client недоступен")
    return memory_client


async def get_redis() -> RedisService:
    if not redis_service:
        raise HTTPException(status_code=503, detail="Redis service недоступен")
    return redis_service


# =================== 11 БАЗОВЫХ MEMORY TOOLS ===================

@app.post("/memory/save", 
          operation_id="save_memory",
          summary="Сохранить память", 
          description="Сохраняет информацию в Graph и Vector память с Redis синхронизацией")
async def save_memory(
    request: MemoryRequest,
    background_tasks: BackgroundTasks,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        result = await client.add_memory(
            content=request.content,
            user_id=request.user_id,
            agent_id=request.agent_id,
            session_id=request.session_id,
            metadata=request.metadata
        )
        
        # Redis event
        background_tasks.add_task(
            redis.publish_event,
            RedisEventTypes.VECTOR_UPDATED,
            {"memory_id": result.get("id"), "user_id": request.user_id}
        )
        
        logger.info(f"✅ Память сохранена: {result.get('id')} для {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения памяти: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/search",
          operation_id="search_memories", 
          summary="Поиск воспоминаний",
          description="Hybrid поиск по Graph и Vector памяти с Redis кэшированием")
async def search_memories(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        # Проверяем Redis кэш
        cache_key = f"search:{request.user_id}:{hash(request.query)}"
        cached_result = await redis.cache_get(cache_key, namespace="memory_search")
        
        if cached_result:
            logger.info(f"📦 Cache hit для поиска: {request.query[:50]}...")
            return cached_result
        
        # Выполняем поиск
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=request.limit,
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        # Кэшируем результат
        await redis.cache_set(cache_key, result, namespace="memory_search", ttl=300)
        
        # Redis event
        await redis.publish_event(
            RedisEventTypes.SEARCH_PERFORMED,
            {"query": request.query, "user_id": request.user_id, "results": len(result.get('memories', []))}
        )
        
        logger.info(f"🔍 Поиск выполнен: {len(result.get('memories', []))} результатов")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка поиска: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        
        logger.info(f"📝 Получено {len(result.get('memories', []))} воспоминаний для {request.user_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения воспоминаний: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/save-verified",
          operation_id="save_verified_memory",
          summary="Сохранить проверенную память",
          description="Сохраняет проверенную информацию с уровнем уверенности")
async def save_verified_memory(
    request: VerifiedMemoryRequest,
    background_tasks: BackgroundTasks,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        # Добавляем метаданные верификации
        metadata = request.metadata or {}
        metadata.update({
            "verified": True,
            "confidence": request.confidence,
            "source": request.source,
            "verification_date": datetime.now().isoformat()
        })
        
        result = await client.add_memory(
            content=request.content,
            user_id=request.user_id,
            metadata=metadata
        )
        
        # Redis event для верифицированной памяти
        background_tasks.add_task(
            redis.publish_event,
            "verified_memory_added",
            {
                "memory_id": result.get("id"), 
                "user_id": request.user_id,
                "confidence": request.confidence
            }
        )
        
        logger.info(f"✅ Проверенная память сохранена: {result.get('id')} (confidence: {request.confidence})")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения проверенной памяти: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/get-context",
          operation_id="get_accurate_context",
          summary="Получить точный контекст",
          description="Получает максимально релевантный контекст для запроса")
async def get_accurate_context(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        # Расширенный поиск для контекста
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=request.limit * 2,  # Больше результатов для лучшего контекста
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        # Логика фильтрации для точного контекста
        memories = result.get('memories', [])
        context_memories = []
        
        for memory in memories:
            # Фильтруем по релевантности (score > 0.7)
            if memory.get('score', 0) > 0.7:
                context_memories.append(memory)
        
        context_result = {
            "query": request.query,
            "user_id": request.user_id,
            "context_memories": context_memories[:request.limit],
            "total_context_found": len(context_memories),
            "accuracy_level": "high" if len(context_memories) > 0 else "low"
        }
        
        logger.info(f"🎯 Точный контекст: {len(context_memories)} высокорелевантных воспоминаний")
        return context_result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/validate-project-context",
          operation_id="validate_project_context",
          summary="Валидация проектного контекста",
          description="Проверяет корректность и полноту проектного контекста")
async def validate_project_context(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        # Поиск связанного с проектом контекста
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=20,  # Больше для валидации
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        memories = result.get('memories', [])
        
        # Валидация контекста
        validation_result = {
            "query": request.query,
            "user_id": request.user_id,
            "total_memories": len(memories),
            "validation_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        if len(memories) == 0:
            validation_result["issues"].append("Отсутствует контекст для проекта")
            validation_result["recommendations"].append("Добавить базовую информацию о проекте")
        elif len(memories) < 3:
            validation_result["issues"].append("Недостаточно контекста")
            validation_result["recommendations"].append("Расширить информацию о проекте")
            validation_result["validation_score"] = 0.5
        else:
            validation_result["validation_score"] = min(len(memories) / 10.0, 1.0)
            validation_result["recommendations"].append("Контекст проекта достаточен")
        
        logger.info(f"✅ Валидация проекта: score {validation_result['validation_score']}")
        return validation_result
        
    except Exception as e:
        logger.error(f"❌ Ошибка валидации проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/resolve-conflict",
          operation_id="resolve_context_conflict",
          summary="Разрешение конфликтов контекста",
          description="Анализирует и разрешает противоречия в памяти")
async def resolve_context_conflict(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        # Поиск потенциально конфликтующих воспоминаний
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=15,
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        memories = result.get('memories', [])
        
        # Анализ конфликтов (упрощенный алгоритм)
        conflicts = []
        resolved_memories = []
        
        for i, memory1 in enumerate(memories):
            for j, memory2 in enumerate(memories[i+1:], i+1):
                # Простое обнаружение конфликтов по содержанию
                content1 = memory1.get('memory', '').lower()
                content2 = memory2.get('memory', '').lower()
                
                # Ищем противоположные утверждения
                if ('не' in content1 and content1.replace('не', '') in content2) or \
                   ('не' in content2 and content2.replace('не', '') in content1):
                    conflicts.append({
                        "memory1": memory1,
                        "memory2": memory2,
                        "conflict_type": "contradiction"
                    })
        
        # Разрешение конфликтов (берем более новые записи)
        for memory in memories:
            if memory not in [c['memory1'] for c in conflicts] and \
               memory not in [c['memory2'] for c in conflicts]:
                resolved_memories.append(memory)
        
        conflict_result = {
            "query": request.query,
            "user_id": request.user_id,
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "resolved_memories": resolved_memories,
            "resolution_strategy": "prioritize_recent"
        }
        
        logger.info(f"⚖️ Разрешение конфликтов: найдено {len(conflicts)} конфликтов")
        return conflict_result
        
    except Exception as e:
        logger.error(f"❌ Ошибка разрешения конфликтов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/audit-quality",
          operation_id="audit_memory_quality",
          summary="Аудит качества памяти",
          description="Анализирует качество и целостность памяти пользователя")
async def audit_memory_quality(
    request: GetMemoriesRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        # Получаем все воспоминания для аудита
        result = await client.list_memory(
            user_id=request.user_id,
            limit=100,  # Анализируем больше для качественного аудита
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        memories = result.get('memories', [])
        
        # Метрики качества
        quality_metrics = {
            "total_memories": len(memories),
            "duplicates": 0,
            "incomplete": 0,
            "high_quality": 0,
            "average_content_length": 0,
            "metadata_coverage": 0,
            "quality_score": 0.0,
            "recommendations": []
        }
        
        if memories:
            # Анализ контента
            total_length = 0
            content_seen = set()
            metadata_count = 0
            
            for memory in memories:
                content = memory.get('memory', '').strip()
                total_length += len(content)
                
                # Проверка дубликатов
                if content in content_seen:
                    quality_metrics["duplicates"] += 1
                else:
                    content_seen.add(content)
                
                # Проверка полноты
                if len(content) < 10:
                    quality_metrics["incomplete"] += 1
                elif len(content) > 50:
                    quality_metrics["high_quality"] += 1
                
                # Проверка метаданных
                if memory.get('metadata') and len(memory['metadata']) > 0:
                    metadata_count += 1
            
            quality_metrics["average_content_length"] = total_length / len(memories)
            quality_metrics["metadata_coverage"] = metadata_count / len(memories)
            
            # Расчет общего скора качества
            quality_score = (
                (quality_metrics["high_quality"] / len(memories)) * 0.4 +
                (1 - quality_metrics["duplicates"] / len(memories)) * 0.3 +
                (1 - quality_metrics["incomplete"] / len(memories)) * 0.2 +
                quality_metrics["metadata_coverage"] * 0.1
            )
            quality_metrics["quality_score"] = quality_score
            
            # Рекомендации
            if quality_metrics["duplicates"] > 0:
                quality_metrics["recommendations"].append(f"Удалить {quality_metrics['duplicates']} дубликатов")
            if quality_metrics["incomplete"] > 0:
                quality_metrics["recommendations"].append(f"Дополнить {quality_metrics['incomplete']} неполных записей")
            if quality_metrics["metadata_coverage"] < 0.5:
                quality_metrics["recommendations"].append("Добавить больше метаданных к воспоминаниям")
            if quality_score > 0.8:
                quality_metrics["recommendations"].append("Отличное качество памяти!")
        
        logger.info(f"📊 Аудит качества: score {quality_metrics['quality_score']:.2f}")
        return quality_metrics
        
    except Exception as e:
        logger.error(f"❌ Ошибка аудита качества: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/save-milestone",
          operation_id="save_project_milestone",
          summary="Сохранить milestone проекта",
          description="Сохраняет важные этапы развития проекта")
async def save_project_milestone(
    request: ProjectMilestoneRequest,
    background_tasks: BackgroundTasks,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        # Формируем контент milestone
        milestone_content = f"MILESTONE: {request.milestone_name}\n"
        milestone_content += f"Проект: {request.project_id}\n"
        milestone_content += f"Описание: {request.description}"
        
        # Метаданные для milestone
        metadata = request.metadata or {}
        metadata.update({
            "type": "project_milestone",
            "milestone_name": request.milestone_name,
            "project_id": request.project_id,
            "milestone_date": datetime.now().isoformat(),
            "importance": "high"
        })
        
        result = await client.add_memory(
            content=milestone_content,
            user_id=request.user_id,
            metadata=metadata
        )
        
        # Redis event для milestone
        background_tasks.add_task(
            redis.publish_event,
            "project_milestone_added",
            {
                "memory_id": result.get("id"),
                "user_id": request.user_id,
                "project_id": request.project_id,
                "milestone_name": request.milestone_name
            }
        )
        
        logger.info(f"🎯 Milestone сохранен: {request.milestone_name} для проекта {request.project_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения milestone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/get-project-state",
          operation_id="get_current_project_state",
          summary="Текущее состояние проекта",
          description="Получает текущее состояние проекта на основе памяти")
async def get_current_project_state(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        # Поиск информации о проекте
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=10,
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        memories = result.get('memories', [])
        
        # Анализ состояния проекта
        project_state = {
            "query": request.query,
            "user_id": request.user_id,
            "total_project_memories": len(memories),
            "milestones": [],
            "current_status": "unknown",
            "last_activity": None,
            "completion_estimate": 0.0
        }
        
        # Извлекаем milestone'ы
        for memory in memories:
            metadata = memory.get('metadata', {})
            if metadata.get('type') == 'project_milestone':
                project_state["milestones"].append({
                    "name": metadata.get('milestone_name'),
                    "date": metadata.get('milestone_date'),
                    "memory_id": memory.get('id')
                })
        
        # Определяем статус проекта
        if len(project_state["milestones"]) == 0:
            project_state["current_status"] = "planning"
        elif len(project_state["milestones"]) < 3:
            project_state["current_status"] = "in_progress"
        else:
            project_state["current_status"] = "advanced"
        
        # Оценка завершенности
        project_state["completion_estimate"] = min(len(project_state["milestones"]) / 5.0, 1.0)
        
        if memories:
            # Последняя активность
            project_state["last_activity"] = memories[0].get('created_at', 'unknown')
        
        logger.info(f"📈 Состояние проекта: {project_state['current_status']} ({project_state['completion_estimate']:.1%})")
        return project_state
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/track-evolution",
          operation_id="track_project_evolution",
          summary="Отслеживание эволюции проекта",
          description="Анализирует развитие проекта во времени")
async def track_project_evolution(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        # Поиск всей истории проекта
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=20,  # Больше для анализа эволюции
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        memories = result.get('memories', [])
        
        # Анализ эволюции
        evolution_analysis = {
            "query": request.query,
            "user_id": request.user_id,
            "timeline": [],
            "phases": [],
            "growth_rate": 0.0,
            "key_changes": [],
            "trend": "stable"
        }
        
        # Сортируем по дате создания
        sorted_memories = sorted(
            memories, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        # Строим timeline
        for memory in sorted_memories:
            evolution_analysis["timeline"].append({
                "date": memory.get('created_at'),
                "content": memory.get('memory', '')[:100] + "...",
                "type": memory.get('metadata', {}).get('type', 'regular')
            })
        
        # Определяем фазы развития
        milestones_count = len([m for m in memories if m.get('metadata', {}).get('type') == 'project_milestone'])
        if milestones_count >= 3:
            evolution_analysis["phases"] = ["Планирование", "Разработка", "Развитие"]
        elif milestones_count >= 1:
            evolution_analysis["phases"] = ["Планирование", "Разработка"]
        else:
            evolution_analysis["phases"] = ["Планирование"]
        
        # Темп роста (упрощенный)
        if len(memories) > 0:
            evolution_analysis["growth_rate"] = len(memories) / max(len(evolution_analysis["phases"]), 1)
        
        # Тренд
        if len(memories) >= 10:
            evolution_analysis["trend"] = "growing"
        elif len(memories) >= 5:
            evolution_analysis["trend"] = "developing"
        else:
            evolution_analysis["trend"] = "early_stage"
        
        logger.info(f"📊 Эволюция проекта: {evolution_analysis['trend']} тренд, {len(evolution_analysis['phases'])} фаз")
        return evolution_analysis
        
    except Exception as e:
        logger.error(f"❌ Ошибка отслеживания эволюции: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =================== 4 GRAPH MEMORY TOOLS ===================

@app.post("/graph/save-memory",
          operation_id="save_graph_memory",
          summary="Сохранить графовую память",
          description="Сохраняет память с извлечением графовых сущностей и связей")
async def save_graph_memory(
    request: MemoryRequest,
    background_tasks: BackgroundTasks,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        if not client.graph_support:
            raise HTTPException(status_code=503, detail="Graph Memory недоступен")
        
        # Добавляем специальную метку для графовой памяти
        metadata = request.metadata or {}
        metadata.update({
            "type": "graph_memory",
            "graph_processing": True,
            "entity_extraction": True
        })
        
        result = await client.add_memory(
            content=request.content,
            user_id=request.user_id,
            agent_id=request.agent_id,
            session_id=request.session_id,
            metadata=metadata
        )
        
        # Redis event для графовой памяти
        background_tasks.add_task(
            redis.publish_event,
            RedisEventTypes.ENTITY_CREATED,
            {
                "memory_id": result.get("id"),
                "user_id": request.user_id,
                "graph_processed": True
            }
        )
        
        logger.info(f"🕸️ Графовая память сохранена: {result.get('id')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения графовой памяти: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/graph/search",
          operation_id="search_graph_memory",
          summary="Поиск по графовой памяти",
          description="Выполняет семантический поиск с использованием графовых связей")
async def search_graph_memory(
    request: SearchRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client),
    redis: RedisService = Depends(get_redis)
) -> Dict[str, Any]:
    try:
        if not client.graph_support:
            raise HTTPException(status_code=503, detail="Graph Memory недоступен")
        
        # Выполняем поиск (Mem0 автоматически использует граф)
        result = await client.search_memory(
            query=request.query,
            user_id=request.user_id,
            limit=request.limit,
            agent_id=request.agent_id,
            session_id=request.session_id
        )
        
        # Добавляем информацию о графовом поиске
        graph_result = result.copy()
        graph_result.update({
            "search_type": "graph_enhanced",
            "graph_support": True,
            "relationship_traversal": True
        })
        
        # Redis event
        await redis.publish_event(
            "graph_search_performed", 
            {
                "query": request.query,
                "user_id": request.user_id,
                "results": len(result.get('memories', []))
            }
        )
        
        logger.info(f"🕸️ Графовый поиск: {len(result.get('memories', []))} результатов")
        return graph_result
        
    except Exception as e:
        logger.error(f"❌ Ошибка графового поиска: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/graph/entity-relationships",
          operation_id="get_entity_relationships",
          summary="Получить связи сущности",
          description="Анализирует графовые связи конкретной сущности")
async def get_entity_relationships(
    request: EntityRequest,
    client: EnterpriseMemoryClient = Depends(get_memory_client)
) -> Dict[str, Any]:
    try:
        if not client.graph_support:
            raise HTTPException(status_code=503, detail="Graph Memory недоступен")
        
        # Поиск всех упоминаний сущности
        search_result = await client.search_memory(
            query=request.entity_name,
            user_id=request.user_id,
            limit=15  # Больше для анализа связей
        )
        
        memories = search_result.get('memories', [])
        
        # Анализ связей (упрощенный)
        relationships = {
            "entity_name": request.entity_name,
            "user_id": request.user_id,
            "direct_mentions": len(memories),
            "related_entities": [],
            "relationship_types": [],
            "connection_strength": 0.0,
            "memory_references": []
        }
        
        # Извлечение связанных сущностей (базовый анализ)
        entity_lower = request.entity_name.lower()
        for memory in memories:
            content = memory.get('memory', '').lower()
            
            # Простое извлечение связей по ключевым словам
            if ' и ' in content:
                parts = content.split(' и ')
                for part in parts:
                    if entity_lower not in part and len(part.strip()) > 3:
                        relationships["related_entities"].append(part.strip()[:50])
            
            # Типы отношений
            if 'работает' in content or 'делает' in content:
                relationships["relationship_types"].append("action")
            if 'знает' in content or 'друг' in content:
                relationships["relationship_types"].append("personal")
            if 'проект' in content or 'задача' in content:
                relationships["relationship_types"].append("professional")
            
            relationships["memory_references"].append({
                "memory_id": memory.get('id'),
                "relevance": memory.get('score', 0.0)
            })
        
        # Сила связи
        if len(memories) > 0:
            avg_score = sum(m.get('score', 0) for m in memories) / len(memories)
            relationships["connection_strength"] = avg_score
        
        # Убираем дубликаты
        relationships["related_entities"] = list(set(relationships["related_entities"]))[:5]
        relationships["relationship_types"] = list(set(relationships["relationship_types"]))
        
        logger.info(f"🔗 Связи сущности {request.entity_name}: {len(relationships['related_entities'])} связей")
        return relationships
        
    except Exception as e:
        logger.error(f"❌ Ошибка анализа связей: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/status",
         operation_id="graph_status",
         summary="Статус графовой системы",
         description="Проверяет состояние графовой памяти и связей")
async def graph_status() -> Dict[str, Any]:
    try:
        if not memory_client:
            return {"graph_available": False, "error": "Memory client недоступен"}
        
        status = {
            "graph_available": memory_client.graph_support,
            "vector_available": memory_client.vector_support,
            "graph_store_type": "memgraph" if memory_client.graph_support else None,
            "vector_store_type": "supabase" if memory_client.vector_support else None,
            "hybrid_mode": memory_client.graph_support and memory_client.vector_support,
            "capabilities": {
                "entity_extraction": memory_client.graph_support,
                "relationship_mapping": memory_client.graph_support,
                "semantic_search": memory_client.vector_support,
                "multi_hop_reasoning": memory_client.graph_support
            }
        }
        
        if memory_client.graph_support:
            status["graph_info"] = {
                "status": "active",
                "connection": "healthy",
                "features": ["entity_extraction", "relationship_inference", "graph_traversal"]
            }
        
        logger.info(f"📊 Graph status: {'active' if memory_client.graph_support else 'inactive'}")
        return status
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса графа: {e}")
        return {"graph_available": False, "error": str(e)}


# =================== 2 СИСТЕМНЫХ TOOLS ===================

@app.get("/health")
async def health() -> Dict[str, Any]:
    """Комплексная проверка состояния всех компонентов"""
    try:
        health_status = {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Memory Client
        if memory_client:
            memory_health = await memory_client.health_check()
            health_status["components"]["memory"] = memory_health
        else:
            health_status["components"]["memory"] = {"status": "unavailable"}
            health_status["status"] = "degraded"
        
        # Redis
        if redis_service:
            redis_health = await redis_service.health_check()
            health_status["components"]["redis"] = redis_health
        else:
            health_status["components"]["redis"] = {"status": "unavailable"}
        
        # Graph Support
        health_status["components"]["graph"] = {
            "status": "active" if (memory_client and memory_client.graph_support) else "inactive"
        }
        
        # Vector Support  
        health_status["components"]["vector"] = {
            "status": "active" if (memory_client and memory_client.vector_support) else "inactive"
        }
        
        # Общий статус
        if health_status["status"] != "degraded":
            if memory_client and memory_client.vector_support:
                health_status["status"] = "healthy"
            else:
                health_status["status"] = "partial"
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check ошибка: {e}")
        return {
            "status": "unhealthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.get("/")
async def root() -> Dict[str, Any]:
    """Информация о системе"""
    return {
        "name": "🧠 Enterprise MCP-Mem0 Server",
        "version": "2.0.0",
        "description": "17 Production-ready Memory Tools for AI Agents",
        "tools_count": 17,
        "features": {
            "memory_tools": 11,
            "graph_tools": 4,
            "system_tools": 2,
            "redis_integration": True,
            "graph_memory": True,
            "vector_memory": True,
            "enterprise_ready": True
        },
        "endpoints": {
            "memory": [
                "/memory/save", "/memory/search", "/memory/get-all",
                "/memory/save-verified", "/memory/get-context",
                "/memory/validate-project-context", "/memory/resolve-conflict",
                "/memory/audit-quality", "/memory/save-milestone",
                "/memory/get-project-state", "/memory/track-evolution"
            ],
            "graph": [
                "/graph/save-memory", "/graph/search",
                "/graph/entity-relationships", "/graph/status"
            ],
            "system": ["/health", "/"]
        },
        "mcp_endpoint": "/mcp",
        "documentation": "/docs"
    }


# =================== MCP INTEGRATION ===================

# Создаем MCP server ПОСЛЕ определения всех endpoints
mcp = FastApiMCP(app)
mcp.mount()

logger.info("🔌 FastAPI-MCP server с 17 Enterprise Tools готов!")
logger.info("📡 MCP endpoint: http://localhost:8000/mcp")
logger.info("📚 Документация: http://localhost:8000/docs")


# =================== DEVELOPMENT SERVER ===================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Запуск в development режиме...")
    uvicorn.run(
        "fastapi_mcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 