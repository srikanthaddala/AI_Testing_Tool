import os
from pathlib import Path

# Application metadata
APP_TITLE = "AI-based End-to-End Testing Tool"
APP_ICON = "🧪"
APP_VERSION = "1.0.0"

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "static")
CSS_DIR = os.path.join(STATIC_DIR, "css")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

# Asset paths
LOGO_PATH = os.path.join(IMAGES_DIR, "001.png")
CSS_PATH = os.path.join(CSS_DIR, "style.css")

# Default values
DEFAULT_PORT = "22"
DEFAULT_MODEL = "o3-mini"
DEFAULT_TEST_CASES_PER_REQ = 3
DEFAULT_TIMEOUT = 30  # seconds

# OpenAI API settings
OPENAI_MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "o3-mini"]
MAX_TOKENS = 10000

# UI settings
MAIN_HEADER_COLOR = "#FF8C00"  # Dark orange
SECTION_HEADER_COLOR = "#4682B4"  # Steel blue
SUCCESS_COLOR = "#4CAF50"  # Green
WARNING_COLOR = "#FFC107"  # Amber
ERROR_COLOR = "#F44336"  # Red
INFO_COLOR = "#2196F3"  # Blue

# Export settings
DEFAULT_FILENAME_EXCEL = "test_cases.xlsx"
DEFAULT_FILENAME_CSV = "test_cases.csv"
DEFAULT_FILENAME_PDF = "test_report.pdf"

# SSH connection settings
SSH_DEFAULT_PORT = 22
SSH_TIMEOUT = 20  # seconds