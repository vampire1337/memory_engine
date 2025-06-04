#!/usr/bin/env python3
import requests
import json
import time
import uuid

def test_mcp_direct():
    """Прямое HTTP тестирование MCP сервера"""
    
    # Получаем session_id
    print("🔌 Получение session_id...")
    response = requests.get("http://localhost:8050/sse", stream=True, timeout=3)
    session_id = None
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            print(f"SSE: {decoded}")
            if 'session_id=' in decoded:
                import re
                match = re.search(r'session_id=([a-f0-9]+)', decoded)
                if match:
                    raw_id = match.group(1)
                    session_id = f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
                    print(f"✅ Session ID: {session_id}")
                    break
            if 'data:' in decoded:
                break
    
    if not session_id:
        print("❌ Не удалось получить session_id")
        return
    
    # Тестируем инструменты
    tools_to_test = [
        ("save_memory", {"text": "HTTP тест после отката коммита 11/11"}),
        ("get_all_memories", {}),
        ("search_memories", {"query": "HTTP тест", "limit": 3}),
        ("save_verified_memory", {
            "content": "Верифицированный HTTP тест", 
            "project_id": "http-test", 
            "category": "testing", 
            "confidence_level": 9
        }),
        ("get_accurate_context", {"query": "HTTP тест", "project_id": "http-test"}),
        ("validate_project_context", {"project_id": "http-test"}),
        ("audit_memory_quality", {"project_id": "http-test"}),
        ("save_project_milestone", {
            "project_id": "http-test",
            "milestone_type": "testing",
            "content": "HTTP тестирование выполнено"
        }),
        ("get_current_project_state", {"project_id": "http-test"}),
        ("track_project_evolution", {"project_id": "http-test"}),
        ("resolve_context_conflict", {
            "conflicting_memory_ids": "test1,test2",
            "correct_content": "HTTP тест конфликтов",
            "resolution_reason": "HTTP тестирование"
        })
    ]
    
    success = 0
    total = len(tools_to_test)
    
    for i, (tool_name, params) in enumerate(tools_to_test, 1):
        print(f"\n{i:2d}/11 🛠️ {tool_name}")
        
        message = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        try:
            url = f"http://localhost:8050/messages/?session_id={session_id}"
            response = requests.post(url, json=message, timeout=15)
            
            if response.status_code == 202:
                print(f"      ✅ УСПЕХ - HTTP 202")
                success += 1
            else:
                print(f"      ❌ НЕУДАЧА - HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"      ❌ ОШИБКА - {e}")
        
        time.sleep(0.5)
    
    print(f"\n🎯 ИТОГ HTTP ТЕСТИРОВАНИЯ: {success}/{total} ({success/total*100:.1f}%)")
    
    if success == total:
        print("🚀 ВСЕ HTTP ТЕСТЫ ПРОШЛИ!")
    else:
        print("⚠️ Есть проблемы с HTTP тестами")

if __name__ == "__main__":
    test_mcp_direct() 