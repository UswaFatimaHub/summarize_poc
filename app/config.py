from dotenv import load_dotenv
import os
from pydantic import BaseSettings
from functools import lru_cache


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
SUMMARY_DIR = os.getenv("SUMMARY_DIR", "summaries")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)


class Settings(BaseSettings):
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME")

@lru_cache()
def get_settings():
    return Settings()
