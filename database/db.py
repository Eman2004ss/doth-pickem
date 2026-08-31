import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Load .env for local development. Render supplies environment variables
# directly, so this has no effect there unless a .env file is present.
load_dotenv()

DATABASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_PATH = DATABASE_DIR / "dothpick.db"


def _normalize_database_url(url: str) -> str:
    """Return a SQLAlchemy URL that uses Psycopg 3 for PostgreSQL."""

    url = url.strip()

    # Some platforms still provide the legacy postgres:// scheme.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    # SQLAlchemy's bare postgresql:// URL normally looks for psycopg2.
    # This project uses the modern Psycopg 3 driver instead.
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]

    return url


_raw_database_url = os.environ.get("DATABASE_URL", "").strip()
_running_on_render = os.environ.get("RENDER", "").strip().lower() == "true"

if _raw_database_url:
    DATABASE_URL = _normalize_database_url(_raw_database_url)
    USING_POSTGRES = DATABASE_URL.startswith("postgresql+")
elif _running_on_render:
    # Never silently fall back to a file database in production. Render sets
    # RENDER=true automatically, so a missing Neon URL becomes an obvious
    # deployment error instead of an app that appears to work but loses data.
    raise RuntimeError(
        "DATABASE_URL is required on Render. Set it to your Neon PostgreSQL "
        "connection string in Render -> Environment."
    )
else:
    # Convenient local-development fallback. Production on Render is guarded
    # above and therefore cannot accidentally use this SQLite file.
    DATABASE_URL = f"sqlite:///{LOCAL_DB_PATH.as_posix()}"
    USING_POSTGRES = False


engine_kwargs = {
    "pool_pre_ping": True,
}

if USING_POSTGRES:
    # Recycle stale pooled connections periodically. This is helpful when Neon
    # suspends/resumes compute or when a long-lived Render process keeps a
    # connection object around.
    engine_kwargs["pool_recycle"] = 300
else:
    engine_kwargs["connect_args"] = {"check_same_thread": False}


engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_backend_name() -> str:
    """Return a safe backend label without exposing credentials."""

    return engine.dialect.name
