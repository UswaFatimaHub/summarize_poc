from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from functools import lru_cache

load_dotenv()

LOG_DIR = os.getenv("LOG_DIR", "log_dir")
MAX_CONTEXT_TOKENS = os.getenv("MAX_CONTEXT_TOKENS", 128000)  
MAX_OUTPUT_TOKENS = os.getenv("MAX_OUTPUT_TOKENS", 300)

os.makedirs(LOG_DIR, exist_ok=True)


class Settings(BaseSettings):
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    max_context_tokens: int = MAX_CONTEXT_TOKENS
    max_output_tokens: int = MAX_OUTPUT_TOKENS
    sentiment_template_path: str = os.getenv("SENTIMENT_PROMPT_TEMPLATE_PATH")
    summary_template_path: str = os.getenv("SUMMARY_PROMPT_TEMPLATE_PATH")
    log_dir: str = LOG_DIR


@lru_cache()
def get_settings():
    return Settings()
