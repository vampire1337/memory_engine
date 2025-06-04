#!/usr/bin/env python3
"""
Test script for MCP STDIO transport with proper initialization sequence.
"""
import json
import subprocess
import sys

def test_mcp_stdio():
    """Test MCP server via STDIO transport with proper MCP protocol."""
    
    # Start the MCP server process
    process = subprocess.Popen(
        [sys.executable, "start_mcp.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("🔄 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        init_response = process.stdout.readline().strip()
        print(f"✅ Initialize response: {init_response}")
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("🔄 Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Step 3: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("🔄 Requesting tools list...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response = process.stdout.readline().strip()
        print(f"✅ Tools response: {tools_response}")
        
        # Parse and show tools
        if tools_response:
            try:
                tools_data = json.loads(tools_response)
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    print(f"\n🛠️  Found {len(tools)} tools:")
                    for i, tool in enumerate(tools, 1):
                        print(f"  {i}. {tool['name']} - {tool.get('description', 'No description')}")
                else:
                    print("❌ No tools found in response")
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing tools response: {e}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_stdio() 