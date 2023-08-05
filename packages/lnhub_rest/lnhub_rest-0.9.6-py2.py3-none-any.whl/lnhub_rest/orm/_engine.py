from sqlmodel import create_engine

from ..config import Settings

settings = Settings()
if settings.postgres_dsn:
    engine = create_engine(settings.postgres_dsn)  # enqine
else:
    engine = None
