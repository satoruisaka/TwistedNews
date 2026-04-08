"""
Configuration settings for TwistedNews application.
Processes news articles from MRA and generates commentary using TwistedPair API.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
MRA_DATA_DIR = Path("../TwistedCollab/data")
NEWS_ARTICLES_DIR = MRA_DATA_DIR / "markdown" / "news_articles"
OUTPUT_DIR = MRA_DATA_DIR / "markdown" / "twistednews"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Language codes for output filenames
LANGUAGE_CODES = {
    'chinese': 'CN',
    'russian': 'RU',
    'hebrew': 'HE',
    'arabic': 'AR',
    'spanish': 'SP'
}

# TwistedPair API Settings
TWISTEDPAIR_BASE_URL = os.getenv("TWISTEDPAIR_BASE_URL", "http://localhost:8001")
TWISTEDPAIR_TIMEOUT = int(os.getenv("TWISTEDPAIR_TIMEOUT", "300"))

# TwistedPair Distortion Parameters (configurable via environment or defaults)
TWISTEDPAIR_MODE = os.getenv("TWISTEDPAIR_MODE", "so_what_er")  # Default: so_what_er for news analysis
TWISTEDPAIR_TONE = os.getenv("TWISTEDPAIR_TONE", "primal")   # Default: primal for news commentary
TWISTEDPAIR_GAIN = int(os.getenv("TWISTEDPAIR_GAIN", "7"))      # Default: 7 (moderate intensity)

# Available modes and tones (for validation)
DISTORTION_MODES = ["invert_er", "so_what_er", "echo_er", "what_if_er", "cucumb_er", "archiv_er"]
DISTORTION_TONES = ["neutral", "technical", "primal", "poetic", "satirical"]

# Ollama Settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:30b")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "128000"))  # Large context window for processing multiple articles

# Email Settings (same as NewsAgent)
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = os.getenv("EMAIL_SMTP_PORT", "587")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")

# Validate email configuration at startup
if not all([EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
    print("⚠️  WARNING: Email configuration incomplete in .env file")
    print("   Set EMAIL_USERNAME, EMAIL_PASSWORD, and EMAIL_RECIPIENT")

# TwistedNews Processing Settings
PROMPT_STYLE = os.getenv("PROMPT_STYLE", "comprehensive")  # Options: comprehensive, simple, raw
# - comprehensive: Detailed analytical commentary with context and synthesis
# - simple: Basic summarization with key points
# - raw: No prompt wrapping (original behavior)

# Logging
VERBOSE = os.getenv("VERBOSE", "False").lower() == "true"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
