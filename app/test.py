"""
Basic tests for the Sprint Coordinator application.
Tests core functionality and data loading.
"""

import json
from pathlib import Path
from config import SPRINTS_FILE, BMC_FILE, VPC_FILE, SEGMENTS_FILE
from copilot.tools.sprint_tools import _load_sprints_data
from copilot.tools.canvas_tools import _load_json_file


def test_data_files_exist():
    """Test that all required data files exist."""
    assert SPRINTS_FILE.exists(), f"Sprints file not found: {SPRINTS_FILE}"
    assert BMC_FILE.exists(), f"BMC file not found: {BMC_FILE}"
    assert VPC_FILE.exists(), f"VPC file not found: {VPC_FILE}"
    assert SEGMENTS_FILE.exists(), f"Segments file not found: {SEGMENTS_FILE}"


def test_sprints_data_loading():
    """Test that sprints data can be loaded and parsed."""
    data = _load_sprints_data()
    
    # Check basic structure
    assert isinstance(data, dict), "Sprints data should be a dictionary"
    assert "sprints" in data, "Sprints data should contain 'sprints' key"
    assert "sprint_analysis" in data, "Sprints data should contain 'sprint_analysis' key"
    
    # Check sprints structure
    sprints = data["sprints"]
    assert isinstance(sprints, list), "Sprints should be a list"
    
    if sprints:  # If there are sprints, check their structure
        sprint = sprints[0]
        required_keys = ["sprint_id", "title", "goal", "items"]
        for key in required_keys:
            assert key in sprint, f"Sprint should contain '{key}'"
        
        # Check items structure
        items = sprint["items"]
        assert isinstance(items, list), "Sprint items should be a list"
        
        if items:  # If there are items, check their structure
            item = items[0]
            required_item_keys = ["item_id", "task", "objective", "success_metric", "status"]
            for key in required_item_keys:
                assert key in item, f"Sprint item should contain '{key}'"


def test_bmc_data_loading():
    """Test that Business Model Canvas data can be loaded."""
    data = _load_json_file(BMC_FILE)
    
    assert isinstance(data, dict), "BMC data should be a dictionary"
    
    # Check for key BMC sections
    expected_sections = [
        "Key Partners", "Key Activities", "Key Resources", 
        "Value Proposition", "Customer Relationships", "Channels",
        "Customer Segment", "Cost Structure", "Revenue Streams"
    ]
    
    for section in expected_sections:
        assert section in data, f"BMC should contain '{section}' section"


def test_vpc_data_loading():
    """Test that Value Proposition Canvas data can be loaded."""
    data = _load_json_file(VPC_FILE)
    
    assert isinstance(data, dict), "VPC data should be a dictionary"
    
    # Check for key VPC sections
    expected_sections = ["Customer Profile", "Value Proposition"]
    for section in expected_sections:
        assert section in data, f"VPC should contain '{section}' section"


def test_segments_data_loading():
    """Test that customer segments data can be loaded."""
    data = _load_json_file(SEGMENTS_FILE)
    
    assert isinstance(data, dict), "Segments data should be a dictionary"
    assert "customer_segments" in data, "Segments data should contain 'customer_segments' key"
    
    segments = data["customer_segments"]
    assert isinstance(segments, list), "Customer segments should be a list"
    
    if segments:  # If there are segments, check their structure
        segment = segments[0]
        required_keys = ["id", "archetype", "demographics"]
        for key in required_keys:
            assert key in segment, f"Customer segment should contain '{key}'"


def test_json_validity():
    """Test that all JSON files are valid."""
    files = [SPRINTS_FILE, BMC_FILE, VPC_FILE, SEGMENTS_FILE]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise AssertionError(f"Error reading {file_path}: {e}")


def test_agent_imports():
    """Test that all agent modules can be imported."""
    try:
        from copilot.agent import create_master_agent, create_session_service
        from copilot.sub_agents import (
            create_design_agent,
            create_execute_agent,
            create_report_agent,
            create_learn_agent
        )
        from copilot.tools import (
            get_sprint_items,
            get_sprint_item,
            update_sprint_item_status,
            get_business_model_canvas,
            update_business_model_canvas
        )
    except ImportError as e:
        raise AssertionError(f"Failed to import agent modules: {e}")


if __name__ == "__main__":
    # Run basic tests
    print("Running Sprint Coordinator tests...")
    
    try:
        test_data_files_exist()
        print("✅ Data files exist")
        
        test_sprints_data_loading()
        print("✅ Sprints data loading")
        
        test_bmc_data_loading()
        print("✅ BMC data loading")
        
        test_vpc_data_loading()
        print("✅ VPC data loading")
        
        test_segments_data_loading()
        print("✅ Segments data loading")
        
        test_json_validity()
        print("✅ JSON validity")
        
        test_agent_imports()
        print("✅ Agent imports")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
