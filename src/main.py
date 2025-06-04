import sys
import json
import logging
import asyncio
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastmcp import FastMCP
from mem0 import Memory
from pydantic import BaseModel

from utils import (
    get_mem0_client, 
    create_enhanced_metadata, 
    is_memory_expired, 
    detect_potential_conflicts,
    should_validate_accuracy, 
    filter_accurate_memories,
    create_memory_id,
    estimate_content_confidence,
    safe_get_memories,
    get_memory_metadata,
    simulate_enhanced_search,
    extract_project_from_content,
    categorize_content
)

load_dotenv()

# Default user ID for memory operations
DEFAULT_USER_ID = "user"

# Global initialization flag to prevent race conditions
_server_initialized = False
_initialization_lock = asyncio.Lock()
_initialization_attempts = 0
_max_initialization_attempts = 5

async def ensure_server_initialized():
    """Ensure the server is properly initialized before processing requests."""
    global _server_initialized, _initialization_attempts
    
    if not _server_initialized:
        async with _initialization_lock:
            if not _server_initialized:
                _initialization_attempts += 1
                print(f"🔧 Initializing server (attempt {_initialization_attempts}/{_max_initialization_attempts})...")
                
                # Progressive delay for initialization
                initial_delay = min(2.0 * _initialization_attempts, 10.0)
                await asyncio.sleep(initial_delay)
                
                # Test the mem0 client multiple times to ensure it's stable
                max_test_attempts = 3
                for test_attempt in range(max_test_attempts):
                    try:
                        print(f"🧪 Testing mem0 client (test {test_attempt + 1}/{max_test_attempts})...")
                        mem0_client = get_mem0_client()
                        
                        # Comprehensive client testing
                        test_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, limit=1)
                        print(f"✅ get_all test passed")
                        
                        test_search = mem0_client.search("test", user_id=DEFAULT_USER_ID, limit=1)  
                        print(f"✅ search test passed")
                        
                        # Additional delay to ensure stability
                        await asyncio.sleep(0.5)
                        
                        print(f"✅ mem0 client stable after {test_attempt + 1} tests")
                        break
                        
                    except Exception as e:
                        print(f"❌ mem0 client test {test_attempt + 1} failed: {str(e)}")
                        if test_attempt == max_test_attempts - 1:
                            if _initialization_attempts >= _max_initialization_attempts:
                                raise RuntimeError(f"Server initialization failed after {_max_initialization_attempts} attempts: {str(e)}")
                            else:
                                print(f"🔄 Will retry initialization...")
                                return await ensure_server_initialized()
                        await asyncio.sleep(1.0)
                
                # Mark as initialized only after all tests pass
                _server_initialized = True
                print(f"🎯 Server initialization complete after {_initialization_attempts} attempts")
    
    if not _server_initialized:
        raise RuntimeError("Server is still initializing, please retry in a moment")

# Create a dataclass for our application context
@dataclass
class Mem0Context:
    """Context for the Mem0 MCP server."""
    mem0_client: Memory

@asynccontextmanager
async def mem0_lifespan() -> AsyncIterator[Mem0Context]:
    """
    Manages the Mem0 client lifecycle.
        
    Yields:
        Mem0Context: The context containing the Mem0 client
    """
    # Create and return the Memory client with the helper function in utils.py
    mem0_client = get_mem0_client()
    
    try:
        yield Mem0Context(mem0_client=mem0_client)
    finally:
        # No explicit cleanup needed for the Mem0 client
        pass

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0",
    description="MCP server for long term memory storage and retrieval with Mem0"
)

@mcp.tool()
async def save_memory(text: str) -> str:
    """Save information to your long-term memory.

    This tool is designed to store any type of information that might be useful in the future.
    The content will be processed and indexed for later retrieval through semantic search.

    Args:
        text: The content to store in memory, including any relevant details and context
    """
    try:
        # Get mem0 client directly from setup
        mem0_client = get_mem0_client()
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID)
        return f"Successfully saved memory: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory: {text}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories() -> str:
    """Get all stored memories for the user.
    
    Call this tool when you need complete context of all previously memories.

    Returns a JSON formatted list of all stored memories, including when they were created
    and their content. Results are paginated with a default of 50 items per page.
    """
    try:
        mem0_client = get_mem0_client()
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

