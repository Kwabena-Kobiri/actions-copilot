"""
Sprint management tools for the Sprint Coordinator application.
Provides CRUD operations for sprint items and sprint data.
"""

import json
import logging
from typing import Dict, List, Optional
from google.adk.tools import tool
from app.config import SPRINTS_FILE

# Set up logging
logger = logging.getLogger(__name__)


def _load_sprints_data() -> Dict:
    """Load sprint data from JSON file with error handling."""
    try:
        with open(SPRINTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Sprints file not found: {SPRINTS_FILE}")
        return {"sprints": [], "sprint_analysis": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in sprints file: {e}")
        return {"sprints": [], "sprint_analysis": {}}
    except Exception as e:
        logger.error(f"Error loading sprints data: {e}")
        return {"sprints": [], "sprint_analysis": {}}


def _save_sprints_data(data: Dict) -> bool:
    """Save sprint data to JSON file with atomic write."""
    try:
        # Write to temporary file first, then rename (atomic operation)
        temp_file = SPRINTS_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(SPRINTS_FILE)
        return True
    except Exception as e:
        logger.error(f"Error saving sprints data: {e}")
        return False


@tool
def get_sprint_items() -> str:
    """
    Retrieve all available sprint items from sprints.json.
    
    Returns:
        str: JSON string containing all sprint items and analysis data.
    """
    try:
        data = _load_sprints_data()
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_sprint_items: {e}")
        return json.dumps({"error": f"Failed to load sprint items: {str(e)}"})


@tool
def get_sprint_item(item_id: str) -> str:
    """
    Get specific sprint item details by ID.
    
    Args:
        item_id (str): The ID of the sprint item to retrieve (e.g., 's1_item_1').
        
    Returns:
        str: JSON string containing the sprint item details, or error message.
    """
    try:
        data = _load_sprints_data()
        
        # Search through all sprints for the item
        for sprint in data.get("sprints", []):
            for item in sprint.get("items", []):
                if item.get("item_id") == item_id:
                    return json.dumps(item, indent=2)
        
        return json.dumps({"error": f"Sprint item '{item_id}' not found"})
    except Exception as e:
        logger.error(f"Error in get_sprint_item: {e}")
        return json.dumps({"error": f"Failed to get sprint item: {str(e)}"})


@tool
def update_sprint_item_status(item_id: str, status: str, notes: str = "") -> str:
    """
    Update sprint item status and add optional notes.
    
    Args:
        item_id (str): The ID of the sprint item to update.
        status (str): New status ('pending', 'in_progress', 'completed').
        notes (str, optional): Additional notes about the status change.
        
    Returns:
        str: Success message or error details.
    """
    try:
        data = _load_sprints_data()
        
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            return json.dumps({
                "error": f"Invalid status '{status}'. Must be one of: {valid_statuses}"
            })
        
        # Find and update the item
        updated = False
        for sprint in data.get("sprints", []):
            for item in sprint.get("items", []):
                if item.get("item_id") == item_id:
                    item["status"] = status
                    if notes:
                        item["notes"] = notes
                    updated = True
                    break
            if updated:
                break
        
        if not updated:
            return json.dumps({"error": f"Sprint item '{item_id}' not found"})
        
        # Save the updated data
        if _save_sprints_data(data):
            return json.dumps({
                "success": True,
                "message": f"Sprint item '{item_id}' status updated to '{status}'",
                "item_id": item_id,
                "status": status,
                "notes": notes
            })
        else:
            return json.dumps({"error": "Failed to save updated sprint data"})
            
    except Exception as e:
        logger.error(f"Error in update_sprint_item_status: {e}")
        return json.dumps({"error": f"Failed to update sprint item status: {str(e)}"})


@tool
def get_user_sprint_items(user_id: str) -> str:
    """
    Get sprint items assigned to a specific user.
    
    Args:
        user_id (str): The user ID to filter sprint items by.
        
    Returns:
        str: JSON string containing sprint items assigned to the user.
    """
    try:
        data = _load_sprints_data()
        user_items = []
        
        # Filter items by assignee
        for sprint in data.get("sprints", []):
            sprint_info = {
                "sprint_id": sprint.get("sprint_id"),
                "title": sprint.get("title"),
                "goal": sprint.get("goal"),
                "items": []
            }
            
            for item in sprint.get("items", []):
                if item.get("assignee") == user_id:
                    sprint_info["items"].append(item)
            
            if sprint_info["items"]:  # Only include sprints with user items
                user_items.append(sprint_info)
        
        return json.dumps({
            "user_id": user_id,
            "sprints": user_items,
            "total_items": sum(len(sprint["items"]) for sprint in user_items)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_user_sprint_items: {e}")
        return json.dumps({"error": f"Failed to get user sprint items: {str(e)}"})
