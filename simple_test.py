#!/usr/bin/env python3
"""
Simple test of Enhanced Memory System MCP tools.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set STDIO transport
os.environ["TRANSPORT"] = "stdio"

async def test_tools():
    """Test basic MCP functionality."""
    from main import mcp
    
    print("🔧 Testing Enhanced Memory System MCP Tools...")
    
    # Test basic memory save
    print("\n1️⃣ Testing save_memory...")
    try:
        result = await mcp._call_tool("save_memory", {"text": "Test memory for MCP system"})
        print(f"✅ save_memory: {result}")
    except Exception as e:
        print(f"❌ save_memory error: {e}")
    
    # Test enhanced save  
    print("\n2️⃣ Testing save_verified_memory...")
    try:
        result = await mcp._call_tool("save_verified_memory", {
            "content": "Enhanced test memory with metadata",
            "project_id": "mcp-test",
            "category": "testing",
            "confidence_level": 9
        })
        print(f"✅ save_verified_memory: {result}")
    except Exception as e:
        print(f"❌ save_verified_memory error: {e}")
    
    # Test memory search
    print("\n3️⃣ Testing search_memories...")
    try:
        result = await mcp._call_tool("search_memories", {"query": "test memory", "limit": 2})
        print(f"✅ search_memories: {result}")
    except Exception as e:
        print(f"❌ search_memories error: {e}")
    
    # Test get all memories
    print("\n4️⃣ Testing get_all_memories...")
    try:
        result = await mcp._call_tool("get_all_memories", {})
        print(f"✅ get_all_memories: {result}")
    except Exception as e:
        print(f"❌ get_all_memories error: {e}")
    
    print("\n🎉 Tool testing completed!")

if __name__ == "__main__":
    asyncio.run(test_tools()) 