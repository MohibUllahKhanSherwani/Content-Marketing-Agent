from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

from content_marketing_agent.config.settings import AppSettings, get_settings


def create_db_engine(settings: AppSettings | None = None) -> Engine:
    resolved = settings or get_settings()
    connect_args = {"check_same_thread": False} if resolved.database_url.startswith("sqlite") else {}
    return create_engine(resolved.database_url, connect_args=connect_args)


def create_db_and_tables(settings: AppSettings | None = None) -> None:
    engine = create_db_engine(settings)
    SQLModel.metadata.create_all(engine)
