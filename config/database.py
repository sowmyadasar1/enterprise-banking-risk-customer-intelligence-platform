from config.settings import settings

def get_database_uri() -> str:
    """
    Construct the database URI from settings.
    Returns:
        str: SQLAlchemy compatible connection string.
    """
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

# Engine configuration parameters
ENGINE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800,
}