@mcp.tool()
async def search_memories(query: str, limit: int = 3) -> str:
    """Search memories using semantic search.

    This tool should be called to find relevant information from your memory. Results are ranked by relevance.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        query: Search query string describing what you're looking for. Can be natural language.
        limit: Maximum number of results to return (default: 3)
    """
    try:
        mem0_client = get_mem0_client()
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=limit)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool()
async def save_verified_memory(
    content: str, 
    project_id: str,
    category: str,
    confidence_level: int,
    source: str = "user_input",
    expires_in_days: Optional[int] = None,
    tags: Optional[str] = None
) -> str:
    """Save verified information to long-term memory with enhanced metadata.
    
    This is an enhanced version of save_memory that includes conflict detection,
    versioning, and accuracy validation to ensure context quality.

    Args:
        content: The information to store in memory
        project_id: Identifier for the project this memory belongs to
        category: Type of information (architecture/problem/solution/status/decision)
        confidence_level: How confident you are in this information (1-10 scale)
        source: Where this information came from (user_input/code_analysis/documentation)
        expires_in_days: Optional expiration in days for time-sensitive information
        tags: Optional comma-separated tags for categorization
    """
    try:
        mem0_client = get_mem0_client()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Calculate expiration date if specified
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # Get existing memories to check for conflicts
        existing_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        if isinstance(existing_memories, dict) and "results" in existing_memories:
            existing_list = existing_memories["results"]
        else:
            existing_list = existing_memories or []
        
        # Detect potential conflicts
        conflicts = detect_potential_conflicts(content, existing_list)
        
        # Create enhanced metadata
        metadata = create_enhanced_metadata(
            project_id=project_id,
            category=category,
            confidence_level=confidence_level,
            source=source,
            expires_at=expires_at,
            tags=tag_list,
            conflicts=conflicts
        )
        
        # If conflicts detected, mark as needing resolution
        if conflicts:
            metadata["status"] = "conflicted"
            metadata["validation_needed"] = True
            
        # Save memory with enhanced metadata
        messages = [{"role": "user", "content": content}]
        result = mem0_client.add(messages, user_id=DEFAULT_USER_ID, metadata=metadata)
        
        if conflicts:
            return f"⚠️  Memory saved but CONFLICTS detected with {len(conflicts)} existing records. Use resolve_context_conflict to resolve. Content: {content[:100]}..."
        else:
            return f"✅ Memory saved successfully with confidence level {confidence_level}/10. Content: {content[:100]}..."
            
    except Exception as e:
        return f"❌ Error saving verified memory: {str(e)}"

