#!/usr/bin/env python3
"""
Direct test of Enhanced Memory System functions.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set env
os.environ["TRANSPORT"] = "stdio"

async def test_functions():
    """Test Enhanced Memory System functions directly."""
    print("🔧 Testing Enhanced Memory System Functions Directly...")
    
    # Import functions
    from main import (
        save_memory, save_verified_memory, search_memories, 
        get_all_memories, get_accurate_context
    )
    
    # Test basic memory save
    print("\n1️⃣ Testing save_memory...")
    try:
        result = await save_memory("Test memory for direct function call")
        print(f"✅ save_memory: {result}")
    except Exception as e:
        print(f"❌ save_memory error: {e}")
    
    # Test enhanced save  
    print("\n2️⃣ Testing save_verified_memory...")
    try:
        result = await save_verified_memory(
            content="Enhanced test memory with metadata",
            project_id="direct-test",
            category="testing",
            confidence_level=9
        )
        print(f"✅ save_verified_memory: {result}")
    except Exception as e:
        print(f"❌ save_verified_memory error: {e}")
    
    # Test memory search
    print("\n3️⃣ Testing search_memories...")
    try:
        result = await search_memories("test memory", limit=2)
        print(f"✅ search_memories: {result}")
    except Exception as e:
        print(f"❌ search_memories error: {e}")
    
    # Test get all memories
    print("\n4️⃣ Testing get_all_memories...")
    try:
        result = await get_all_memories()
        print(f"✅ get_all_memories: {result}")
    except Exception as e:
        print(f"❌ get_all_memories error: {e}")
    
    # Test accurate context
    print("\n5️⃣ Testing get_accurate_context...")
    try:
        result = await get_accurate_context("test memory", min_confidence=5)
        print(f"✅ get_accurate_context: {result}")
    except Exception as e:
        print(f"❌ get_accurate_context error: {e}")
    
    print("\n🎉 Direct function testing completed!")

if __name__ == "__main__":
    asyncio.run(test_functions()) 