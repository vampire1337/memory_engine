#!/usr/bin/env python3
"""
🔥 ХИТРЫЙ TEMPORAL DEBUGGING WRAPPER
Перехватывает все вызовы start_workflow и логирует аргументы
"""

import asyncio
import inspect
from typing import Any
from temporalio.client import Client

class TemporalDebugWrapper:
    def __init__(self, original_client: Client):
        self.original_client = original_client
        
    async def start_workflow(self, *args, **kwargs):
        """Wrapper для debugging start_workflow вызовов"""
        print("🔥 TEMPORAL DEBUG WRAPPER ПЕРЕХВАТИЛ ВЫЗОВ!")
        print(f"📊 Количество позиционных аргументов: {len(args)}")
        print(f"📊 Количество keyword аргументов: {len(kwargs)}")
        
        print("\n🔍 ПОЗИЦИОННЫЕ АРГУМЕНТЫ:")
        for i, arg in enumerate(args):
            print(f"  [{i}] {type(arg).__name__}: {repr(arg)}")
            
        print("\n🔍 KEYWORD АРГУМЕНТЫ:")
        for key, value in kwargs.items():
            print(f"  {key}: {type(value).__name__} = {repr(value)}")
            
        print("\n🎯 СТЕК ВЫЗОВА:")
        frame = inspect.currentframe()
        try:
            while frame:
                filename = frame.f_code.co_filename
                line_no = frame.f_lineno
                func_name = frame.f_code.co_name
                if 'temporal_memory_service' in filename:
                    print(f"  📍 {filename}:{line_no} в функции {func_name}")
                frame = frame.f_back
        finally:
            del frame
            
        print("\n🚀 ПОПЫТКА ВЫЗОВА ОРИГИНАЛЬНОГО start_workflow...")
        try:
            result = await self.original_client.start_workflow(*args, **kwargs)
            print("✅ УСПЕХ!")
            return result
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            print(f"📋 Тип ошибки: {type(e).__name__}")
            raise
            
    def __getattr__(self, name):
        """Перенаправляем все остальные методы к оригинальному клиенту"""
        return getattr(self.original_client, name)

# Функция для monkey patching
def patch_temporal_client():
    """Заменяет Client.start_workflow на debug версию"""
    original_connect = Client.connect
    
    async def debug_connect(*args, **kwargs):
        client = await original_connect(*args, **kwargs)
        return TemporalDebugWrapper(client)
        
    Client.connect = debug_connect
    print("🔧 TEMPORAL CLIENT УСПЕШНО ЗАПАТЧЕН!")

if __name__ == "__main__":
    print("🔥 TEMPORAL DEBUG WRAPPER ГОТОВ К РАБОТЕ!")
    print("Импортируйте этот модуль в начале temporal_memory_service.py")
    print("И вызовите patch_temporal_client() перед созданием клиента") 