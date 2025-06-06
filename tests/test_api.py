"""
Unified Memory System - API Tests
Tests for all major API endpoints and functionality
"""

import pytest
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8051"

class TestUnifiedMemoryAPI:
    """Test suite for Unified Memory System API"""
    
    @classmethod
    def setup_class(cls):
        """Wait for service to be ready"""
        for _ in range(30):
            try:
                response = requests.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        else:
            pytest.fail("Service not ready after 30 seconds")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_save_memory(self):
        """Test saving memory"""
        memory_data = {
            "content": "Test memory for API testing",
            "user_id": "test_user_api",
            "agent_id": "pytest_agent",
            "session_id": "test_session",
            "metadata": {
                "category": "test",
                "priority": "medium",
                "tags": ["api", "test", "pytest"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/memory/save",
            json=memory_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "memory_id" in data
        assert "status" in data
    
    def test_search_memories(self):
        """Test searching memories"""
        search_data = {
            "query": "test memory",
            "user_id": "test_user_api",
            "limit": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/memory/search",
            json=search_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "memories" in data or "results" in data
    
    def test_get_all_memories(self):
        """Test getting all memories"""
        get_all_data = {
            "user_id": "test_user_api"
        }
        
        response = requests.post(
            f"{BASE_URL}/memory/get-all",
            json=get_all_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
    
    def test_graph_status(self):
        """Test graph status endpoint"""
        response = requests.get(f"{BASE_URL}/graph/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_save_graph_memory(self):
        """Test saving graph memory"""
        graph_memory_data = {
            "content": "Graph memory for API testing with relationships",
            "user_id": "test_user_api",
            "metadata": {
                "category": "graph_test",
                "entities": ["API", "Testing", "Graph"],
                "relationships": ["uses", "tests"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/graph/save-memory",
            json=graph_memory_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "memory_id" in data or "status" in data
    
    def test_search_graph_memory(self):
        """Test searching graph memory"""
        graph_search_data = {
            "query": "graph testing",
            "user_id": "test_user_api",
            "limit": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/graph/search",
            json=graph_search_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
    
    def test_entity_relationships(self):
        """Test entity relationships endpoint"""
        entity_data = {
            "entity_name": "test_user_api",
            "user_id": "test_user_api"
        }
        
        response = requests.post(
            f"{BASE_URL}/graph/entity-relationships",
            json=entity_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
    
    def test_save_verified_memory(self):
        """Test saving verified memory"""
        verified_data = {
            "content": "Verified memory for API testing with high confidence",
            "user_id": "test_user_api",
            "confidence": 0.95,
            "source": "api_test",
            "verification_method": "automated_test",
            "metadata": {
                "category": "verified_test",
                "priority": "high"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/memory/save-verified",
            json=verified_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "memory_id" in data or "status" in data
    
    def test_save_project_milestone(self):
        """Test saving project milestone"""
        milestone_data = {
            "project_name": "unified_memory_api_test",
            "milestone": "v1.0.0-test",
            "description": "API testing milestone for verification",
            "user_id": "test_user_api",
            "metadata": {
                "category": "milestone",
                "priority": "high",
                "test_run": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/memory/save-milestone",
            json=milestone_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "memory_id" in data or "status" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 