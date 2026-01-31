import os
import sys
from pathlib import Path

# Go up from alembic/ to auth-service/
service_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(service_root))

from src.database import Base, engine

target_metadata = Base.metadata