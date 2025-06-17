from app.utils.token_estimation import estimate_tokens
from app.utils.cleaning import truncate_conversation
# from app.utils.logger import setup_logger
from app.core.logger import logger
from app.config import get_settings
import os

settings = get_settings()
MAX_CONTEXT_TOKENS = settings.max_context_tokens  
MAX_OUTPUT_TOKENS = settings.max_output_tokens  
MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - MAX_OUTPUT_TOKENS
# logger = setup_logger(os.path.join(settings.log_dir))
from app.core.logger import logger


def build_prompt_from_conversation(conversation: list, prompt_file_path: str) -> str:
    # Load the prompt template from file
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    placeholder = "{conversation_text}"
    if placeholder not in prompt_template:
        raise ValueError(f"Prompt template must contain the placeholder '{placeholder}'")

    # Estimate how much room we have for the conversation
    template_tokens = estimate_tokens(prompt_template.replace(placeholder, ""))
    max_tokens_for_convo = MAX_INPUT_TOKENS - template_tokens
    logger.info(f"Tokens available for conversation: {max_tokens_for_convo}")

    # Truncate and inject conversation into the prompt
    conversation_text = truncate_conversation(conversation, max_tokens_for_convo)
    prompt = prompt_template.replace(placeholder, conversation_text)

    # logger.info(f"Final prompt built from file {prompt_file_path}: {prompt[:300]}...")  # truncate log if long
    return prompt
