#!/usr/bin/env python3
"""
Скрипт запуска FastAPI-MCP сервера памяти
Заменяет проблемную реализацию на стабильную архитектуру
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Запуск FastAPI-MCP сервера памяти"""
    
    print("🚀 Запуск FastAPI-MCP сервера памяти...")
    print("=" * 60)
    print("📌 Преимущества новой архитектуры:")
    print("  ✅ Стабильная FastAPI база")
    print("  ✅ Автоматическое создание MCP tools")
    print("  ✅ Исправленные ошибки NoneType")
    print("  ✅ Все 11 инструментов памяти")
    print("  ✅ REST API + MCP протокол")
    print("=" * 60)
    
    # Убеждаемся что мы в правильной директории
    src_dir = Path(__file__).parent / "src"
    if not src_dir.exists():
        print("❌ Ошибка: папка src не найдена")
        return 1
    
    fastapi_server = src_dir / "fastapi_memory_server.py"
    if not fastapi_server.exists():
        print(f"❌ Ошибка: файл {fastapi_server} не найден")
        return 1
    
    print(f"📁 Запуск из: {fastapi_server}")
    print(f"🌐 FastAPI будет доступно на: http://localhost:8000")
    print(f"🔧 MCP сервер будет доступен на: http://localhost:8000/mcp")
    print(f"📖 Swagger UI: http://localhost:8000/docs")
    print()
    
    try:
        # Запускаем FastAPI сервер
        cmd = [sys.executable, str(fastapi_server)]
        print(f"💻 Выполняем: {' '.join(cmd)}")
        print("🔄 Нажмите Ctrl+C для остановки сервера")
        print()
        
        subprocess.run(cmd, cwd=src_dir.parent)
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 