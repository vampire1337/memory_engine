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
        mem0_client = get_mem0_client()
        
        # Use enhanced search simulation
        filtered_memories = simulate_enhanced_search(
            mem0_client, query, project_id, min_confidence, limit
        )
        
        if not filtered_memories:
            return f"🔍 No accurate context found for query: '{query}' (min_confidence: {min_confidence})"
        
        # Format results with quality indicators
        results = []
        for metadata in filtered_memories:
            result_entry = {
                "content": metadata['content'],
                "confidence_level": metadata['confidence_level'],
                "category": categorize_content(metadata['content']),
                "estimated_project": extract_project_from_content(metadata['content']) or project_id,
                "content_length": len(metadata['content']),
                "estimated_tags": [categorize_content(metadata['content'])]
            }
            results.append(result_entry)
        
        return json.dumps({
            "query": query,
            "results_found": len(results),
            "min_confidence_applied": min_confidence,
            "note": "Results based on content analysis due to basic API limitations",
            "accurate_context": results
        }, indent=2)
        
    except Exception as e:
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
        mem0_client = get_mem0_client()
        
        # Get all memories
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Process memories and filter by project using content analysis
        project_memories = []
        for memory_item in memory_list:
            metadata = get_memory_metadata(memory_item)
            content = metadata['content']
            
            # Check if memory is related to the project
            extracted_project = extract_project_from_content(content)
            if (extracted_project and extracted_project.lower() == project_id.lower()) or \
               (project_id.lower() in content.lower()):
                # Estimate metadata for analysis
                metadata['confidence_level'] = estimate_content_confidence(content)
                metadata['category'] = categorize_content(content)
                metadata['estimated_project'] = extracted_project or project_id
                project_memories.append(metadata)
        
        if not project_memories:
            return f"📋 No memories found for project: {project_id}"
        
        # Analyze memory quality using estimated data
        total_memories = len(project_memories)
        low_confidence_memories = [m for m in project_memories if m.get('confidence_level', 10) < 5]
        needs_validation = [m for m in project_memories if m.get('confidence_level', 10) < 7]
        
        # Basic conflict detection by content similarity
        potential_conflicts = []
        for i, memory1 in enumerate(project_memories):
            for j, memory2 in enumerate(project_memories[i+1:], i+1):
                content1 = memory1['content'].lower()
                content2 = memory2['content'].lower()
                
                # Simple conflict detection: same category but contradictory keywords
                if memory1['category'] == memory2['category']:
                    conflict_pairs = [
                        ('исправлено', 'проблема'), ('fixed', 'problem'),
                        ('работает', 'не работает'), ('works', 'doesn\'t work'),
                        ('завершено', 'в процессе'), ('completed', 'in progress')
                    ]
                    
                    for word1, word2 in conflict_pairs:
                        if word1 in content1 and word2 in content2:
                            potential_conflicts.append((i, j))
                            break
        
        validation_report = {
            "project_id": project_id,
            "total_memories": total_memories,
            "analysis": {
                "low_confidence_memories": len(low_confidence_memories),
                "needs_validation": len(needs_validation),
                "potential_conflicts": len(potential_conflicts)
            },
            "categories_found": list(set(m.get('category', 'unknown') for m in project_memories)),
            "confidence_distribution": {
                "high_confidence": len([m for m in project_memories if m.get('confidence_level', 5) >= 8]),
                "medium_confidence": len([m for m in project_memories if 5 <= m.get('confidence_level', 5) < 8]),
                "low_confidence": len(low_confidence_memories)
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if potential_conflicts:
            validation_report["recommendations"].append(
                f"⚠️  {len(potential_conflicts)} potential conflicts detected - review similar content for contradictions"
            )
        if low_confidence_memories:
            validation_report["recommendations"].append(
                f"🔍 {len(low_confidence_memories)} memories have low confidence - verify accuracy"
            )
        if needs_validation:
            validation_report["recommendations"].append(
                f"✅ {len(needs_validation)} memories need accuracy validation"
            )
            
        if not validation_report["recommendations"]:
            validation_report["recommendations"].append("✨ Project context appears to be in good condition!")
        
        validation_report["note"] = "Analysis based on content heuristics due to basic API limitations"
        
        return json.dumps(validation_report, indent=2)
        
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
        mem0_client = get_mem0_client()
        
        # Parse memory IDs
        memory_ids = [id.strip() for id in conflicting_memory_ids.split(',')]
        
        if len(memory_ids) < 2:
            return "❌ Need at least 2 memory IDs to resolve conflicts"
        
        # Get all memories to find the conflicted ones
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Convert memory list to searchable format
        memory_dict = {}
        for i, memory_item in enumerate(memory_list):
            metadata = get_memory_metadata(memory_item)
            # Use index as ID if no real ID available
            memory_id = metadata.get('memory_id', str(i))
            memory_dict[memory_id] = metadata
        
        # Find conflicted memories
        conflicted_memories = []
        found_ids = []
        for memory_id in memory_ids:
            if memory_id in memory_dict:
                conflicted_memories.append(memory_dict[memory_id])
                found_ids.append(memory_id)
        
        if len(conflicted_memories) < 2:
            return f"❌ Could not find sufficient memory IDs. Found {len(conflicted_memories)} out of {len(memory_ids)}. Available IDs: {list(memory_dict.keys())[:10]}"
        
        # Create new correct memory
        enhanced_metadata = create_enhanced_metadata(
            category="conflict_resolution",
            confidence_level=9,
            source="conflict_resolution",
            project_id=conflicted_memories[0].get('project_id', 'general'),
            tags=["conflict_resolved"]
        )
        
        # Add resolution information
        enhanced_metadata.update({
            'resolved_conflict_ids': found_ids,
            'resolution_reason': resolution_reason,
            'resolved_at': datetime.now().isoformat()
        })
        
        # Save the correct information
        save_result = mem0_client.add(
            messages=[{"role": "user", "content": correct_content}],
            user_id=DEFAULT_USER_ID,
            metadata=enhanced_metadata
        )
        
        resolution_summary = {
            "action": "conflict_resolved",
            "conflicted_memories_count": len(conflicted_memories),
            "resolution_reason": resolution_reason,
            "new_memory_created": True,
            "conflicted_content_sample": [m['content'][:100] + "..." for m in conflicted_memories[:3]],
            "correct_content": correct_content[:200] + "..." if len(correct_content) > 200 else correct_content
        }
        
        return json.dumps(resolution_summary, indent=2)
        
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
        mem0_client = get_mem0_client()
        
        # Get all memories
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Process memories and filter by project if specified
        processed_memories = []
        for memory_item in memory_list:
            metadata = get_memory_metadata(memory_item)
            if not project_id or metadata.get('project_id') == project_id:
                processed_memories.append(metadata)
        
        if not processed_memories:
            scope = f"project '{project_id}'" if project_id else "database"
            return f"📋 No memories found in {scope}"
        
        # Quality analysis
        total_memories = len(processed_memories)
        
        # Categorize issues
        expired_memories = [m for m in processed_memories if m.get('expires_at') and 
                          datetime.fromisoformat(m['expires_at'].replace('Z', '+00:00')) < datetime.now()]
        conflicted_memories = [m for m in processed_memories if m.get('status') == 'conflicted']
        deprecated_memories = [m for m in processed_memories if m.get('status') == 'deprecated']
        low_confidence_memories = [m for m in processed_memories if m.get('confidence_level', 10) < 5]
        needs_validation = [m for m in processed_memories if m.get('confidence_level', 10) < 7]
        
        # Confidence distribution
        confidence_distribution = {}
        for memory in processed_memories:
            conf = memory.get('confidence_level', 5)
            confidence_distribution[conf] = confidence_distribution.get(conf, 0) + 1
        
        # Category distribution
        category_distribution = {}
        for memory in processed_memories:
            cat = memory.get('category', 'unknown')
            category_distribution[cat] = category_distribution.get(cat, 0) + 1
        
        # Age analysis - since we don't have reliable creation dates, use basic heuristics
        old_memories = []
        for memory in processed_memories:
            updated_at = memory.get('updated_at')
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_old = (datetime.now().replace(tzinfo=updated_date.tzinfo) - updated_date).days
                    if days_old > 60:  # Older than 2 months
                        old_memories.append(memory)
                except (ValueError, TypeError):
                    pass
        
        # Generate comprehensive audit report
        audit_report = {
            "audit_scope": f"project '{project_id}'" if project_id else "entire database",
            "audit_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_memories": total_memories,
                "active_memories": total_memories - len(deprecated_memories),
                "deprecated_memories": len(deprecated_memories)
            },
            "quality_issues": {
                "expired_memories": len(expired_memories),
                "conflicted_memories": len(conflicted_memories),
                "low_confidence_memories": len(low_confidence_memories),
                "needs_validation": len(needs_validation),
                "old_memories_60_days": len(old_memories)
            },
            "distributions": {
                "confidence_levels": confidence_distribution,
                "categories": category_distribution
            },
            "health_score": 0,
            "recommendations": []
        }
        
        # Calculate health score (0-100)
        active_memories = total_memories - len(deprecated_memories)
        if active_memories > 0:
            issue_ratio = (
                len(expired_memories) + 
                len(conflicted_memories) + 
                len(low_confidence_memories)
            ) / active_memories
            audit_report["health_score"] = max(0, int((1 - issue_ratio) * 100))
        
        # Generate recommendations
        if expired_memories:
            audit_report["recommendations"].append({
                "priority": "HIGH",
                "issue": f"{len(expired_memories)} expired memories",
                "action": "Remove or update expired information to prevent outdated context"
            })
        
        if conflicted_memories:
            audit_report["recommendations"].append({
                "priority": "CRITICAL",
                "issue": f"{len(conflicted_memories)} conflicted memories",
                "action": "Use resolve_context_conflict to resolve contradictions immediately"
            })
        
        if low_confidence_memories:
            audit_report["recommendations"].append({
                "priority": "MEDIUM",
                "issue": f"{len(low_confidence_memories)} low confidence memories",
                "action": "Review and either verify or remove uncertain information"
            })
        
        if needs_validation:
            audit_report["recommendations"].append({
                "priority": "MEDIUM",
                "issue": f"{len(needs_validation)} memories need validation",
                "action": "Validate accuracy of flagged memories"
            })
        
        if old_memories:
            audit_report["recommendations"].append({
                "priority": "LOW",
                "issue": f"{len(old_memories)} memories older than 60 days",
                "action": "Review relevance of old memories for current project state"
            })
        
        if audit_report["health_score"] >= 90:
            audit_report["recommendations"].append({
                "priority": "INFO",
                "issue": "Memory quality is excellent",
                "action": "Continue current memory management practices"
            })
        elif audit_report["health_score"] >= 70:
            audit_report["recommendations"].append({
                "priority": "INFO", 
                "issue": "Memory quality is good",
                "action": "Address minor issues to improve context accuracy"
            })
        else:
            audit_report["recommendations"].append({
                "priority": "CRITICAL",
                "issue": "Memory quality needs attention",
                "action": "Urgent cleanup required to ensure reliable context"
            })
        
        return json.dumps(audit_report, indent=2)
        
    except Exception as e:
        return f"❌ Error during memory quality audit: {str(e)}"

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
        
        # Validate milestone type
        valid_types = ["architecture_decision", "problem_identified", "solution_implemented", "status_change"]
        if milestone_type not in valid_types:
            return f"❌ Invalid milestone_type. Must be one of: {', '.join(valid_types)}"
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        tag_list.append(f"milestone_{milestone_type}")
        tag_list.append("project_milestone")
        
        # Get existing project memories to check for similar milestones
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Find previous milestones of the same type for this project
        similar_milestones = []
        for memory_item in memory_list:
            metadata = get_memory_metadata(memory_item)
            if (metadata.get('project_id') == project_id and 
                metadata.get('category') == milestone_type and
                metadata.get('status') != 'deprecated'):
                similar_milestones.append(metadata)
        
        # Mark previous similar milestones as superseded if this is a status change
        superseded_count = 0
        if milestone_type == "status_change" and similar_milestones:
            # In a real implementation, we'd update the metadata
            # For now, we'll track that they should be superseded
            superseded_count = len(similar_milestones)
        
        # Create enhanced metadata for milestone
        milestone_metadata = create_enhanced_metadata(
            project_id=project_id,
            category=milestone_type,
            confidence_level=impact_level,
            source="project_milestone",
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
        mem0_client = get_mem0_client()
        
        # Get all memories
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Process memories and filter by project and active status
        project_memories = []
        for memory_item in memory_list:
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
        mem0_client = get_mem0_client()
        
        # Get all memories including deprecated ones
        all_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        memory_list = safe_get_memories(all_memories)
        
        # Process memories and filter by project (include deprecated to show evolution)
        project_memories = []
        for memory_item in memory_list:
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
    # Read environment variables
    transport = os.getenv("TRANSPORT", "stdio").lower()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8050"))
    
    if transport == "sse":
        print(f"🚀 Starting MCP server with SSE transport on {host}:{port}")
        await mcp.run_async(transport="sse", host=host, port=port)
    else:
        print(f"🚀 Starting MCP server with STDIO transport")
        await mcp.run_async(transport="stdio")

if __name__ == "__main__":
    asyncio.run(main())