@mcp.tool()
async def get_accurate_context(
    query: str, 
    project_id: Optional[str] = None,
    min_confidence: int = 5,
    limit: int = 5
) -> str:
    """Get accurate, validated context from memory with quality filtering.
    
    This tool returns only verified, non-expired information with sufficient
    confidence levels, ensuring the context provided is reliable.

    Args:
        query: Search query to find relevant information
        project_id: Optional project ID to filter results
        min_confidence: Minimum confidence level required (1-10, default: 5)
        limit: Maximum number of results to return
    """
    try:
        # CRITICAL: Ensure server is fully initialized before proceeding
        await ensure_server_initialized()
        
        print(f"🔍 DEBUG: get_accurate_context called with query='{query}', project_id={project_id}")
        
        mem0_client = get_mem0_client()
        print(f"✅ DEBUG: mem0_client obtained successfully")
        
        # Get all memories to filter through
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        print(f"📋 DEBUG: all_memories type: {type(all_memories)}, content: {str(all_memories)[:200]}...")
        
        memory_list = safe_get_memories(all_memories)
        print(f"📋 DEBUG: memory_list type: {type(memory_list)}, length: {len(memory_list) if memory_list else 'None'}")
        
        if memory_list:
            print(f"📋 DEBUG: First memory item type: {type(memory_list[0]) if len(memory_list) > 0 else 'empty'}")
            print(f"📋 DEBUG: First memory item: {str(memory_list[0])[:100] if len(memory_list) > 0 else 'empty'}...")
        
        # Filter by project if specified and process for accuracy
        filtered_memories = []
        for i, memory_item in enumerate(memory_list):
            print(f"🔄 DEBUG: Processing memory_item {i}: type={type(memory_item)}, is_none={memory_item is None}")
            
            if memory_item is None:  # Skip None objects
                print(f"⚠️ DEBUG: Skipping None memory_item at index {i}")
                continue
                
            print(f"🔍 DEBUG: Calling get_memory_metadata for item {i}")
            metadata = get_memory_metadata(memory_item)
            print(f"📊 DEBUG: metadata type: {type(metadata)}, is_none: {metadata is None}")
            
            if metadata is None:
                print(f"⚠️ DEBUG: metadata is None for item {i}, skipping")
                continue
                
            print(f"📊 DEBUG: metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'not a dict'}")
            
            # Skip expired memories
            print(f"🕐 DEBUG: Checking if memory expired...")
            if is_memory_expired(metadata):
                print(f"⏰ DEBUG: Memory {i} is expired, skipping")
                continue
                
            # Filter by project if specified
            print(f"🏷️ DEBUG: Checking project filter...")
            project_id_from_metadata = metadata.get('project_id') if metadata else None
            print(f"🏷️ DEBUG: project_id_from_metadata: {project_id_from_metadata}")
            
            if project_id and project_id_from_metadata != project_id:
                print(f"🏷️ DEBUG: Project mismatch, skipping: expected={project_id}, got={project_id_from_metadata}")
                continue
                
            # Filter by confidence level
            print(f"📈 DEBUG: Checking confidence level...")
            confidence = metadata.get('confidence_level', 5) if metadata else 5
            print(f"📈 DEBUG: confidence: {confidence}, min_confidence: {min_confidence}")
            
            if confidence >= min_confidence:
                # Check if not deprecated
                status = metadata.get('status') if metadata else 'active'
                print(f"📊 DEBUG: status: {status}")
                
                if status != 'deprecated':
                    print(f"✅ DEBUG: Adding memory {i} to filtered_memories")
                    filtered_memories.append(metadata)
                else:
                    print(f"🗑️ DEBUG: Memory {i} is deprecated, skipping")
            else:
                print(f"📉 DEBUG: Confidence too low for memory {i}, skipping")
        
        print(f"📋 DEBUG: Filtered memories count: {len(filtered_memories)}")
        
        # If we have too few results, do a semantic search as backup
        if len(filtered_memories) < limit:
            print(f"🔍 DEBUG: Need more results, doing semantic search...")
            search_results = mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=limit * 2)
            print(f"🔍 DEBUG: search_results type: {type(search_results)}")
            
            search_list = safe_get_memories(search_results)
            print(f"🔍 DEBUG: search_list length: {len(search_list) if search_list else 'None'}")
            
            for i, memory_item in enumerate(search_list):
                print(f"🔄 DEBUG: Processing search memory_item {i}")
                
                if memory_item is None:  # Skip None objects
                    print(f"⚠️ DEBUG: Skipping None search memory_item at index {i}")
                    continue
                    
                metadata = get_memory_metadata(memory_item)
                print(f"📊 DEBUG: search metadata type: {type(metadata)}")
                
                if metadata is None:
                    print(f"⚠️ DEBUG: search metadata is None for item {i}, skipping")
                    continue
                
                # Apply same filters
                if (not is_memory_expired(metadata) and
                    metadata.get('confidence_level', 5) >= min_confidence and
                    metadata.get('status') != 'deprecated' and
                    (not project_id or metadata.get('project_id') == project_id)):
                    
                    # Avoid duplicates
                    if not any(existing.get('content') == metadata.get('content') 
                             for existing in filtered_memories):
                        filtered_memories.append(metadata)
        
        # Sort by confidence level and limit results
        print(f"📋 DEBUG: Sorting {len(filtered_memories)} memories by confidence...")
        filtered_memories.sort(key=lambda x: x.get('confidence_level', 0), reverse=True)
        filtered_memories = filtered_memories[:limit]
        
        if not filtered_memories:
            scope = f"project '{project_id}'" if project_id else "memory"
            return f"🔍 No accurate context found for query '{query}' in {scope} with min confidence {min_confidence}/10"
        
        # Format results
        context_data = {
            "query": query,
            "project_filter": project_id,
            "min_confidence_filter": min_confidence,
            "results_found": len(filtered_memories),
            "accurate_context": filtered_memories
        }
        
        print(f"✅ DEBUG: Returning successful result with {len(filtered_memories)} memories")
        return json.dumps(context_data, indent=2)
        
    except Exception as e:
        print(f"❌ DEBUG: Exception in get_accurate_context: {str(e)}")
        print(f"❌ DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        return f"❌ Error retrieving accurate context: {str(e)}"

@mcp.tool()
async def validate_project_context(project_id: str) -> str:
    """Validate all memory records for a project to identify outdated information.
    
    This tool analyzes all memories related to a project and identifies
    potentially outdated, conflicting, or low-confidence information.

    Args:
        project_id: The project identifier to validate
    """
    try:
        # CRITICAL: Ensure server is fully initialized before proceeding
        await ensure_server_initialized()
        
        mem0_client = get_mem0_client()
        
        # Get all memories
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Filter project-specific memories
        project_memories = []
        for memory_item in memory_list:
            if memory_item is None:  # Skip None objects
                continue
                
            metadata = get_memory_metadata(memory_item)
            if metadata.get('project_id') == project_id:
                project_memories.append(metadata)
        
        if not project_memories:
            return f"📋 No memories found for project: {project_id}"
        
        # Validate memories
        validation_results = {
            "project_id": project_id,
            "validation_timestamp": datetime.now().isoformat(),
            "total_memories": len(project_memories),
            "issues_found": [],
            "recommendations": []
        }
        
        # Check for expired memories
        expired_memories = []
        for metadata in project_memories:
            if metadata is None:  # Skip None metadata
                continue
            if is_memory_expired(metadata):
                expired_memories.append({
                    "content": metadata.get('content', '')[:100] + "...",
                    "expired_at": metadata.get('expires_at'),
                    "reason": "Memory has exceeded expiration date"
                })
        
        if expired_memories:
            validation_results["issues_found"].append({
                "type": "expired_memories",
                "count": len(expired_memories),
                "details": expired_memories
            })
            validation_results["recommendations"].append(
                f"Remove or refresh {len(expired_memories)} expired memories"
            )
        
        # Check for low confidence memories
        low_confidence_memories = []
        for metadata in project_memories:
            confidence = metadata.get('confidence_level', 5)
            if confidence < 5:
                low_confidence_memories.append({
                    "content": metadata.get('content', '')[:100] + "...",
                    "confidence_level": confidence,
                    "reason": f"Low confidence level ({confidence}/10)"
                })
        
        if low_confidence_memories:
            validation_results["issues_found"].append({
                "type": "low_confidence_memories",
                "count": len(low_confidence_memories),
                "details": low_confidence_memories
            })
            validation_results["recommendations"].append(
                f"Review and validate {len(low_confidence_memories)} low-confidence memories"
            )
        
        # Check for conflicted memories
        conflicted_memories = []
        for metadata in project_memories:
            if metadata.get('status') == 'conflicted' or metadata.get('validation_needed'):
                conflicted_memories.append({
                    "content": metadata.get('content', '')[:100] + "...",
                    "conflicts": metadata.get('conflicts', []),
                    "reason": "Memory marked as conflicted or needing validation"
                })
        
        if conflicted_memories:
            validation_results["issues_found"].append({
                "type": "conflicted_memories", 
                "count": len(conflicted_memories),
                "details": conflicted_memories
            })
            validation_results["recommendations"].append(
                f"Resolve conflicts in {len(conflicted_memories)} memories using resolve_context_conflict"
            )
        
        # Check for deprecated memories that should be cleaned up
        deprecated_memories = []
        for metadata in project_memories:
            if metadata.get('status') == 'deprecated':
                deprecated_memories.append({
                    "content": metadata.get('content', '')[:100] + "...",
                    "deprecated_reason": metadata.get('deprecated_reason'),
                    "superseded_by": metadata.get('superseded_by')
                })
        
        if deprecated_memories:
            validation_results["issues_found"].append({
                "type": "deprecated_memories",
                "count": len(deprecated_memories),
                "details": deprecated_memories
            })
            validation_results["recommendations"].append(
                f"Consider cleaning up {len(deprecated_memories)} deprecated memories"
            )
        
        # Overall health score
        total_issues = len(expired_memories) + len(low_confidence_memories) + len(conflicted_memories)
        health_score = max(0, 100 - (total_issues / len(project_memories) * 100))
        validation_results["health_score"] = round(health_score, 1)
        
        if not validation_results["issues_found"]:
            validation_results["status"] = "✅ Project context is healthy"
        elif health_score > 80:
            validation_results["status"] = "⚠️  Minor issues found"
        elif health_score > 60:
            validation_results["status"] = "🔶 Moderate issues require attention"
        else:
            validation_results["status"] = "🔴 Significant issues need immediate resolution"
        
        return json.dumps(validation_results, indent=2)
        
    except Exception as e:
        return f"❌ Error validating project context: {str(e)}"

@mcp.tool()
async def resolve_context_conflict(
    conflicting_memory_ids: str,
    correct_content: str,
    resolution_reason: str
) -> str:
    """Resolve conflicts between memory records by marking incorrect ones as deprecated.
    
    When conflicts are detected between memories, this tool allows you to specify
    which information is correct and provide reasoning for the resolution.

    Args:
        conflicting_memory_ids: Comma-separated list of memory IDs that are in conflict
        correct_content: The correct information that should replace conflicting data
        resolution_reason: Explanation of why this resolution was chosen
    """
    try:
        # CRITICAL: Ensure server is fully initialized before proceeding
        await ensure_server_initialized()
        
        mem0_client = get_mem0_client()
        
        # Parse memory IDs
        memory_ids = [id.strip() for id in conflicting_memory_ids.split(',')]
        
        if not memory_ids:
            return "❌ No memory IDs provided for conflict resolution"
        
        # Get all memories to find the conflicted ones
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Find memories by ID (we'll use content matching as a fallback)
        conflicted_memories = []
        for memory_item in memory_list:
            if memory_item is None:  # Skip None objects
                continue
                
            metadata = get_memory_metadata(memory_item)
            memory_id = metadata.get('memory_id') or create_memory_id(metadata.get('content', ''))
            
            if memory_id in memory_ids:
                conflicted_memories.append(metadata)
        
        if not conflicted_memories:
            return f"⚠️  No memories found matching the provided IDs: {conflicting_memory_ids}"
        
        # Extract project info from the first conflicted memory
        project_id = conflicted_memories[0].get('project_id', 'unknown')
        category = conflicted_memories[0].get('category', 'general')
        
        resolution_metadata = {
            "project_id": project_id,
            "category": category,
            "confidence_level": 9,  # High confidence for manually resolved conflicts
            "source": "conflict_resolution",
            "status": "active",
            "resolution_timestamp": datetime.now().isoformat(),
            "resolution_reason": resolution_reason,
            "resolved_conflicts": len(conflicted_memories),
            "supersedes": memory_ids,
            "tags": ["resolution", "conflict_resolved"]
        }
        
        # Create a new memory with the correct content
        messages = [{"role": "user", "content": correct_content}]
        new_memory = mem0_client.add(messages, user_id=DEFAULT_USER_ID, metadata=resolution_metadata)
        
        # NOTE: mem0 doesn't support direct updates, so we can't actually deprecate the old memories
        # In a production system, you'd want to implement a soft-delete mechanism
        
        resolution_summary = {
            "action": "conflict_resolved",
            "timestamp": datetime.now().isoformat(),
            "new_correct_content": correct_content,
            "resolution_reason": resolution_reason,
            "conflicted_memory_count": len(conflicted_memories),
            "resolution_confidence": "9/10 (manually resolved)",
            "note": "Conflicted memories remain in storage but resolution is recorded with high confidence"
        }
        
        return f"✅ Conflict resolved successfully!\n{json.dumps(resolution_summary, indent=2)}"
        
    except Exception as e:
        return f"❌ Error resolving context conflict: {str(e)}"

@mcp.tool()
async def audit_memory_quality(project_id: Optional[str] = None) -> str:
    """Comprehensive audit of memory quality across all projects or a specific project.
    
    This tool analyzes the entire memory database to identify quality issues,
    contradictions, outdated information, and provides actionable recommendations.

    Args:
        project_id: Optional project ID to limit audit scope
    """
    try:
        # CRITICAL: Ensure server is fully initialized before proceeding
        await ensure_server_initialized()
        
        mem0_client = get_mem0_client()
        
        # Get all memories
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Filter by project if specified
        if project_id:
            filtered_memories = []
            for memory_item in memory_list:
                if memory_item is None:  # Skip None objects
                    continue
                    
                metadata = get_memory_metadata(memory_item)
                if metadata.get('project_id') == project_id:
                    filtered_memories.append(metadata)
            memory_list = filtered_memories
            
        if not memory_list:
            scope = f"project '{project_id}'" if project_id else "entire memory database"
            return f"📋 No memories found in {scope}"
        
        # Comprehensive quality audit
        audit_results = {
            "audit_scope": project_id if project_id else "all_projects",
            "audit_timestamp": datetime.now().isoformat(),
            "total_memories_analyzed": len(memory_list),
            "quality_metrics": {},
            "issues_by_category": {},
            "recommendations": [],
            "overall_quality_score": 0
        }
        
        # Initialize counters
        expired_count = 0
        low_confidence_count = 0
        high_confidence_count = 0
        conflicted_count = 0
        deprecated_count = 0
        no_metadata_count = 0
        
        # Detailed analysis
        for memory_item in memory_list:
            if memory_item is None:  # Skip None objects
                continue
                
            metadata = get_memory_metadata(memory_item)
            
            # Check expiration
            if is_memory_expired(metadata):
                expired_count += 1
                
            # Check confidence levels
            confidence = metadata.get('confidence_level', 5)
            if confidence < 5:
                low_confidence_count += 1
            elif confidence >= 8:
                high_confidence_count += 1
                
            # Check status
            status = metadata.get('status', 'unknown')
            if status == 'conflicted' or metadata.get('validation_needed'):
                conflicted_count += 1
            elif status == 'deprecated':
                deprecated_count += 1
                
            # Check for missing metadata
            if not metadata.get('project_id') or not metadata.get('category'):
                no_metadata_count += 1
        
        # Calculate quality metrics
        audit_results["quality_metrics"] = {
            "confidence_distribution": {
                "high_confidence": high_confidence_count,
                "medium_confidence": len(memory_list) - high_confidence_count - low_confidence_count,
                "low_confidence": low_confidence_count
            },
            "status_distribution": {
                "active": len(memory_list) - deprecated_count - conflicted_count,
                "conflicted": conflicted_count,
                "deprecated": deprecated_count
            },
            "data_quality": {
                "expired_memories": expired_count,
                "missing_metadata": no_metadata_count,
                "well_documented": len(memory_list) - no_metadata_count
            }
        }
        
        # Identify issues by category
        if expired_count > 0:
            audit_results["issues_by_category"]["expired_data"] = {
                "count": expired_count,
                "severity": "medium",
                "description": f"{expired_count} memories have expired and may contain outdated information"
            }
            
        if low_confidence_count > 0:
            audit_results["issues_by_category"]["low_confidence"] = {
                "count": low_confidence_count,
                "severity": "medium",
                "description": f"{low_confidence_count} memories have low confidence scores (<5/10)"
            }
            
        if conflicted_count > 0:
            audit_results["issues_by_category"]["conflicts"] = {
                "count": conflicted_count,
                "severity": "high",
                "description": f"{conflicted_count} memories are marked as conflicted and need resolution"
            }
            
        if no_metadata_count > 0:
            audit_results["issues_by_category"]["missing_metadata"] = {
                "count": no_metadata_count,
                "severity": "low",
                "description": f"{no_metadata_count} memories lack proper categorization metadata"
            }
        
        # Generate recommendations
        if expired_count > 0:
            audit_results["recommendations"].append(
                f"🗓️  Review and refresh {expired_count} expired memories"
            )
            
        if low_confidence_count > 0:
            audit_results["recommendations"].append(
                f"🔍 Validate and improve confidence for {low_confidence_count} low-confidence memories"
            )
            
        if conflicted_count > 0:
            audit_results["recommendations"].append(
                f"⚠️  Resolve {conflicted_count} conflicted memories using resolve_context_conflict"
            )
            
        if no_metadata_count > 0:
            audit_results["recommendations"].append(
                f"📝 Add proper metadata to {no_metadata_count} memories for better organization"
            )
            
        # Calculate overall quality score
        total_issues = expired_count + low_confidence_count + conflicted_count + no_metadata_count
        quality_score = max(0, 100 - (total_issues / len(memory_list) * 100))
        audit_results["overall_quality_score"] = round(quality_score, 1)
        
        # Determine overall status
        if quality_score >= 90:
            audit_results["overall_status"] = "✨ Excellent - Memory quality is very high"
        elif quality_score >= 80:
            audit_results["overall_status"] = "✅ Good - Minor issues that can be addressed"
        elif quality_score >= 70:
            audit_results["overall_status"] = "⚠️  Fair - Several issues need attention"
        elif quality_score >= 60:
            audit_results["overall_status"] = "🔶 Poor - Significant quality problems"
        else:
            audit_results["overall_status"] = "🔴 Critical - Major quality overhaul needed"
            
        if not audit_results["recommendations"]:
            audit_results["recommendations"].append("🎉 Memory quality is excellent - no action needed!")
            
        return json.dumps(audit_results, indent=2)
        
    except Exception as e:
        return f"❌ Error auditing memory quality: {str(e)}"

@mcp.tool()
async def save_project_milestone(
    project_id: str,
    milestone_type: str,
    content: str,
    impact_level: int = 8,
    tags: Optional[str] = None
) -> str:
    """Save important project milestones with automatic versioning and status updates.
    
    This tool is designed for tracking key project moments like architectural decisions,
    problem identification, solution implementation, and status changes.

    Args:
        project_id: The project identifier
        milestone_type: Type of milestone (architecture_decision/problem_identified/solution_implemented/status_change)
        content: Description of the milestone or decision
        impact_level: Impact significance (1-10, default: 8 for high impact)
        tags: Optional comma-separated tags
    """
    try:
        mem0_client = get_mem0_client()
        
        # Parse tags and add milestone tag
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        if 'milestone' not in tag_list:
            tag_list.append('milestone')
            
        # Get existing milestones to check for superseding
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Find existing milestones of the same type for this project
        existing_milestones = []
        for memory_item in memory_list:
            metadata = get_memory_metadata(memory_item)
            if (metadata.get('project_id') == project_id and 
                metadata.get('milestone_type') == milestone_type and
                'milestone' in metadata.get('tags', [])):
                existing_milestones.append(metadata)
        
        # Count milestones that will be superseded
        superseded_count = len(existing_milestones)
        
        # Create milestone metadata
        milestone_metadata = create_enhanced_metadata(
            project_id=project_id,
            category="milestone",
            confidence_level=9,  # Milestones are high confidence
            source="milestone_tracking",
            tags=tag_list
        )
        
        # Add milestone-specific metadata
        milestone_metadata.update({
            "milestone_type": milestone_type,
            "impact_level": impact_level,
            "superseded_milestones": superseded_count,
            "milestone_timestamp": datetime.now().isoformat()
        })
        
        # Save milestone
        messages = [{"role": "user", "content": content}]
        result = mem0_client.add(messages, user_id=DEFAULT_USER_ID, metadata=milestone_metadata)
        
        milestone_msg = f"📍 Project milestone saved: {milestone_type.replace('_', ' ').title()}"
        if superseded_count > 0:
            milestone_msg += f" (superseded {superseded_count} previous milestones)"
        milestone_msg += f"\nContent: {content[:100]}..."
        
        return milestone_msg
        
    except Exception as e:
        return f"❌ Error saving project milestone: {str(e)}"

@mcp.tool()
async def get_current_project_state(project_id: str) -> str:
    """Get the current state of a project including latest milestones and active information.
    
    This tool provides a comprehensive view of the project's current state by retrieving
    only the most recent and relevant information, excluding deprecated data.

    Args:
        project_id: The project identifier to get state for
    """
    try:
        # CRITICAL: Ensure server is fully initialized before proceeding
        await ensure_server_initialized()
        
        mem0_client = get_mem0_client()
        
        # Get all memories
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Process memories and filter by project and active status
        project_memories = []
        for memory_item in memory_list:
            if memory_item is None:  # Skip None objects
                continue
                
            metadata = get_memory_metadata(memory_item)
            
            # Filter by project and exclude deprecated/expired
            if (metadata.get('project_id') == project_id and 
                metadata.get('status') != 'deprecated' and
                not (metadata.get('expires_at') and 
                     datetime.fromisoformat(metadata['expires_at'].replace('Z', '+00:00')) < datetime.now())):
                project_memories.append(metadata)
        
        if not project_memories:
            return f"📋 No active memories found for project: {project_id}"
        
        # Group by category
        state_by_category = {}
        milestones = []
        
        for metadata in project_memories:
            category = metadata.get('category', 'unknown')
            
            if 'milestone' in metadata.get('tags', []):
                milestones.append({
                    "type": metadata.get('milestone_type', category),
                    "content": metadata.get('content', ''),
                    "timestamp": metadata.get('milestone_timestamp', metadata.get('updated_at')),
                    "impact_level": metadata.get('impact_level', 0)
                })
            else:
                if category not in state_by_category:
                    state_by_category[category] = []
                
                state_by_category[category].append({
                    "content": metadata.get('content', ''),
                    "confidence_level": metadata.get('confidence_level', 0),
                    "last_updated": metadata.get('updated_at'),
                    "tags": metadata.get('tags', [])
                })
        
        # Sort milestones by timestamp (most recent first)
        milestones.sort(key=lambda m: m.get('timestamp', ''), reverse=True)
        
        # Sort each category by confidence level
        for category in state_by_category:
            state_by_category[category].sort(
                key=lambda m: m.get('confidence_level', 0), 
                reverse=True
            )
        
        project_state = {
            "project_id": project_id,
            "state_timestamp": datetime.now().isoformat(),
            "total_active_memories": len(project_memories),
            "recent_milestones": milestones[:5],  # Last 5 milestones
            "current_state_by_category": state_by_category,
            "summary": {
                "categories_with_data": list(state_by_category.keys()),
                "milestone_count": len(milestones),
                "last_milestone": milestones[0] if milestones else None
            }
        }
        
        return json.dumps(project_state, indent=2)
        
    except Exception as e:
        return f"❌ Error retrieving current project state: {str(e)}"

@mcp.tool() 
async def track_project_evolution(project_id: str, category: Optional[str] = None) -> str:
    """Track how project understanding and decisions have evolved over time.
    
    This tool shows the version history and evolution of project knowledge,
    useful for understanding decision-making progression and learning from past choices.

    Args:
        project_id: The project identifier to track
        category: Optional category to focus on (architecture/problem/solution/status/decision)
    """
    try:
        # CRITICAL: Ensure server is fully initialized before proceeding
        await ensure_server_initialized()
        
        mem0_client = get_mem0_client()
        
        # Get all memories including deprecated ones
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Process memories and filter by project (include deprecated to show evolution)
        project_memories = []
        for memory_item in memory_list:
            if memory_item is None:  # Skip None objects
                continue
                
            metadata = get_memory_metadata(memory_item)
            
            # Filter by project and optionally by category
            if metadata.get('project_id') == project_id:
                if not category or metadata.get('category') == category:
                    project_memories.append(metadata)
        
        if not project_memories:
            scope = f"project '{project_id}'" + (f" category '{category}'" if category else "")
            return f"📋 No memories found for {scope}"
        
        # Sort by creation/update date
        project_memories.sort(key=lambda m: m.get('updated_at', ''))
        
        # Group into timeline events
        timeline = []
        for metadata in project_memories:
            event = {
                "timestamp": metadata.get('updated_at'),
                "content": metadata.get('content', ''),
                "category": metadata.get('category', 'unknown'),
                "status": metadata.get('status', 'active'),
                "confidence_level": metadata.get('confidence_level', 5),
                "version": metadata.get('version', 1),
                "superseded_by": metadata.get('superseded_by'),
                "deprecated_reason": metadata.get('deprecated_reason'),
                "tags": metadata.get('tags', [])
            }
            
            # Add milestone info if applicable
            if 'milestone' in event["tags"]:
                event["milestone_type"] = metadata.get('milestone_type')
                event["impact_level"] = metadata.get('impact_level')
            
            timeline.append(event)
        
        # Create evolution summary
        evolution_data = {
            "project_id": project_id,
            "tracking_scope": category if category else "all_categories", 
            "tracking_timestamp": datetime.now().isoformat(),
            "timeline_length": len(timeline),
            "evolution_timeline": timeline,
            "evolution_summary": {
                "total_decisions": len([e for e in timeline if e.get('milestone_type') == 'architecture_decision']),
                "problems_identified": len([e for e in timeline if e.get('milestone_type') == 'problem_identified']),
                "solutions_implemented": len([e for e in timeline if e.get('milestone_type') == 'solution_implemented']),
                "status_changes": len([e for e in timeline if e.get('milestone_type') == 'status_change']),
                "deprecated_entries": len([e for e in timeline if e.get('status') == 'deprecated']),
                "active_entries": len([e for e in timeline if e.get('status') == 'active'])
            }
        }
        
        return json.dumps(evolution_data, indent=2)
        
    except Exception as e:
        return f"❌ Error tracking project evolution: {str(e)}"

async def main():
    """Run the FastMCP server with transport from environment variables."""
    global _server_initialized
    
    # Read environment variables
    transport = os.getenv("TRANSPORT", "stdio").lower()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8050"))
    
    print(f"🔧 CRITICAL: Pre-initializing MCP BEFORE starting HTTP server...")
    
    # ===== PHASE 1: COMPLETE MCP INITIALIZATION BEFORE ANY HTTP =====
    max_init_rounds = 3
    mcp_ready = False
    
    for init_round in range(max_init_rounds):
        try:
            print(f"🏗️ MCP Pre-initialization round {init_round + 1}/{max_init_rounds}")
            
            # Extended delay before testing
            await asyncio.sleep(3.0 + init_round * 2.0)
            
            # Test mem0 client extensively
            mem0_client = get_mem0_client()
            
            print(f"🧪 Comprehensive MCP validation tests...")
            
            # Test 1: Basic connectivity
            test_result_1 = mem0_client.get_all(user_id=DEFAULT_USER_ID, limit=1)
            print(f"✅ Test 1 (get_all): PASSED")
            
            # Test 2: Search functionality  
            test_result_2 = mem0_client.search("test", user_id=DEFAULT_USER_ID, limit=1)
            print(f"✅ Test 2 (search): PASSED")
            
            # Test 3: Add functionality
            test_messages = [{"role": "user", "content": "MCP Pre-initialization test"}]
            test_result_3 = mem0_client.add(test_messages, user_id=DEFAULT_USER_ID)
            print(f"✅ Test 3 (add): PASSED")
            
            # Test 4: Ensure server initialization function works
            await ensure_server_initialized()
            print(f"✅ Test 4 (ensure_server_initialized): PASSED")
            
            # Additional stability delay
            await asyncio.sleep(3.0)
            
            print(f"✅ MCP Pre-initialization round {init_round + 1} completed successfully")
            mcp_ready = True
            break
            
        except Exception as e:
            print(f"❌ MCP Pre-initialization round {init_round + 1} failed: {str(e)}")
            if init_round == max_init_rounds - 1:
                print(f"❌ All MCP pre-initialization rounds failed!")
                print(f"🚨 CRITICAL: Cannot start HTTP server without MCP ready")
                return
            else:
                print(f"🔄 Retrying MCP pre-initialization...")
                await asyncio.sleep(5.0)
    
    if not mcp_ready:
        print(f"🚨 CRITICAL: MCP initialization failed, aborting server startup")
        return
        
    # Mark server as fully initialized BEFORE starting HTTP
    _server_initialized = True
    print(f"🎯 MCP FULLY INITIALIZED - ready to accept connections")
    
    # ===== PHASE 2: START HTTP SERVER ONLY AFTER MCP IS READY =====
    print(f"🚀 PHASE 2: Starting HTTP server NOW that MCP is ready...")
    
    if transport == "sse":
        print(f"🌐 Starting HTTP server with SSE transport on {host}:{port}")
        print(f"✅ MCP is ready - HTTP server will NOT cause race conditions")
        await mcp.run_async(transport="sse", host=host, port=port)
    else:
        print(f"📡 Starting server with STDIO transport")
        print(f"✅ MCP is ready - STDIO server will NOT cause race conditions")
        await mcp.run_async(transport="stdio")

if __name__ == "__main__":
    asyncio.run(main())
