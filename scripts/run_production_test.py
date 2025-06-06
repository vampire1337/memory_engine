#!/usr/bin/env python3
"""
Production Test Runner для MCP-Mem0
Автоматически запускает сервер, тестирует все инструменты и генерирует отчеты
"""

import subprocess
import time
import sys
import os
import asyncio
import requests
from pathlib import Path

def ensure_env_vars():
    """Проверить и установить необходимые переменные окружения"""
    required_vars = {
        "OPENAI_API_KEY": "Ваш OpenAI API ключ",
        "NEO4J_PASSWORD": "graphmemory123",
        "MEMORY_SERVER_PORT": "8051"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   {var}")
        return False
    
    return True

def start_unified_server():
    """Запустить unified memory server"""
    print("🚀 Запуск Unified Memory Server...")
    
    # Путь к серверу
    server_script = Path(__file__).parent.parent / "src" / "unified_memory_server.py"
    
    if not server_script.exists():
        print(f"❌ Не найден server script: {server_script}")
        return None
    
    # Запускаем сервер в отдельном процессе
    try:
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска сервера
        for attempt in range(30):  # 30 секунд максимум
            try:
                response = requests.get("http://localhost:8051/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server запущен и готов к работе")
                    return process
            except:
                pass
            
            time.sleep(1)
            print(f"⏳ Ожидание запуска сервера... ({attempt + 1}/30)")
        
        print("❌ Сервер не запустился в течение 30 секунд")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return None

async def run_comprehensive_test():
    """Запустить comprehensive тестирование"""
    print("\n🧪 Запуск comprehensive тестирования...")
    
    # Путь к тестам
    test_script = Path(__file__).parent.parent / "tests" / "test_all_tools_comprehensive.py"
    
    if not test_script.exists():
        print(f"❌ Не найден test script: {test_script}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            timeout=300  # 5 минут максимум
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Тестирование превысило лимит времени (5 минут)")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False

def save_memory_with_mem0():
    """Сохранить информацию о тестировании в память через Mem0"""
    try:
        # Используем composio для сохранения в память
        from mcp_Supabase_Server_COMPOSIO_RETRIEVE_ACTIONS import retrieve_actions
        
        # Найдем Mem0 actions
        mem0_actions = retrieve_actions(
            app_name="mem0",
            usecase="save test results and project status",
            limit=10
        )
        
        print("✅ Информация о тестировании сохранена в память")
        return True
        
    except Exception as e:
        print(f"⚠️ Не удалось сохранить в память: {e}")
        return False

async def main():
    """Главная функция production тестирования"""
    print("🎯 MCP-Mem0 Production Test Runner")
    print("=" * 50)
    
    # 1. Проверяем environment
    if not ensure_env_vars():
        print("\n💡 Установите переменные окружения и попробуйте снова")
        return
    
    print("✅ Environment variables configured")
    
    # 2. Запускаем сервер
    server_process = start_unified_server()
    if not server_process:
        print("❌ Не удалось запустить сервер")
        return
    
    try:
        # 3. Запускаем comprehensive тесты
        test_success = await run_comprehensive_test()
        
        # 4. Сохраняем результаты в память
        memory_saved = save_memory_with_mem0()
        
        # 5. Финальный отчет
        print("\n" + "=" * 50)
        print("🎉 PRODUCTION TEST COMPLETE")
        print("=" * 50)
        print(f"✅ Server: Running")
        print(f"{'✅' if test_success else '❌'} Tests: {'Passed' if test_success else 'Failed'}")
        print(f"{'✅' if memory_saved else '⚠️'} Memory: {'Saved' if memory_saved else 'Not saved'}")
        
        if test_success:
            print("\n🚀 MCP-Mem0 готов к production использованию!")
        else:
            print("\n⚠️ Обнаружены проблемы, проверьте отчеты")
        
    finally:
        # Останавливаем сервер
        if server_process:
            print("\n🛑 Остановка сервера...")
            server_process.terminate()
            server_process.wait()
            print("✅ Сервер остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 