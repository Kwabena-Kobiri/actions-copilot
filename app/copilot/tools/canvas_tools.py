"""
Canvas management tools for the Sprint Coordinator application.
Provides CRUD operations for Business Model Canvas, Value Proposition Canvas, and Customer Segments.
"""

import json
import logging
from typing import Dict, Any, Optional
from google.adk.tools import tool
from app.config import BMC_FILE, VPC_FILE, SEGMENTS_FILE

# Set up logging
logger = logging.getLogger(__name__)


def _load_json_file(file_path) -> Dict:
    """Load JSON data from file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return {}


def _save_json_file(file_path, data: Dict) -> bool:
    """Save JSON data to file with atomic write."""
    try:
        # Write to temporary file first, then rename (atomic operation)
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(file_path)
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {e}")
        return False


# Business Model Canvas Tools

@tool
def get_business_model_canvas() -> str:
    """
    Retrieve current Business Model Canvas data.
    
    Returns:
        str: JSON string containing the complete Business Model Canvas.
    """
    try:
        data = _load_json_file(BMC_FILE)
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_business_model_canvas: {e}")
        return json.dumps({"error": f"Failed to load Business Model Canvas: {str(e)}"})


@tool
def update_business_model_canvas(section: str, updates: str) -> str:
    """
    Update a specific section of the Business Model Canvas.
    
    Args:
        section (str): The section to update (e.g., 'Key Partners', 'Value Proposition').
        updates (str): JSON string containing the updates to apply.
        
    Returns:
        str: Success message or error details.
    """
    try:
        # Load current data
        data = _load_json_file(BMC_FILE)
        
        # Parse updates
        try:
            updates_dict = json.loads(updates)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON format in updates parameter"})
        
        # Validate section exists or create it
        if section not in data:
            data[section] = {}
        
        # Apply updates
        if isinstance(data[section], dict) and isinstance(updates_dict, dict):
            data[section].update(updates_dict)
        elif isinstance(data[section], list) and isinstance(updates_dict, list):
            data[section] = updates_dict
        else:
            data[section] = updates_dict
        
        # Save updated data
        if _save_json_file(BMC_FILE, data):
            return json.dumps({
                "success": True,
                "message": f"Business Model Canvas section '{section}' updated successfully",
                "section": section,
                "updates": updates_dict
            })
        else:
            return json.dumps({"error": "Failed to save Business Model Canvas updates"})
            
    except Exception as e:
        logger.error(f"Error in update_business_model_canvas: {e}")
        return json.dumps({"error": f"Failed to update Business Model Canvas: {str(e)}"})


# Value Proposition Canvas Tools

@tool
def get_value_proposition_canvas() -> str:
    """
    Retrieve current Value Proposition Canvas data.
    
    Returns:
        str: JSON string containing the complete Value Proposition Canvas.
    """
    try:
        data = _load_json_file(VPC_FILE)
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_value_proposition_canvas: {e}")
        return json.dumps({"error": f"Failed to load Value Proposition Canvas: {str(e)}"})


@tool
def update_value_proposition_canvas(section: str, updates: str) -> str:
    """
    Update a specific section of the Value Proposition Canvas.
    
    Args:
        section (str): The section to update (e.g., 'Customer Profile', 'Value Proposition').
        updates (str): JSON string containing the updates to apply.
        
    Returns:
        str: Success message or error details.
    """
    try:
        # Load current data
        data = _load_json_file(VPC_FILE)
        
        # Parse updates
        try:
            updates_dict = json.loads(updates)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON format in updates parameter"})
        
        # Validate section exists or create it
        if section not in data:
            data[section] = {}
        
        # Apply updates
        if isinstance(data[section], dict) and isinstance(updates_dict, dict):
            data[section].update(updates_dict)
        elif isinstance(data[section], list) and isinstance(updates_dict, list):
            data[section] = updates_dict
        else:
            data[section] = updates_dict
        
        # Save updated data
        if _save_json_file(VPC_FILE, data):
            return json.dumps({
                "success": True,
                "message": f"Value Proposition Canvas section '{section}' updated successfully",
                "section": section,
                "updates": updates_dict
            })
        else:
            return json.dumps({"error": "Failed to save Value Proposition Canvas updates"})
            
    except Exception as e:
        logger.error(f"Error in update_value_proposition_canvas: {e}")
        return json.dumps({"error": f"Failed to update Value Proposition Canvas: {str(e)}"})


# Customer Segments Tools

@tool
def get_customer_segments() -> str:
    """
    Retrieve current customer segments data.
    
    Returns:
        str: JSON string containing all customer segments.
    """
    try:
        data = _load_json_file(SEGMENTS_FILE)
        return json.dumps(data, indent=2)
    except Exception as e:
        logger.error(f"Error in get_customer_segments: {e}")
        return json.dumps({"error": f"Failed to load customer segments: {str(e)}"})


@tool
def update_customer_segments(segment_id: str, updates: str) -> str:
    """
    Update a specific customer segment.
    
    Args:
        segment_id (str): The ID of the customer segment to update.
        updates (str): JSON string containing the updates to apply.
        
    Returns:
        str: Success message or error details.
    """
    try:
        # Load current data
        data = _load_json_file(SEGMENTS_FILE)
        
        # Parse updates
        try:
            updates_dict = json.loads(updates)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON format in updates parameter"})
        
        # Find and update the segment
        updated = False
        segments = data.get("customer_segments", [])
        
        for i, segment in enumerate(segments):
            if segment.get("id") == segment_id:
                # Apply updates
                if isinstance(segment, dict) and isinstance(updates_dict, dict):
                    segments[i].update(updates_dict)
                else:
                    segments[i] = updates_dict
                updated = True
                break
        
        if not updated:
            return json.dumps({"error": f"Customer segment '{segment_id}' not found"})
        
        # Save updated data
        if _save_json_file(SEGMENTS_FILE, data):
            return json.dumps({
                "success": True,
                "message": f"Customer segment '{segment_id}' updated successfully",
                "segment_id": segment_id,
                "updates": updates_dict
            })
        else:
            return json.dumps({"error": "Failed to save customer segments updates"})
            
    except Exception as e:
        logger.error(f"Error in update_customer_segments: {e}")
        return json.dumps({"error": f"Failed to update customer segments: {str(e)}"})
