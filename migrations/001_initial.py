"""Initial schema marker. Tables are declared in api.models and versioned here."""
from api.database import Base
from api import models  # noqa: F401

VERSION = 1

def upgrade(engine):
    Base.metadata.create_all(engine)
