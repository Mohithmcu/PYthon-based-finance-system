from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./finance.db"

    class Config:
        env_file = ".env"


settings = Settings()
