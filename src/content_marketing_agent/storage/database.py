from sqlmodel import SQLModel, create_engine

from content_marketing_agent.config.settings import AppSettings, get_settings


def create_db_engine(settings: AppSettings | None = None):
    resolved = settings or get_settings()
    return create_engine(resolved.database_url)


def create_db_and_tables(settings: AppSettings | None = None) -> None:
    engine = create_db_engine(settings)
    SQLModel.metadata.create_all(engine)

