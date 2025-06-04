import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import (
    save_verified_memory, get_accurate_context, validate_project_context,
    resolve_context_conflict, audit_memory_quality, save_project_milestone,
    get_current_project_state, track_project_evolution
)
from utils import (
    create_enhanced_metadata, detect_potential_conflicts, filter_accurate_memories,
    is_memory_expired, should_validate_accuracy, create_memory_id
)

class TestEnhancedMemoryTools:
    """Comprehensive tests for enhanced memory system with accuracy guarantees"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context for MCP tools"""
        ctx = Mock()
        ctx.request_context = Mock()
        ctx.request_context.lifespan_context = Mock()
        ctx.request_context.lifespan_context.mem0_client = Mock()
        return ctx
    
    @pytest.fixture
    def sample_memories(self):
        """Sample memory data for testing"""
        return [
            {
                "id": "mem_001",
                "memory": "Project uses PostgreSQL database",
                "metadata": {
                    "project_id": "test_project",
                    "category": "architecture",
                    "confidence_level": 9,
                    "status": "active",
                    "created_at": "2025-01-01T10:00:00",
                    "updated_at": "2025-01-01T10:00:00"
                }
            },
            {
                "id": "mem_002", 
                "memory": "Project uses MySQL database",
                "metadata": {
                    "project_id": "test_project",
                    "category": "architecture",
                    "confidence_level": 7,
                    "status": "active",
                    "created_at": "2025-01-02T10:00:00",
                    "updated_at": "2025-01-02T10:00:00"
                }
            },
            {
                "id": "mem_003",
                "memory": "Performance issue resolved with caching",
                "metadata": {
                    "project_id": "test_project",
                    "category": "solution",
                    "confidence_level": 8,
                    "status": "active",
                    "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
                }
            }
        ]

    # Tests for utility functions
    def test_create_memory_id(self):
        """Test unique memory ID generation"""
        id1 = create_memory_id("test content", "project1")
        id2 = create_memory_id("test content", "project1")
        id3 = create_memory_id("different content", "project1")
        
        # IDs should be different due to timestamp
        assert id1 != id2
        assert id1 != id3
        assert len(id1) == 32  # MD5 hash length

    def test_detect_potential_conflicts(self, sample_memories):
        """Test conflict detection between similar memories"""
        new_content = "Project uses PostgreSQL for data storage"
        conflicts = detect_potential_conflicts(new_content, sample_memories)
        
        # Should detect conflict with PostgreSQL memory
        assert len(conflicts) > 0
        assert "mem_001" in conflicts

    def test_filter_accurate_memories(self, sample_memories):
        """Test filtering for accurate, non-expired memories"""
        # Add an expired memory
        expired_memory = {
            "id": "mem_expired",
            "memory": "Outdated information",
            "metadata": {
                "status": "active",
                "confidence_level": 8,
                "expires_at": (datetime.now() - timedelta(days=1)).isoformat()
            }
        }
        test_memories = sample_memories + [expired_memory]
        
        filtered = filter_accurate_memories(test_memories, min_confidence=7)
        
        # Should exclude expired memory
        filtered_ids = [m.get('id') for m in filtered]
        assert "mem_expired" not in filtered_ids
        assert len(filtered) == 3  # Original 3 memories

    def test_is_memory_expired(self):
        """Test memory expiration detection"""
        # Non-expired memory
        future_memory = {
            "metadata": {
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
            }
        }
        assert not is_memory_expired(future_memory)
        
        # Expired memory
        past_memory = {
            "metadata": {
                "expires_at": (datetime.now() - timedelta(days=1)).isoformat()
            }
        }
        assert is_memory_expired(past_memory)
        
        # Memory without expiration
        no_expiry_memory = {"metadata": {}}
        assert not is_memory_expired(no_expiry_memory)

    # Tests for main tools
    @pytest.mark.asyncio
    async def test_save_verified_memory_success(self, mock_context):
        """Test successful verified memory saving"""
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": []
        }
        mock_context.request_context.lifespan_context.mem0_client.add.return_value = {"id": "new_mem_001"}
        
        result = await save_verified_memory(
            mock_context,
            content="Test memory content",
            project_id="test_project",
            category="architecture",
            confidence_level=8,
            source="user_input"
        )
        
        assert "✅ Memory saved successfully" in result
        assert "confidence level 8/10" in result

    @pytest.mark.asyncio
    async def test_save_verified_memory_with_conflicts(self, mock_context, sample_memories):
        """Test verified memory saving with conflict detection"""
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": sample_memories
        }
        mock_context.request_context.lifespan_context.mem0_client.add.return_value = {"id": "new_mem_002"}
        
        result = await save_verified_memory(
            mock_context,
            content="Project uses PostgreSQL database for all operations",
            project_id="test_project", 
            category="architecture",
            confidence_level=9,
            source="code_analysis"
        )
        
        assert "⚠️  Memory saved but CONFLICTS detected" in result
        assert "resolve_context_conflict" in result

    @pytest.mark.asyncio
    async def test_get_accurate_context(self, mock_context, sample_memories):
        """Test accurate context retrieval with filtering"""
        mock_context.request_context.lifespan_context.mem0_client.search.return_value = {
            "results": sample_memories
        }
        
        result = await get_accurate_context(
            mock_context,
            query="database architecture",
            project_id="test_project",
            min_confidence=8
        )
        
        result_data = json.loads(result)
        assert result_data["query"] == "database architecture"
        assert result_data["min_confidence_applied"] == 8
        assert len(result_data["accurate_context"]) > 0

    @pytest.mark.asyncio
    async def test_validate_project_context(self, mock_context, sample_memories):
        """Test project context validation"""
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": sample_memories
        }
        
        result = await validate_project_context(mock_context, "test_project")
        
        validation_data = json.loads(result)
        assert validation_data["project_id"] == "test_project"
        assert validation_data["total_memories"] == 3
        assert "recommendations" in validation_data

    @pytest.mark.asyncio
    async def test_resolve_context_conflict(self, mock_context, sample_memories):
        """Test conflict resolution between memories"""
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": sample_memories
        }
        mock_context.request_context.lifespan_context.mem0_client.add.return_value = {"id": "resolved_mem"}
        
        result = await resolve_context_conflict(
            mock_context,
            conflicting_memory_ids="mem_001,mem_002",
            correct_content="Project uses PostgreSQL database exclusively",
            resolution_reason="PostgreSQL confirmed by latest architecture review"
        )
        
        assert "✅ Conflict resolved!" in result
        assert "Deprecated 2 conflicting memories" in result

    @pytest.mark.asyncio
    async def test_audit_memory_quality(self, mock_context, sample_memories):
        """Test comprehensive memory quality audit"""
        # Add some problematic memories for testing
        problematic_memories = sample_memories + [
            {
                "id": "mem_expired",
                "memory": "Expired info",
                "metadata": {
                    "status": "active",
                    "confidence_level": 3,
                    "expires_at": (datetime.now() - timedelta(days=1)).isoformat()
                }
            },
            {
                "id": "mem_conflicted",
                "memory": "Conflicted info",
                "metadata": {
                    "status": "conflicted",
                    "confidence_level": 8
                }
            }
        ]
        
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": problematic_memories
        }
        
        result = await audit_memory_quality(mock_context)
        
        audit_data = json.loads(result)
        assert "audit_scope" in audit_data
        assert "health_score" in audit_data
        assert "recommendations" in audit_data
        assert audit_data["quality_issues"]["expired_memories"] > 0
        assert audit_data["quality_issues"]["conflicted_memories"] > 0

    @pytest.mark.asyncio
    async def test_save_project_milestone(self, mock_context):
        """Test project milestone saving"""
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": []
        }
        mock_context.request_context.lifespan_context.mem0_client.add.return_value = {"id": "milestone_001"}
        
        result = await save_project_milestone(
            mock_context,
            project_id="test_project",
            milestone_type="architecture_decision",
            content="Decided to use microservices architecture",
            impact_level=9,
            tags="microservices,architecture"
        )
        
        assert "📍 Project milestone saved" in result
        assert "Architecture Decision" in result

    @pytest.mark.asyncio
    async def test_get_current_project_state(self, mock_context, sample_memories):
        """Test current project state retrieval"""
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": sample_memories
        }
        
        result = await get_current_project_state(mock_context, "test_project")
        
        state_data = json.loads(result)
        assert state_data["project_id"] == "test_project"
        assert "current_state_by_category" in state_data
        assert "recent_milestones" in state_data

    @pytest.mark.asyncio
    async def test_track_project_evolution(self, mock_context, sample_memories):
        """Test project evolution tracking"""
        # Add some evolution data
        evolution_memories = sample_memories + [
            {
                "id": "mem_deprecated",
                "memory": "Old approach using files",
                "metadata": {
                    "project_id": "test_project",
                    "category": "architecture",
                    "status": "deprecated",
                    "created_at": "2024-12-01T10:00:00",
                    "deprecated_reason": "Moved to database approach"
                }
            }
        ]
        
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": evolution_memories
        }
        
        result = await track_project_evolution(mock_context, "test_project", "architecture")
        
        evolution_data = json.loads(result)
        assert evolution_data["project_id"] == "test_project"
        assert evolution_data["tracking_scope"] == "architecture"
        assert "evolution_timeline" in evolution_data
        assert "evolution_summary" in evolution_data

