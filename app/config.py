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

# Data file paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "copilot" / "data"

SPRINTS_FILE = DATA_DIR / "sprints.json"
BMC_FILE = DATA_DIR / "bmc.json"
VPC_FILE = DATA_DIR / "vpc.json"
SEGMENTS_FILE = DATA_DIR / "segments.json"

# Google ADK configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Model configuration
DEFAULT_MODEL = "gemini-2.0-flash"
