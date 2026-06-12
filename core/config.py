from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Centralized configuration management.
    Pydantic automatically reads these from your .env file or system environment variables.
    """
    project_name: str = "IBS Logistics Orchestrator"
    environment: str = "development"
    port: int = 8000
    
    # LLM API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    # Kafka Configuration
    kafka_broker_url: str = "localhost:9092"
    kafka_topic_anomalies: str = "logistics.anomalies"

    # --- ADDED: Supabase Configuration ---
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    class Config:
        # Tells Pydantic to look for a .env file in the root directory
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Ignores extra variables in the .env file that aren't defined here
        extra = "ignore" 

@lru_cache()
def get_settings():
    """
    Uses lru_cache so we only read the .env file once upon startup,
    improving performance across the application.
    """
    return Settings()

# Instantiate the settings so they can be imported anywhere
settings = get_settings()