from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "3D Buddy Enterprise API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Configuration (to be implemented in Phase 2)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "buddy_db"

    # Redis & Celery (to be implemented in Phase 3)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
