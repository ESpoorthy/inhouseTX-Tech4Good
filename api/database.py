from sqlalchemy import create_engine, Table, Column, Integer, DateTime, select, insert
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

engine = None
Session = scoped_session(sessionmaker(autoflush=False, expire_on_commit=False))


class Base(DeclarativeBase):
    pass


def configure_database(url: str):
    global engine
    options = {"future": True, "pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    engine = create_engine(url, **options)
    Session.configure(bind=engine)


def init_database():
    from api import models  # noqa: F401
    Base.metadata.create_all(engine)
    versions = Table("schema_migrations", Base.metadata,
                     Column("version", Integer, primary_key=True),
                     Column("applied_at", DateTime(timezone=True), nullable=False), extend_existing=True)
    versions.create(engine, checkfirst=True)
    with engine.begin() as conn:
        if conn.scalar(select(versions.c.version).where(versions.c.version == 1)) is None:
            conn.execute(insert(versions).values(version=1, applied_at=datetime.now(timezone.utc)))


def get_db():
    from flask import g
    if "db_session" not in g:
        g.db_session = Session()
    return g.db_session


def close_db(_error=None):
    from flask import g
    db = g.pop("db_session", None)
    if db is not None:
        db.close()
    Session.remove()
