import os
import pandas as pd
from app.config import get_settings
# from app.utils.logger import setup_logger
from app.services.summarization import summarize_conversation
from app.services.sentiment import analyze_sentiment
from app.services.sentiment2 import run_sentiment_pipeline
from app.db import get_records_by_opportunity_id

from app.core.logger import logger
settings = get_settings()

def processconv_by_opportunity_id(opportunity_id: float):
    logger.info(f"Starting processing for opportunity_id: {opportunity_id}")

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
        if settings.sentiment_source == 1:
            sentiment = run_sentiment_pipeline(conversation=conversation)
        elif settings.sentiment_source == 0:
            sentiment = analyze_sentiment(conversation)
        else:
            sentiment_1 =run_sentiment_pipeline(conversation=conversation)
            sentiment_2 = analyze_sentiment(conversation)
            sentiment = {
                "sentiment_sa_models": sentiment_1,
                "sentiment_llm": sentiment_2
            }
        logger.info(f"✅ Processed opportunity_id: {opportunity_id}")
        logger.debug(f"Summary: {summary}")
        logger.debug(f"Sentiment: {sentiment}")
        return {
            "opportunity_id": opportunity_id,
            "summary": summary,
            "sentiment": sentiment
        }

    except Exception as e:
        logger.error(f"❌ Error processing opportunity_id {opportunity_id}: {e}")
        return {"error": str(e)}

