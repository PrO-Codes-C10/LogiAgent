import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Database URL
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "logiagent.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# OpenAi API Key (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Geolocation & Logistics Defaults
EARTH_RADIUS_KM = 6371.0
DEFAULT_TRANSIT_SPEED_KMH = float(os.getenv("DEFAULT_SPEED_KMH", "65.0"))
