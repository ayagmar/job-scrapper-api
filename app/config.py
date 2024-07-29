from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://jobuser:jobpassword@localhost/jobscraper"
    LOG_LEVEL: str = "INFO"
    DROP_AND_CREATE_SCHEMA: bool = True

settings = Settings()