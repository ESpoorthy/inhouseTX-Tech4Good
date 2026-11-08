"""Load the preserved merchant taxonomy from the project data directory."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_taxonomy(path=None):
    taxonomy_path = Path(path) if path else ROOT / "data" / "taxonomy.json"
    with taxonomy_path.open("r", encoding="utf-8") as f:
        return json.load(f)
