#!/usr/bin/env python3
"""
Start script for MCP Mem0 server with STDIO transport.
This script is designed to be called by MCP clients like Cursor.
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment for STDIO transport
os.environ["TRANSPORT"] = "stdio"

# Set OpenAI API key if not already set
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "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"

# Set LLM configuration 
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_API_KEY"] = "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"
os.environ["LLM_CHOICE"] = "gpt-4o-mini"
os.environ["EMBEDDING_MODEL_CHOICE"] = "text-embedding-3-small"

# Import and run the main server
from main import main

if __name__ == "__main__":
    asyncio.run(main()) 