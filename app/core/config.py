from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Presell Platform API"
    API_V1_STR: str = "/api/v1"

    # Database - Read from environment variable for Render compatibility
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./presell_platform.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 day

    # First Superuser
    FIRST_SUPERUSER_EMAIL: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "changethis")

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000", 
        "http://localhost:8000", 
        "https://presell-platform-frontend.vercel.app",
        "https://5176-igk5lxbgg8d1hr6d2zi4a-b4d88b30.manusvm.computer",
        "https://5174-igk5lxbgg8d1hr6d2zi4a-b4d88b30.manusvm.computer",
        "https://5175-igk5lxbgg8d1hr6d2zi4a-b4d88b30.manusvm.computer",
        "https://5173-igk5lxbgg8d1hr6d2zi4a-b4d88b30.manusvm.computer",
        "https://*.manusvm.computer"
    ]

    # Generated assets directory
    GENERATED_ASSETS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "generated_assets")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in environment variables

settings = Settings()
