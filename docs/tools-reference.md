# 🛠️ Tools Reference

## Overview

Unified Memory System provides 25 total tools and endpoints:
- **10 MCP Tools** (Model Context Protocol) for AI agent integration
- **15 REST API Endpoints** for direct HTTP access

All tools implement the same core functionality with different interfaces for maximum compatibility.

---

## 🔧 MCP Tools (FastMCP Server)

### Server Details
- **Host**: `localhost:2000` (development)
- **Protocol**: [Model Context Protocol](https://modelcontextprotocol.org/)
- **Usage**: AI agents (Cursor IDE, Claude Desktop, custom agents)

### Tool 1: `save_memory`
**Purpose**: Save information to long-term memory with semantic indexing

**Parameters**:
- `text` (string): Content to store in memory

**Returns**: Success confirmation with preview

**Example**:
```json
{
  "text": "Docker multi-stage builds reduce image size by 70% using COPY --from=builder pattern"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 2: `get_all_memories`
**Purpose**: Retrieve all stored memories for the user

**Parameters**: None

**Returns**: JSON array of all memories with timestamps

**Example**:
```json
{}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 3: `search_memories`
**Purpose**: Semantic search through stored memories

**Parameters**:
- `query` (string): Search query in natural language
- `limit` (int, default=3): Maximum results to return

**Returns**: Ranked search results with relevance scores

**Example**:
```json
{
  "query": "Docker optimization techniques",
  "limit": 5
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 4: `save_verified_memory`
**Purpose**: Save verified information with enhanced metadata and conflict detection

**Parameters**:
- `content` (string): Information to store
- `project_id` (string): Project identifier
- `category` (string): Content category
- `confidence_level` (int): Confidence level (1-10)
- `source` (string, default="user_input"): Information source
- `expires_in_days` (int, optional): Expiration in days
- `tags` (string, optional): Comma-separated tags

**Returns**: Memory ID with metadata

**Example**:
```json
{
  "content": "Neo4j provides 26% better performance for relationship queries",
  "project_id": "unified_memory",
  "category": "performance",
  "confidence_level": 9,
  "source": "benchmark_testing",
  "tags": "neo4j,performance,benchmark"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 5: `get_accurate_context`
**Purpose**: Retrieve high-confidence memories for project context

**Parameters**:
- `query` (string): Context query
- `project_id` (string, optional): Project filter
- `min_confidence` (int, default=5): Minimum confidence level
- `limit` (int, default=5): Maximum results

**Returns**: High-confidence memories with accuracy scores

**Example**:
```json
{
  "query": "performance optimizations",
  "project_id": "unified_memory",
  "min_confidence": 7,
  "limit": 10
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 6: `validate_project_context`
**Purpose**: Validate project context for accuracy and consistency

**Parameters**:
- `project_id` (string): Project to validate

**Returns**: Validation report with confidence metrics

**Example**:
```json
{
  "project_id": "unified_memory"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 7: `resolve_context_conflict`
**Purpose**: Resolve conflicts between conflicting memories

**Parameters**:
- `conflicting_memory_ids` (string): Comma-separated memory IDs
- `correct_content` (string): Correct information
- `resolution_reason` (string): Reason for resolution

**Returns**: Resolution report with updated memories

**Example**:
```json
{
  "conflicting_memory_ids": "mem_123,mem_456",
  "correct_content": "Updated Docker optimization technique",
  "resolution_reason": "Newer benchmark results available"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 8: `audit_memory_quality`
**Purpose**: Audit memory quality and identify issues

**Parameters**:
- `project_id` (string, optional): Project to audit

**Returns**: Quality audit report with recommendations

**Example**:
```json
{
  "project_id": "unified_memory"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 9: `save_project_milestone`
**Purpose**: Save project milestone with enhanced tracking

**Parameters**:
- `project_id` (string): Project identifier
- `milestone_type` (string): Type of milestone
- `content` (string): Milestone description
- `impact_level` (int, default=8): Impact level (1-10)
- `tags` (string, optional): Comma-separated tags

**Returns**: Milestone ID with tracking info

**Example**:
```json
{
  "project_id": "unified_memory",
  "milestone_type": "release",
  "content": "v1.0.0 production release with all 25 tools",
  "impact_level": 10,
  "tags": "release,production,milestone"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

### Tool 10: `get_current_project_state`
**Purpose**: Get current state and progress of a project

**Parameters**:
- `project_id` (string): Project to analyze

**Returns**: Project state with recent activities and milestones

**Example**:
```json
{
  "project_id": "unified_memory"
}
```

**Test Status**: ✅ Verified in MCP Inspector

---

## 🌐 REST API Endpoints (FastAPI Server)

### Server Details
- **Host**: `localhost:8051` (development)
- **Protocol**: HTTP/HTTPS REST API
- **Docs**: `/docs` (Swagger UI), `/redoc` (ReDoc)
- **Usage**: Web applications, scripts, direct HTTP calls

---

### Endpoint 1: `POST /memory/save`
**Purpose**: Save memory with metadata

**Body**: `MemoryRequest`
- `content` (string): Content to save
- `user_id` (string, default="user"): User identifier
- `agent_id` (string, optional): Agent identifier  
- `session_id` (string, optional): Session identifier
- `metadata` (object, optional): Additional metadata

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/memory/save" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Docker multi-stage builds reduce image size by 70%",
    "user_id": "demo_user",
    "metadata": {
      "category": "technical",
      "priority": "high",
      "tags": ["docker", "optimization"]
    }
  }'
```

**Response**: `{"memory_id": "mem_123", "status": "success"}`

**Test Screenshot**: `assets/screenshots/save_memory_success.png`

---

### Endpoint 2: `POST /memory/search`
**Purpose**: Search memories semantically

**Body**: `SearchRequest`
- `query` (string): Search query
- `user_id` (string, default="user"): User identifier
- `limit` (int, default=5): Maximum results

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Docker optimization techniques",
    "user_id": "demo_user",
    "limit": 10
  }'
```

**Response**: `{"memories": [...], "total": 10}`

**Test Screenshot**: `assets/screenshots/search_memory_success.png`

---

### Endpoint 3: `POST /memory/get-all`
**Purpose**: Get all memories for user

**Body**: `GetMemoriesRequest`
- `user_id` (string, default="user"): User identifier

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/memory/get-all" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user"}'
```

**Response**: `[{"memory": "...", "id": "mem_123"}, ...]`

**Test Screenshot**: `assets/screenshots/get_all_memories_success.png`

---

### Endpoint 4: `POST /memory/save-verified`
**Purpose**: Save verified memory with confidence scoring

**Body**: `VerifiedMemoryRequest`
- `content` (string): Verified content
- `confidence` (float, default=0.9): Confidence level
- `source` (string, default="verified"): Source information
- `user_id` (string, default="user"): User identifier
- `metadata` (object, optional): Additional metadata

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/memory/save-verified" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Neo4j provides 26% better performance for relationship queries",
    "confidence": 0.92,
    "source": "performance_testing",
    "user_id": "demo_user",
    "metadata": {
      "category": "performance",
      "verified": true,
      "benchmark_date": "2025-01-01"
    }
  }'
```

**Response**: `{"memory_id": "verified_123", "confidence": 0.92}`

**Test Screenshot**: `assets/screenshots/save_verified_memory_success.png`

---

### Endpoint 5: `POST /graph/save-memory`
**Purpose**: Save memory with graph relationships

**Body**: `MemoryRequest` (with graph metadata)

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/graph/save-memory" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "John leads the DevOps team using Kubernetes and Docker",
    "user_id": "demo_user",
    "metadata": {
      "category": "team",
      "entities": ["John", "DevOps", "Kubernetes", "Docker"],
      "relationships": ["leads", "uses"]
    }
  }'
```

**Response**: `{"memory_id": "graph_123", "entities_extracted": 4}`

**Test Screenshot**: `assets/screenshots/save_graph_memory_success.png`

---

### Endpoint 6: `POST /graph/search`
**Purpose**: Search graph memories with relationship context

**Body**: `SearchRequest`

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/graph/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "team leadership",
    "user_id": "demo_user",
    "limit": 5
  }'
```

**Response**: Graph search results with relationship paths

**Test Screenshot**: `assets/screenshots/search_graph_memory_success.png`

---

### Endpoint 7: `POST /graph/entity-relationships`
**Purpose**: Get relationships for specific entity

**Body**: `EntityRequest`
- `entity_name` (string): Entity to analyze
- `user_id` (string, default="user"): User identifier

**cURL Example**:
```bash
curl -X POST "http://localhost:8051/graph/entity-relationships" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "John",
    "user_id": "demo_user"
  }'
