"""
Configuration module for the Sprint Coordinator application.
Handles environment variables and application constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application constants
APP_NAME = os.getenv("APP_NAME", "sprint_coordinator")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "user1234")

# Data file paths - pointing to shared global data folder
BASE_DIR = Path(__file__).parent
# Navigate up to workspace root, then into global data folder
WORKSPACE_ROOT = BASE_DIR.parent.parent
DATA_DIR = WORKSPACE_ROOT / "global data"

SPRINTS_FILE = DATA_DIR / "sprints.json"
BMC_FILE = DATA_DIR / "bmc.json"
VPC_FILE = DATA_DIR / "vpc.json"
SEGMENTS_FILE = DATA_DIR / "segments.json"

# Google ADK configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Model configuration
DEFAULT_MODEL = "gemini-2.5-flash"
