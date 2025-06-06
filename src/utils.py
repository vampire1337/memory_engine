from mem0 import Memory
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Custom instructions for memory processing
# These aren't being used right now but Mem0 does support adding custom prompting
# for handling memory retrieval and processing.
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Key Information: Identify and save the most important details.
- Context: Capture the surrounding context to understand the memory's relevance.
- Connections: Note any relationships to other topics or memories.
- Importance: Highlight why this information might be valuable in the future.
- Source: Record where this information came from when applicable.
"""

@dataclass
class MemoryRecord:
    """Enhanced memory record with versioning and validation"""
    id: str
    content: str
    project_id: str
    category: str  # "architecture", "problem", "solution", "status", "decision"
    confidence_level: int  # 1-10 scale
    source: str  # "user_input", "code_analysis", "documentation"
    created_at: str
    updated_at: str
    expires_at: Optional[str]
    version: int
    status: str  # "active", "deprecated", "conflicted"
    superseded_by: Optional[str]
    conflict_with: List[str] 
    validation_needed: bool
    tags: List[str]
    metadata: Dict[str, Any]

def create_memory_id(content: str, project_id: str) -> str:
    """Create unique memory ID based on content and project"""
    hash_input = f"{content}_{project_id}_{datetime.now().isoformat()}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def calculate_content_similarity(content1: str, content2: str) -> float:
    """Simple similarity calculation - can be enhanced with ML models"""
    words1 = set(content1.lower().split())
    words2 = set(content2.lower().split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0.0

def detect_potential_conflicts(new_content: str, existing_memories: List[Dict]) -> List[str]:
    """Detect potential conflicts with existing memories"""
    conflicts = []
    
    for memory in existing_memories:
        similarity = calculate_content_similarity(new_content, memory.get('memory', ''))
        
        # High similarity with active memory might indicate conflict
        if similarity > 0.7 and memory.get('metadata', {}).get('status') == 'active':
            conflicts.append(memory.get('id', ''))
            
    return conflicts

def create_enhanced_metadata(
    project_id: str,
    category: str,
    confidence_level: int,
    source: str,
    expires_at: Optional[str] = None,
    tags: List[str] = None,
    conflicts: List[str] = None
) -> Dict[str, Any]:
    """Create enhanced metadata for memory record"""
    now = datetime.now().isoformat()
    
    return {
        "project_id": project_id,
        "category": category,
        "confidence_level": confidence_level,
        "source": source,
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at,
        "version": 1,
        "status": "active",
        "superseded_by": None,
        "conflict_with": conflicts or [],
        "validation_needed": False,
        "tags": tags or [],
        "accuracy_validated": False,
        "last_accessed": now
    }

def is_memory_expired(memory: Dict) -> bool:
    """Check if memory has expired"""
    expires_at = memory.get('metadata', {}).get('expires_at')
    if not expires_at:
        return False
        
    try:
        expiry_date = datetime.fromisoformat(expires_at)
        return datetime.now() > expiry_date
    except (ValueError, TypeError):
        return False

def should_validate_accuracy(memory: Dict) -> bool:
    """Determine if memory needs accuracy validation"""
    metadata = memory.get('metadata', {})
    
    # Need validation if:
    # 1. Never validated before
    # 2. Old memory (>30 days) with high importance
    # 3. Marked as needing validation
    # 4. Low confidence level
    
    if metadata.get('validation_needed', False):
        return True
        
    if not metadata.get('accuracy_validated', False):
        return True
        
    if metadata.get('confidence_level', 10) < 5:
        return True
        
    created_at = metadata.get('created_at')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at)
            days_old = (datetime.now() - created_date).days
            if days_old > 30 and metadata.get('category') in ['architecture', 'decision']:
                return True
        except (ValueError, TypeError):
            pass
            
    return False

def filter_accurate_memories(memories: List[Dict], min_confidence: int = 5) -> List[Dict]:
    """Filter memories to return only accurate, non-expired ones"""
    filtered = []
    
    for memory in memories:
        metadata = memory.get('metadata', {})
        
        # Skip if expired
        if is_memory_expired(memory):
            continue
            
        # Skip if deprecated
        if metadata.get('status') == 'deprecated':
            continue
            
        # Skip if conflicted and not resolved
        if metadata.get('status') == 'conflicted':
            continue
            
        # Skip if confidence too low
        if metadata.get('confidence_level', 0) < min_confidence:
            continue
            
        filtered.append(memory)
    
    # Sort by confidence level and recency
    filtered.sort(key=lambda m: (
        m.get('metadata', {}).get('confidence_level', 0),
        m.get('metadata', {}).get('updated_at', '')
    ), reverse=True)
    
    return filtered

def get_mem0_config(provider: str = "openai") -> dict:
    """
    Получить конфигурацию для Mem0
    """
    base_config = {
        "version": "v1.1"
    }
    
    if provider == "openai":
        return {
            **base_config,
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                    # Убираю embedding_dims - не поддерживается в текущей версии
                }
            },
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.1
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "unified-memory-v2",
                    "path": "./data/chroma_db"
                }
            }
        }
    elif provider == "nomic":
        return {
            **base_config,
            "embedder": {
                "provider": "nomic",
                "config": {
                    "model": "nomic-embed-text"
                    # Убираю embedding_dims - не поддерживается в текущей версии
                }
            },
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.1
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "unified-memory-v2",
                    "path": "./data/chroma_db"
                }
            }
        }

def get_mem0_client():
    # Get LLM provider and configuration
    llm_provider = os.getenv('LLM_PROVIDER')
    llm_api_key = os.getenv('LLM_API_KEY')
    llm_model = os.getenv('LLM_CHOICE')
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
    
    # Initialize config dictionary
    config = {}
    
    # Configure LLM based on provider
    if llm_provider == 'openai' or llm_provider == 'openrouter':
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000,
            }
        }
        
        # Set API key in environment if not already set
        if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = llm_api_key
            
        # For OpenRouter, set the specific API key
        if llm_provider == 'openrouter' and llm_api_key:
            os.environ["OPENROUTER_API_KEY"] = llm_api_key
    
    elif llm_provider == 'ollama':
        config["llm"] = {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000,
            }
        }
        
        # Set base URL for Ollama if provided
        llm_base_url = os.getenv('LLM_BASE_URL')
        if llm_base_url:
            config["llm"]["config"]["ollama_base_url"] = llm_base_url
    
    # Configure embedder based on provider
    if llm_provider == 'openai':
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "model": embedding_model or "text-embedding-3-small"
                # Убираю embedding_dims - не поддерживается в текущей версии
            }
        }
        
        # Set API key in environment if not already set
        if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = llm_api_key
    
    elif llm_provider == 'ollama':
        config["embedder"] = {
            "provider": "ollama",
            "config": {
                "model": embedding_model or "nomic-embed-text"
                # Убираю embedding_dims - не поддерживается в текущей версии
            }
        }
        
        # Set base URL for Ollama if provided
        embedding_base_url = os.getenv('LLM_BASE_URL')
        if embedding_base_url:
            config["embedder"]["config"]["ollama_base_url"] = embedding_base_url
    
    # Configure Supabase vector store - REMOVED for testing
    # Use default in-memory vector store instead

    # config["custom_fact_extraction_prompt"] = CUSTOM_INSTRUCTIONS
    
    # Create and return the Memory client
    return Memory.from_config(config)

def safe_get_memories(memories_result):
    """Safely extract memories from different result formats."""
    if isinstance(memories_result, dict) and "results" in memories_result:
        return memories_result["results"]
    elif isinstance(memories_result, list):
        return memories_result
    elif memories_result is None:
        return []
    else:
        # If it's a single memory object, wrap in list
        return [memories_result] if hasattr(memories_result, 'get') else []

def get_memory_metadata(memory_item):
    """Extract metadata from memory item safely."""
    if isinstance(memory_item, str):
        # Basic memory format - just text, no metadata
        return {
            'content': memory_item,
            'confidence_level': 5,  # Default
            'category': 'unknown',
            'status': 'active',
            'project_id': None,
            'updated_at': None,
            'expires_at': None,
            'tags': [],
            'source': 'unknown',
            'memory_id': None,
            'version': 1
        }
    elif isinstance(memory_item, dict):
        # Enhanced memory format with metadata
        metadata = memory_item.get('metadata', {})
        return {
            'content': memory_item.get('memory', memory_item.get('content', '')),
            'confidence_level': metadata.get('confidence_level', 5),
            'category': metadata.get('category', 'unknown'),
            'status': metadata.get('status', 'active'),
            'project_id': metadata.get('project_id'),
            'updated_at': metadata.get('updated_at'),
            'expires_at': metadata.get('expires_at'),
            'tags': metadata.get('tags', []),
            'source': metadata.get('source', 'unknown'),
            'memory_id': memory_item.get('id'),
            'version': metadata.get('version', 1)
        }
    else:
        # Unknown format
        return {
            'content': str(memory_item),
            'confidence_level': 1,  # Low confidence for unknown format
            'category': 'unknown',
            'status': 'active',
            'project_id': None,
            'updated_at': None,
            'expires_at': None,
            'tags': [],
            'source': 'unknown',
            'memory_id': None,
            'version': 1
        }

def simulate_enhanced_search(mem0_client, query, project_id=None, min_confidence=5, limit=5):
    """Simulate enhanced search with basic filtering since real API doesn't support metadata search."""
    try:
        # Get all memories first
        all_memories = mem0_client.search(query, user_id="user", limit=50)
        memory_list = safe_get_memories(all_memories)
        
        filtered_memories = []
        for memory_item in memory_list:
            if memory_item is None:  # Skip None objects
                continue
                
            metadata = get_memory_metadata(memory_item)
            
            # Estimate confidence and project for basic filtering
            estimated_confidence = estimate_content_confidence(metadata['content'])
            estimated_project = extract_project_from_content(metadata['content'])
            
            # Apply filters
            if estimated_confidence >= min_confidence:
                if not project_id or (estimated_project and estimated_project.lower() == project_id.lower()):
                    metadata['confidence_level'] = estimated_confidence
                    metadata['estimated_project'] = estimated_project or project_id
                    filtered_memories.append(metadata)
        
        # Sort by estimated confidence and return top results
        filtered_memories = [m for m in filtered_memories if m is not None]  # Remove None objects
        filtered_memories.sort(key=lambda x: x.get('confidence_level', 0) if x else 0, reverse=True)
        return filtered_memories[:limit]
        
    except Exception as e:
        print(f"Error in simulate_enhanced_search: {e}")
        return []

