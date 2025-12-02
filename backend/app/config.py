from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./transcriptions.db"
    model_path: str = "./models/vosk-model-small-en-us-0.15"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        protected_namespaces = ('settings_',) 

@lru_cache()
def get_settings():
    return Settings()
