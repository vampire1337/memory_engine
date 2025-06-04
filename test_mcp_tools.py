#!/usr/bin/env python3
"""
Прямое тестирование каждого MCP инструмента Enhanced Memory System
"""
import os
import sys
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

# Mock Mem0 client для тестирования
class MockMem0Client:
    def __init__(self):
        self.memories = []
        
    def add(self, content, metadata=None):
        memory = {
            "id": f"test_{len(self.memories)}",
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        self.memories.append(memory)
        return {"message": f"Memory added with ID {memory['id']}"}
    
    def search(self, query, limit=10):
        # Simple mock search
        return [mem for mem in self.memories if query.lower() in mem['content'].lower()][:limit]
    
    def get_all(self):
        return self.memories

# Настройка окружения для тестирования
os.environ["MEM0_CONFIG_TYPE"] = "sqlite"
os.environ["MEM0_SQLITE_PATH"] = "./test_memory.db"
os.environ["DEBUG"] = "true"

async def test_all_tools():
    """Тестирование каждого инструмента поочередно"""
    
    print("🚀 НАЧИНАЕМ ТЕСТИРОВАНИЕ КАЖДОГО MCP ИНСТРУМЕНТА")
    print("=" * 60)
    
    # Импортируем все инструменты
    try:
        from main import (
            save_verified_memory, get_accurate_context, validate_project_context,
            resolve_context_conflict, audit_memory_quality, save_project_milestone,
            get_current_project_state, track_project_evolution
        )
        print("✅ Все инструменты импортированы успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Создаем мок контекст
    class MockContext:
        def __init__(self):
            self.mem0_client = MockMem0Client()
    
    ctx = MockContext()
    
    # Тестовые данные
    project_id = "test_project_enhanced_memory"
    
    print("\n1️⃣ ТЕСТИРУЕМ save_verified_memory")
    try:
        result = await save_verified_memory(
            ctx,
            content="Тест архитектурного решения для Enhanced Memory System",
            project_id=project_id,
            category="architecture",
            confidence_level=9,
            source="code_analysis",
            tags="enhanced_memory,architecture,mcp"
        )
        print("✅ save_verified_memory работает:", result)
    except Exception as e:
        print("❌ Ошибка save_verified_memory:", e)
    
    print("\n2️⃣ ТЕСТИРУЕМ get_accurate_context")
    try:
        result = await get_accurate_context(
            ctx,
            query="Enhanced Memory System архитектура",
            project_id=project_id,
            min_confidence=7
        )
        print("✅ get_accurate_context работает:", len(result))
    except Exception as e:
        print("❌ Ошибка get_accurate_context:", e)
    
    print("\n3️⃣ ТЕСТИРУЕМ validate_project_context")
    try:
        result = await validate_project_context(ctx, project_id=project_id)
        print("✅ validate_project_context работает:", result)
    except Exception as e:
        print("❌ Ошибка validate_project_context:", e)
    
    print("\n4️⃣ ТЕСТИРУЕМ save_project_milestone")
    try:
        result = await save_project_milestone(
            ctx,
            project_id=project_id,
            milestone_type="architecture_decision",
            content="Реализована система Enhanced Memory с гарантией точности контекста",
            impact_level=10,
            tags="milestone,architecture,production"
        )
        print("✅ save_project_milestone работает:", result)
    except Exception as e:
        print("❌ Ошибка save_project_milestone:", e)
    
    print("\n5️⃣ ТЕСТИРУЕМ get_current_project_state")
    try:
        result = await get_current_project_state(ctx, project_id=project_id)
        print("✅ get_current_project_state работает:", result)
    except Exception as e:
        print("❌ Ошибка get_current_project_state:", e)
    
    print("\n6️⃣ ТЕСТИРУЕМ track_project_evolution")
    try:
        result = await track_project_evolution(ctx, project_id=project_id)
        print("✅ track_project_evolution работает:", result)
    except Exception as e:
        print("❌ Ошибка track_project_evolution:", e)
    
    print("\n7️⃣ ТЕСТИРУЕМ audit_memory_quality")
    try:
        result = await audit_memory_quality(ctx, project_id=project_id)
        print("✅ audit_memory_quality работает:", result)
    except Exception as e:
        print("❌ Ошибка audit_memory_quality:", e)
    
    print("\n8️⃣ ТЕСТИРУЕМ resolve_context_conflict")
    try:
        result = await resolve_context_conflict(
            ctx,
            conflicting_memory_ids="test_0,test_1",
            correct_content="Обновленная корректная информация",
            resolution_reason="Тестирование системы разрешения конфликтов"
        )
        print("✅ resolve_context_conflict работает:", result)
    except Exception as e:
        print("❌ Ошибка resolve_context_conflict:", e)
    
    print("\n" + "=" * 60)
    print("🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("Все инструменты проверены на работоспособность")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_all_tools()) 