from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
SUMMARY_DIR = os.getenv("SUMMARY_DIR", "summaries")
MAX_CONTEXT_TOKENS = os.getenv("MAX_CONTEXT_TOKENS", 128000)  
MAX_OUTPUT_TOKENS = os.getenv("MAX_OUTPUT_TOKENS", 300)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)


class Settings(BaseSettings):
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    max_context_tokens: int = MAX_CONTEXT_TOKENS
    max_output_tokens: int = MAX_OUTPUT_TOKENS
    prompt_template_path: str = os.getenv("PROMPT_TEMPLATE_PATH")

@lru_cache()
def get_settings():
    return Settings()