```

**Response**: Entity relationships with connection strengths

**Test Screenshot**: `assets/screenshots/entity_relationships_success.png`

---

### Endpoint 8: `GET /graph/status`
**Purpose**: Check graph database status

**cURL Example**:
```bash
curl -X GET "http://localhost:8051/graph/status"
```

**Response**: Graph status with node/relationship counts

**Test Screenshot**: `assets/screenshots/graph_status_success.png`

---

### Endpoint 9: `GET /health`
**Purpose**: System health check

**cURL Example**:
```bash
curl -X GET "http://localhost:8051/health"
```

**Response**: `{"status": "healthy", "components": {...}}`

**Test Screenshot**: `assets/screenshots/health_check_success.png`

---

### Additional Endpoints (10-15)

The remaining endpoints (`/memory/get-context`, `/memory/validate-project-context`, `/memory/resolve-conflict`, `/memory/audit-quality`, `/memory/save-milestone`, `/memory/get-project-state`, `/memory/track-evolution`) follow similar patterns with specialized functionality for advanced memory management.

---

## 🧪 Testing Integration

### MCP Inspector Testing
All MCP tools are tested through MCP Inspector:
1. Connection verification
2. Parameter validation  
3. Response validation
4. Error handling

### Playwright API Testing
All REST endpoints are tested with Playwright:
1. Successful API calls
2. Error conditions
3. Response validation
4. Screenshot generation

### Results Location
- **Screenshots**: `assets/screenshots/`
- **Test Reports**: `docs/mcp-testing-report.md`
- **Test Scripts**: `scripts/test_all.sh`, `tests/test_api.py`

---

## 🔗 Integration Examples

### Cursor IDE Integration
```json
{
  "mcpServers": {
    "unified-memory": {
      "command": "python",
      "args": ["src/main.py"],
      "env": {}
    }
  }
}
```

### Direct API Usage
```javascript
// JavaScript example
const response = await fetch('http://localhost:8051/memory/save', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'Important information to remember',
    user_id: 'user123'
  })
});
```

### Python SDK Usage
```python
# Python example
import requests

response = requests.post('http://localhost:8051/memory/search', json={
    'query': 'Docker optimization',
    'user_id': 'user123',
    'limit': 5
})
```

---

## 📊 Performance Metrics

- **MCP Tools**: ~10ms response time
- **REST API**: ~50ms response time  
- **Graph Operations**: ~100ms for complex queries
- **Concurrent Users**: 1000+ with proper scaling
- **Memory Capacity**: Limited only by storage backend

---

This reference covers all 25 tools and endpoints in the Unified Memory System, providing complete integration guidance for developers and AI agents. 