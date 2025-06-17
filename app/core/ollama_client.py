# import os
import ollama
# from app.utils.logger import setup_logger
from app.config import get_settings

settings = get_settings()
MAX_OUTPUT_TOKENS = settings.max_output_tokens  
# logger = setup_logger(os.path.join(settings.log_dir))


from app.core.logger import logger


def send_to_ollama(messages: list, temperature=0.1, max_output_tokens=MAX_OUTPUT_TOKENS) -> str:
    response = ollama.chat(
        model=settings.ollama_model,
        messages=messages,
        options={
            "temperature": temperature,
            "num_predict": max_output_tokens
        }
    )
    raw_content = response["message"]["content"].strip()
    logger.info(f"Ollama raw response: {raw_content}")
    return raw_content
