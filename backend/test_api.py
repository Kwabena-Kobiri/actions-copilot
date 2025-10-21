#!/usr/bin/env python3
"""
Simple test script to verify the API functions work correctly.
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sprint_functions():
    """Test the sprint functions directly."""
    try:
        from app.copilot.tools.sprint_tools import _get_sprint_items, _get_sprint_item
        from app.copilot.tools.canvas_tools import _get_business_model_canvas, _get_value_proposition_canvas, _get_customer_segments
        
        print("Testing sprint functions...")
        
        # Test get_sprint_items
        result = _get_sprint_items()
        data = json.loads(result)
        print(f"[OK] get_sprint_items: {len(data)} items found")
        
        # Test get_sprint_item (if there are items)
        if data and len(data) > 0:
            # Check if data is a list or dict
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                first_item_id = first_item.get('item_id', 'test_id')
            elif isinstance(data, dict) and 'sprints' in data:
                first_item = data['sprints'][0]
                first_item_id = first_item.get('item_id', 'test_id')
            else:
                first_item_id = 'test_id'
            
            result = _get_sprint_item(first_item_id)
            item_data = json.loads(result)
            print(f"[OK] get_sprint_item: Item found")
        
        # Test canvas functions
        bmc_result = _get_business_model_canvas()
        bmc_data = json.loads(bmc_result)
        print(f"[OK] get_business_model_canvas: Canvas loaded")
        
        vpc_result = _get_value_proposition_canvas()
        vpc_data = json.loads(vpc_result)
        print(f"[OK] get_value_proposition_canvas: Canvas loaded")
        
        segments_result = _get_customer_segments()
        segments_data = json.loads(segments_result)
        print(f"[OK] get_customer_segments: Segments loaded")
        
        print("\n[SUCCESS] All functions work correctly!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sprint_functions()
    sys.exit(0 if success else 1)
