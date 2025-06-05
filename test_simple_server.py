"""
Простой тестовый FastAPI сервер для диагностики
"""
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI(title="Test Server")

@app.get("/")
async def health_check():
    return {"status": "OK", "message": "Test server works"}

@app.get("/test")
async def test_endpoint():
    return {"test": "success"}

# Настройка FastAPI-MCP
mcp = FastApiMCP(app)
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    print("🔧 Starting test server on port 8051...")
    uvicorn.run(app, host="0.0.0.0", port=8051) 