"""Apply the current declarative schema migration to DATABASE_URL."""
from pathlib import Path
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.database import configure_database, init_database

configure_database(os.getenv("DATABASE_URL", "sqlite:///inhouse_tx.db"))
init_database()
print("Database schema is at version 1.")
