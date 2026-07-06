from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Upward AI API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./upward_ai.db"
    
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    N8N_WEBHOOK_URL: str | None = None

    # Configuración para leer el archivo .env automáticamente
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()