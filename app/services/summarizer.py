import os
import pandas as pd
from tqdm import tqdm
from app.utils.token_estimation import estimate_tokens
from app.utils.logger import setup_logger
from app.utils.prompt_loader import load_prompt_template
from app.utils.cleaning import safe_parse_json, truncate_conversation
from app.config import get_settings
from app.db import get_records_by_opportunity_id
from app.config import  SUMMARY_DIR
import ollama
import re
from datetime import datetime

logger = setup_logger(os.path.join(SUMMARY_DIR, "summarization.log"))
settings = get_settings()

MAX_CONTEXT_TOKENS = settings.max_context_tokens  
MAX_OUTPUT_TOKENS = settings.max_output_tokens  
MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - MAX_OUTPUT_TOKENS

token_used = 0
request_count = 0


PROMPT_TEMPLATE_PATH = settings.prompt_template_path
prompt_template = load_prompt_template(PROMPT_TEMPLATE_PATH)

import re

def clean_json_response(content: str) -> str:
    # Check if there's a JSON object in the content
    if "{" in content and "}" in content:
        # Remove everything before the first '{'
        return re.sub(r'^.*?{', '{', content, flags=re.DOTALL)
    return content

def summarize_conversation(conversation: list):
    global token_used, request_count

    placeholder = "{conversation_text}"
    template_tokens = estimate_tokens(prompt_template.replace(placeholder, ""))
    max_tokens_for_convo = MAX_INPUT_TOKENS - template_tokens
    logger.info(f"Tokens available for conversation: {max_tokens_for_convo}")

    # Truncate conversation accordingly
    conversation_text = truncate_conversation(conversation, max_tokens_for_convo)

    prompt = prompt_template.replace("{conversation_text}", conversation_text)

    logger.info(f"Prompt for summarization: {prompt}")

    input_tokens = estimate_tokens(prompt)
    logger.info(f"Estimated input tokens: {input_tokens}")

    total_estimated_tokens = input_tokens + MAX_OUTPUT_TOKENS


    response = ollama.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.1,
            "num_predict": MAX_OUTPUT_TOKENS  # Limit to 300 output tokens
        }
    )

    content = response["message"]["content"].strip()  # Remove any extra text
    logger.info(f"Raw summary response: {content}")

    content = clean_json_response(content)



    token_used += total_estimated_tokens
    logger.info(f"Total tokens used: {token_used}")
    request_count += 1

    return content


def summarize_by_opportunity_id(opportunity_id: float):
    logger.info(f"Starting summarization for opportunity_id: {opportunity_id}")

    result = get_records_by_opportunity_id(opportunity_id)
    records_df = pd.DataFrame(result["records"])

    conversation = []
    for _, row in records_df.iterrows():
        text = row.get("text", "")
        if isinstance(text, str) and text.strip():
            sender = "client" if pd.notna(row["user_id"]) else "agent"
            conversation.append({"sender": sender, "text": text})

    if not conversation:
        logger.warning(f"No conversation found for opportunity_id: {opportunity_id}")
        return {"error": f"No conversation found for opportunity_id: {opportunity_id}"}

    try:
        summary = summarize_conversation(conversation)
        logger.info(f"✅ Summarized opportunity_id: {opportunity_id}")
        return {"opportunity_id": opportunity_id, "summary": summary}
    except Exception as e:
        logger.error(f"❌ Error processing opportunity_id {opportunity_id}: {e}")
        return {"error": str(e)}