class TestAccuracyScenarios:
    """Test specific accuracy scenarios"""
    
    @pytest.mark.asyncio
    async def test_accuracy_scenario_conflicting_tech_stack(self, mock_context):
        """Test scenario: Conflicting technology stack information"""
        conflicting_memories = [
            {
                "id": "tech_001",
                "memory": "Frontend built with React",
                "metadata": {
                    "project_id": "web_app",
                    "category": "architecture",
                    "confidence_level": 8,
                    "status": "active"
                }
            },
            {
                "id": "tech_002", 
                "memory": "Frontend uses Vue.js framework",
                "metadata": {
                    "project_id": "web_app",
                    "category": "architecture", 
                    "confidence_level": 7,
                    "status": "active"
                }
            }
        ]
        
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": conflicting_memories
        }
        
        # Validate should detect the conflict
        result = await validate_project_context(mock_context, "web_app")
        validation_data = json.loads(result)
        
        assert validation_data["total_memories"] == 2
        # Should recommend resolving conflicts due to similar content

    @pytest.mark.asyncio
    async def test_accuracy_scenario_outdated_status(self, mock_context):
        """Test scenario: Outdated project status information"""
        outdated_memories = [
            {
                "id": "status_001",
                "memory": "Project is in planning phase",
                "metadata": {
                    "project_id": "new_feature",
                    "category": "status",
                    "confidence_level": 9,
                    "status": "active",
                    "created_at": (datetime.now() - timedelta(days=45)).isoformat()
                }
            }
        ]
        
        mock_context.request_context.lifespan_context.mem0_client.get_all.return_value = {
            "results": outdated_memories
        }
        
        # Should flag for validation due to age
        result = await validate_project_context(mock_context, "new_feature")
        validation_data = json.loads(result)
        
        assert "needs_validation" in validation_data["analysis"]

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 