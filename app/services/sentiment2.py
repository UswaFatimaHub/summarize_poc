import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.db import get_records_by_opportunity_id
from app.core.logger import logger
from app.config import get_settings
settings = get_settings()

# Enabled model keys (e.g., "nlptown,visalkao")
ENABLED_MODELS = settings.sentiment_analysis_models.split(',')

# Map model keys to HuggingFace model IDs
MODEL_MAP = {
    "nlptown": "nlptown/bert-base-multilingual-uncased-sentiment",
    "visalkao": "visalkao/sentiment-analysis-french"
}

# Initialize model/tokenizer pairs
MODEL_INSTANCES = {}

logger.info(f"Loading models: {ENABLED_MODELS}")
for key in ENABLED_MODELS:
    model_name = MODEL_MAP.get(key)
    if model_name:
        logger.info(f"Loading model '{model_name}' for key '{key}'")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        MODEL_INSTANCES[key] = {
            "model": model,
            "tokenizer": tokenizer
        }
    else:
        logger.warning(f"Unknown model key '{key}', skipping.")

def extract_conversation_by_role(conversation: list, role: str = None) -> str:
    filtered = (
        [msg for msg in conversation if msg["sender"] == role]
        if role else conversation
    )
    logger.info(f"Extracted {len(filtered)} messages for role: {role or 'all'}")
    return '\n'.join(
        f"{msg['sender'].capitalize()}: {msg['text']}" for msg in filtered
    )

def analyze_sentiment(text: str, model_key: str) -> dict:
    if not text.strip():
        logger.warning(f"[{model_key}] Empty text input for sentiment analysis.")
        return {"star_rating": None, "confidence": 0.0, "message": "No content provided."}

    logger.info(f"[{model_key}] Analyzing sentiment for {len(text)} characters")

    tokenizer = MODEL_INSTANCES[model_key]["tokenizer"]
    model = MODEL_INSTANCES[model_key]["model"]

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = F.softmax(logits, dim=-1)

    predicted_class = torch.argmax(probabilities, dim=-1).item() + 1
    confidence = probabilities[0][predicted_class - 1].item()

    logger.info(
        f"[{model_key}] Sentiment: {predicted_class} stars, confidence: {round(confidence, 4)}"
    )

    return {
        "star_rating": predicted_class,
        "confidence": round(confidence, 4)
    }

def run_sentiment_pipeline(conversation: list) -> dict:
    logger.info(f"Starting sentiment pipeline...")

    client_text = extract_conversation_by_role(conversation, "client")
    agent_text = extract_conversation_by_role(conversation, "agent")
    full_text = extract_conversation_by_role(conversation)

    result = {}
    for model_key in MODEL_INSTANCES:
        logger.info(f"[{model_key}] Running sentiment analysis for client, agent, and full")
        result[model_key] = {
            "client_sentiment": analyze_sentiment(client_text, model_key),
            "agent_sentiment": analyze_sentiment(agent_text, model_key),
            "full_conversation_sentiment": analyze_sentiment(full_text, model_key)
        }

    logger.info(f"Sentiment analysis completed...")
    return result


