#!/usr/bin/env python3
"""
Тест исправленных enhanced инструментов
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import (
    get_mem0_client,
    simulate_enhanced_search,
    estimate_content_confidence,
    extract_project_from_content,
    categorize_content,
    get_memory_metadata,
    safe_get_memories
)

async def test_enhanced_tools():
    """Тест enhanced инструментов"""
    print("🧪 ТЕСТИРОВАНИЕ ENHANCED TOOLS")
    print("=" * 50)
    
    # Загружаем переменные окружения
    load_dotenv()
    
    try:
        # Инициализируем клиент
        print("1️⃣ Инициализация Mem0 клиента...")
        mem0_client = get_mem0_client()
        print("✅ Клиент инициализирован")
        
        # Создаем тестовые данные
        print("\n2️⃣ Создание тестовых данных...")
        test_memories = [
            "Проект mcp-mem0: Архитектура основана на FastMCP сервере с enhanced инструментами",
            "Проект mcp-mem0: Проблема с NoneType ошибками в enhanced инструментах исправлена",
            "Проект mcp-mem0: Решение - адаптация к базовому API Mem0 через content analysis",
            "Проект mcp-mem0: Статус - багфикс завершен, все инструменты работают",
            "Проект другой: Это память из другого проекта для тестирования фильтрации",
            "Аутентификация работает идеально и протестирована в production",
            "Возможно есть проблема с производительностью базы данных"
        ]
        
        for memory in test_memories:
            result = mem0_client.add(memory, user_id="default")
            print(f"   ✅ Добавлено: {memory[:50]}...")
        
        # Тест 3: Получение всех воспоминаний
        print("\n3️⃣ Тест получения воспоминаний...")
        all_memories = mem0_client.get_all(user_id="default")
        memory_list = safe_get_memories(all_memories)
        print(f"✅ Найдено {len(memory_list)} воспоминаний")
        
        # Тест 4: Обработка метаданных
        print("\n4️⃣ Тест обработки метаданных...")
        if memory_list:
            for i, memory in enumerate(memory_list[:3]):
                metadata = get_memory_metadata(memory)
                print(f"   Память {i+1}:")
                print(f"     Контент: {metadata['content'][:50]}...")
                print(f"     Confidence: {metadata['confidence_level']}")
                print(f"     Категория: {metadata['category']}")
                print(f"     Проект: {extract_project_from_content(metadata['content'])}")
        
        # Тест 5: Оценка уверенности
        print("\n5️⃣ Тест оценки уверенности...")
        test_contents = [
            "Проблема с аутентификацией не решена",
            "Аутентификация работает идеально и протестирована",
            "Возможно, есть баг в системе",
            "Завершена разработка улучшенной системы памяти MCP с гарантиями точности"
        ]
        
        for content in test_contents:
            confidence = estimate_content_confidence(content)
            category = categorize_content(content)
            print(f"   '{content[:40]}...' -> Confidence: {confidence}, Category: {category}")
        
        # Тест 6: Симуляция enhanced поиска
        print("\n6️⃣ Тест enhanced поиска...")
        search_results = simulate_enhanced_search(
            mem0_client, 
            query="mcp-mem0 проект", 
            project_id="mcp-mem0", 
            min_confidence=5, 
            limit=3
        )
        
        print(f"✅ Найдено {len(search_results)} релевантных результатов")
        for i, result in enumerate(search_results):
            print(f"   Результат {i+1}:")
            print(f"     Контент: {result['content'][:50]}...")
            print(f"     Confidence: {result['confidence_level']}")
            print(f"     Категория: {result['category']}")
        
        # Тест 7: Поиск с фильтрацией по confidence
        print("\n7️⃣ Тест поиска с высоким confidence...")
        high_confidence_results = simulate_enhanced_search(
            mem0_client, 
            query="аутентификация", 
            min_confidence=7, 
            limit=5
        )
        
        print(f"✅ Найдено {len(high_confidence_results)} результатов с высоким confidence")
        for i, result in enumerate(high_confidence_results):
            print(f"   Результат {i+1}:")
            print(f"     Контент: {result['content'][:50]}...")
            print(f"     Confidence: {result['confidence_level']}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"📊 Итого протестировано: {len(memory_list)} воспоминаний")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_tools())
    sys.exit(0 if success else 1) 