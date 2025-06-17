import os
import pandas as pd
from app.config import get_settings
# from app.utils.logger import setup_logger
from app.services.summarization import summarize_conversation
from app.services.sentiment import analyze_sentiment
from app.db import get_records_by_opportunity_id
settings = get_settings()

# logger = setup_logger(os.path.join(settings.log_dir))

from app.core.logger import logger


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
        sentiment = analyze_sentiment(conversation)

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

