from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Core configuration loader for the Enterprise Banking Risk & Customer Intelligence Platform.
    Reads from environment variables and .env file.
    """

    # Project Settings
    PROJECT_NAME: str = "Enterprise Banking Risk & Customer Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "enterprise_db"

    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change_this_in_production_extremely_long_string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Model / Feature Store Paths
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    FEATURE_STORE_PATH: str = "data/feature_store"

    # Paths
    DATA_RAW_DIR: str = "data/raw"
    DATA_BRONZE_DIR: str = "data/bronze"
    DATA_SILVER_DIR: str = "data/silver"
    DATA_GOLD_DIR: str = "data/gold"

    # AWS / Cloud Config (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Initialize global settings instance
settings = Settings()
