from app.core.ollama_client import send_to_ollama
from app.core.prompt_builder import build_prompt_from_conversation
from app.config import get_settings
# from app.utils.logger import setup_logger
from app.utils.cleaning import clean_json_response, safe_parse_json
from app.utils.token_estimation import estimate_tokens
from app.services import state
import os
settings = get_settings()

# logger = setup_logger(os.path.join(settings.log_dir))
from app.core.logger import logger
MAX_OUTPUT_TOKENS = settings.max_output_tokens  


def process_conversation_task( prompt_template_path: str, conversation: list, track_tokens: bool = False) -> dict:

    prompt = build_prompt_from_conversation(conversation, prompt_template_path)
    input_tokens = estimate_tokens(prompt)
    total_estimated_tokens = input_tokens + MAX_OUTPUT_TOKENS

    messages = [{"role": "user", "content": prompt}]
    content = send_to_ollama(messages)
    cleaned = safe_parse_json(content)

    if track_tokens:
        state.token_used += total_estimated_tokens
        logger.info(f"Total tokens used so far: {state.token_used}")

    return cleaned
