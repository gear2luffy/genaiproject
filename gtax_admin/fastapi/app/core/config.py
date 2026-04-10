"""
Configuration management using Pydantic Settings.

Demonstrates:
- Environment variable loading
- Type validation
- Settings inheritance
- Computed properties
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic Settings for automatic validation and type coercion.
    All settings can be overridden via environment variables or .env file.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Settings
    app_name: str = Field(default="Task Management API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: str = Field(default="production", description="Environment name")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, description="Number of workers")
    
    # Database Settings
    database_url: str = Field(
        default="sqlite+aiosqlite:///./task_management.db",
        description="Database connection URL"
    )
    
    # Redis Settings
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # JWT Settings
    secret_key: str = Field(
        default="change-me-in-production",
        min_length=32,
        description="Secret key for JWT encoding"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, ge=1, description="Access token expiry")
    refresh_token_expire_days: int = Field(default=7, ge=1, description="Refresh token expiry")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, ge=1, description="Rate limit per minute")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or console)")
    
    # CORS Settings
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed origins"
    )
    
    # File Upload Settings
    max_upload_size: int = Field(default=10485760, description="Max upload size in bytes")
    upload_dir: str = Field(default="./uploads", description="Upload directory path")
    
    # Celery Settings
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        valid_envs = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v.lower()
    
    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @computed_field
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    This is a common pattern for dependency injection in FastAPI.
    
    Returns:
        Settings: The application settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()
