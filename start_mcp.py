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

# Import and run the main server
from main import main

if __name__ == "__main__":
    asyncio.run(main()) 