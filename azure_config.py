"""
Azure-specific configuration for production deployment
"""
import os
from typing import Optional
class AzureConfig:
    """"""Azure deployment configuration""""""
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    # Database - Azure PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@server.postgres.database.azure.com:5432/documents_db?sslmode=require"
    )
    # Azure Storage Account for file uploads
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    # CORS Origins (Azure URLs)
    ALLOWED_ORIGINS: list = [
        "https://yourdomain.azurewebsites.net",
        "https://www.yourdomain.com",
        "http://localhost:3000",  # For local development
    ]
    # File upload settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))  # 50MB default
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")  # Azure temp storage
    # Worker settings
    WORKERS: int = int(os.getenv("WORKERS", 4))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 120))
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    @classmethod
    def is_production(cls) -> bool:
        return cls.ENVIRONMENT == "production"
    @classmethod
    def use_azure_storage(cls) -> bool:
        return bool(cls.AZURE_STORAGE_CONNECTION_STRING)
# Singleton instance
azure_config = AzureConfig()
