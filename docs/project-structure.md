# 📁 Project Structure

## Overview

Unified Memory System follows a modular, enterprise-grade architecture designed for scalability, maintainability, and extensibility. The project is structured to support both development and production deployments with clear separation of concerns.

```
mcp-mem0/
├── 📁 src/                     # Core application logic
│   ├── 🗠 main.py              # FastMCP server with 10 MCP tools
│   ├── 🗠 unified_memory_server.py # REST API with 15 endpoints
│   ├── 🗠 fastapi_memory_server.py # Legacy FastAPI server
│   ├── 🗠 graph_memory_upgrade.py # Graph memory enhancements
│   └── 🗠 utils.py             # Shared utilities and helpers
├── 📁 mcp_tools/               # MCP Protocol Tools (10 tools)
│   └── → Defined in main.py    # FastMCP tool definitions
├── 📁 scripts/                # CLI and automation scripts
│   └── 🗠 test_all.sh         # Comprehensive API testing script
├── 📁 examples/               # Working examples and demos
│   ├── 🗠 memory_save.json    # Basic memory save example
│   ├── 🗠 graph_search.json   # Graph search parameters
│   └── 🗠 verified_memory.json # High-confidence memory example
├── 📁 tests/                  # Test suites
│   └── 🗠 test_api.py         # Python pytest suite for APIs
├── 📁 docs/                   # Documentation
│   ├── 🗠 project-structure.md # This file
│   ├── 🗠 tools-reference.md   # Complete tools inventory
│   ├── 🗠 mcp-testing-report.md # Testing results and screenshots
│   ├── 🗠 GRAPH_MEMORY_GUIDE.md # Graph memory usage guide
│   └── 🗠 QUICKSTART.md       # Quick start guide
├── 📁 assets/                 # Visual assets and demos
│   └── 📁 screenshots/        # Generated demo screenshots
│       ├── 🖼️ neo4j_graph.png  # Neo4j graph visualization
│       └── 🖼️ api_success.png  # API call demonstration
├── 📁 .github/               # GitHub automation
│   └── 📁 ISSUE_TEMPLATE/     # Issue templates
│       └── 🗠 bug_report.md   # Bug report template
├── 🐳 docker-compose.unified.yml # Production deployment
├── 🐳 Dockerfile.unified      # Production container
├── 📋 requirements.txt        # Python dependencies
├── ⚙️ pyproject.toml          # Python project configuration
├── 📄 README.md              # Main project documentation
├── 📄 LICENSE                # MIT License
├── 📄 CONTRIBUTING.md        # Contribution guidelines
└── 🎯 cursor.json            # Agent automation rules
```

## 🏗️ Architecture Components

### 📁 Core Application (`src/`)

#### `main.py` - FastMCP Server
- **Purpose**: Model Context Protocol (MCP) server implementation
- **Tools**: 10 MCP tools for AI agent integration
- **Protocol**: Implements [MCP Protocol](https://modelcontextprotocol.org/)
- **Usage**: Connects to Cursor IDE, Claude Desktop, and other MCP clients

#### `unified_memory_server.py` - REST API Server
- **Purpose**: Enterprise-grade REST API for memory operations
- **Endpoints**: 15 comprehensive endpoints (11 basic + 4 graph)
- **Architecture**: FastAPI with async/await support
- **Features**: Health monitoring, graph support, fallback storage

#### `utils.py` - Shared Utilities
- **Purpose**: Common functions and helpers
- **Features**: Mem0 client management, metadata enhancement, validation
- **Components**: Memory utilities, confidence estimation, project detection

### 🔧 Tools & Integration (`mcp_tools/`)

MCP tools are defined as FastMCP decorators in `main.py`:

1. **Basic Memory**: `save_memory`, `get_all_memories`, `search_memories`
2. **Enhanced Memory**: `save_verified_memory`, `get_accurate_context`
3. **Project Management**: `validate_project_context`, `save_project_milestone`
4. **Quality Control**: `audit_memory_quality`, `resolve_context_conflict`
5. **State Tracking**: `get_current_project_state`, `track_project_evolution`

### 🧪 Testing Framework (`tests/`, `scripts/`)

#### Python Tests (`tests/test_api.py`)
- **Framework**: pytest
- **Coverage**: All 15 API endpoints
- **Features**: Health checks, memory operations, graph operations
- **Usage**: `python -m pytest tests/`

#### Bash Integration Tests (`scripts/test_all.sh`)
- **Purpose**: End-to-end API testing
- **Features**: 10 comprehensive tests with colored output
- **Coverage**: Health, memory, graph, and verification endpoints
- **Usage**: `./scripts/test_all.sh`

### 📚 Examples & Demos (`examples/`)

- **`memory_save.json`**: Technical memory example with Docker optimization tips
- **`graph_search.json`**: Semantic search with graph relationship parameters
- **`verified_memory.json`**: High-confidence memory with benchmarks

### 📄 Documentation (`docs/`)

- **Architecture**: Complete system architecture and design decisions
- **API Reference**: All endpoints with parameters and examples
- **Testing**: Comprehensive testing reports with screenshots
- **Guides**: Quick start, graph memory, and integration guides

## 🚀 Deployment Patterns

### Development Mode
```bash
# Local development
python src/main.py              # MCP server on port 2000
python src/unified_memory_server.py # REST API on port 8051
```

### Production Mode
```bash
# Docker deployment
docker-compose -f docker-compose.unified.yml up -d
```

### Components Stack
- **Application**: FastAPI + FastMCP
- **Memory**: Mem0 SDK with OpenAI embeddings  
- **Graph Database**: Neo4j for relationships
- **Storage**: PostgreSQL + fallback storage
- **Protocol**: MCP for AI agent integration

## 🔄 Integration Points

### MCP Clients
- **Cursor IDE**: Via `~/.config/cursor/mcp-settings.json`
- **Claude Desktop**: Via Claude configuration
- **Custom Agents**: Direct MCP protocol connection

### REST API Clients
- **Web Applications**: Direct HTTP/HTTPS calls
- **Other Services**: API integration via OpenAPI/Swagger
- **CLI Tools**: Via curl or HTTP clients

## 🎯 File Naming Conventions

- **Python Files**: `snake_case.py`
- **Documentation**: `UPPERCASE.md` for main docs, `lowercase.md` for technical docs
- **Examples**: `descriptive_name.json`
- **Scripts**: `action_description.sh`
- **Assets**: `component_purpose.png`

## 🔐 Security & Configuration

- **Environment Variables**: Stored in `.env` (not committed)
- **Secrets**: Managed via Docker secrets or environment
- **API Keys**: OpenAI, Neo4j, Supabase (all configurable)
- **Fallback**: Graceful degradation when services unavailable

## 📈 Scaling Considerations

- **Horizontal**: Multiple server instances with load balancer
- **Vertical**: Memory and CPU scaling per container
- **Storage**: Neo4j clustering, PostgreSQL replication
- **Caching**: Memory caching for frequent operations

---

This structure supports enterprise deployment patterns while maintaining development simplicity and extensibility for the open-source community. 