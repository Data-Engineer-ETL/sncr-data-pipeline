"""Configuration management using Pydantic Settings."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sncr_db"
    POSTGRES_USER: str = "sncr_user"
    POSTGRES_PASSWORD: str = "change_me_in_production"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Scraper
    BASE_URL: str = "https://data-engineer-challenge-production.up.railway.app"
    MAX_RETRIES: int = 5
    RETRY_BACKOFF_FACTOR: int = 2
    REQUEST_TIMEOUT: int = 30
    CHECKPOINT_DIR: str = "./checkpoints"
    LOG_LEVEL: str = "INFO"
    
    # Target states for extraction
    TARGET_STATES: str = "SP,MG,RJ"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def async_database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def target_states_list(self) -> List[str]:
        """Parse comma-separated states into list."""
        return [s.strip().upper() for s in self.TARGET_STATES.split(",") if s.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