def estimate_content_confidence(content):
    """
    Estimate confidence level based on content characteristics.
    This is a basic heuristic since we don't have real metadata.
    """
    confidence = 5  # Base confidence
    
    # Longer content tends to be more detailed and confident
    if len(content) > 200:
        confidence += 1
    if len(content) > 500:
        confidence += 1
        
    # Check for confident language patterns
    confident_keywords = [
        "решено", "исправлено", "завершено", "готово", "протестировано",
        "подтверждено", "verified", "fixed", "completed", "tested", "confirmed"
    ]
    
    for keyword in confident_keywords:
        if keyword in content.lower():
            confidence += 1
            break
            
    # Check for uncertain language patterns
    uncertain_keywords = [
        "возможно", "может быть", "неуверен", "проблема", "ошибка",
        "maybe", "possibly", "unsure", "problem", "error", "issue"
    ]
    
    for keyword in uncertain_keywords:
        if keyword in content.lower():
            confidence -= 1
            break
            
    # Clamp to valid range
    return max(1, min(10, confidence))

def extract_project_from_content(content):
    """
    Try to extract project information from content.
    Basic pattern matching approach.
    """
    import re
    
    # Look for common project patterns
    patterns = [
        r'проект[:\s]+([a-zA-Z0-9\-_]+)',
        r'project[:\s]+([a-zA-Z0-9\-_]+)',
        r'([a-zA-Z0-9\-_]+)\s+проект',
        r'([a-zA-Z0-9\-_]+)\s+project'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
            
    return None

def categorize_content(content):
    """
    Basic content categorization based on keywords.
    """
    content_lower = content.lower()
    
    # Architecture keywords
    if any(word in content_lower for word in ['архитектура', 'структура', 'компонент', 'architecture', 'structure', 'component']):
        return 'architecture'
        
    # Problem keywords  
    if any(word in content_lower for word in ['проблема', 'ошибка', 'баг', 'problem', 'error', 'bug', 'issue']):
        return 'problem'
        
    # Solution keywords
    if any(word in content_lower for word in ['решение', 'исправление', 'фикс', 'solution', 'fix', 'resolved']):
        return 'solution'
        
    # Status keywords
    if any(word in content_lower for word in ['статус', 'состояние', 'готово', 'завершено', 'status', 'state', 'ready', 'completed']):
        return 'status'
        
    return 'unknown'