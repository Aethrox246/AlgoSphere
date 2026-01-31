import os
from pathlib import Path
from dotenv import load_dotenv

# project root = profile-service/
ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
