import os
import time
import pandas as pd
from tqdm import tqdm
from app.utils.token_estimation import estimate_tokens
from app.utils.file_io import save_json_file, load_json_file
from app.utils.logger import setup_logger
from app.utils.prompt_loader import load_prompt_template
from app.services.cleaner import clean_text_column
from app.config import GROQ_API_KEY, SUMMARY_DIR
from groq import Groq
import json
import re
from datetime import datetime

logger = setup_logger(os.path.join(SUMMARY_DIR, "summarization.log"))

client = Groq(api_key=GROQ_API_KEY)

MAX_RPM = 30
MAX_TPD = 500000
SECONDS_PER_REQUEST = 60 / MAX_RPM

token_used = 0
request_count = 0

PROMPT_TEMPLATE_PATH = "app/services/summarization_prompt.txt"
prompt_template = load_prompt_template(PROMPT_TEMPLATE_PATH)

def safe_parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found.")
        json_block = match.group()
        json_block = re.sub(r'//.*', '', json_block)
        return json.loads(json_block)

def summarize_conversation(conversation: list):
    global token_used, request_count

    conversation_text = ""
    for msg in conversation:
        sender = "Client" if msg["sender"] == "client" else "Agent"
        conversation_text += f"{sender}: {msg['text']}\n"

    prompt = prompt_template.replace("{conversation_text}", conversation_text)

    input_tokens = estimate_tokens(prompt)
    total_estimated_tokens = input_tokens + 300

    if token_used + total_estimated_tokens > MAX_TPD:
        raise RuntimeError("Token limit exceeded.")
    if request_count >= 14400:
        raise RuntimeError("Request limit exceeded.")

    time.sleep(SECONDS_PER_REQUEST)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content
    parsed = safe_parse_json(content)

    token_used += total_estimated_tokens
    request_count += 1

    return parsed

def summarize_opportunities(filepath: str):
    logger.info(f"Starting summarization for file: {filepath}")
    df = pd.read_csv(filepath)
    df = clean_text_column(df)

    opportunity_groups = df.groupby("opportunity_id")
    summaries = {}
    skipped = []

    for opp_id, group in tqdm(opportunity_groups, desc="Summarizing Opportunities"):
        logger.info(f"Processing opportunity_id: {opp_id}")

        conversation = []
        group = group.sort_values("date")

        for _, row in group.iterrows():
            text = row.get("text", "")
            if isinstance(text, str) and text.strip():
                sender = "client" if pd.notna(row["user_id"]) else "agent"
                conversation.append({"sender": sender, "text": text})

        if not conversation:
            logger.warning(f"Skipping empty conversation for {opp_id}")
            continue

        try:
            summary = summarize_conversation(conversation)
            summaries[opp_id] = summary
            logger.info(f"✅ Summarized opportunity_id: {opp_id}")
        except Exception as e:
            logger.error(f"❌ Error processing {opp_id}: {e}")
            skipped.append(opp_id)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(SUMMARY_DIR, f"summaries_{timestamp}.json")
    save_json_file(summary_file, summaries)

    logger.info(f"Summarization complete. {len(summaries)} summaries generated.")
    if skipped:
        logger.warning(f"Skipped {len(skipped)} opportunities: {skipped}")


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(SUMMARY_DIR, f"summaries_{timestamp}.json")
    save_json_file(summary_file, summaries)

    logger.info(f"Summarization complete. File saved at {summary_file}")
    return summary_file

    # return summaries




# import os
# import pandas as pd
# from app.utils.file_io import read_csv_file, save_json_file, load_json_file
# from app.services.cleaner import clean_text_column
# from app.utils.token_estimation import estimate_tokens
# from groq import Groq
# import time
# import json
# import re

# client = Groq(api_key="your_groq_api_key")

# SECONDS_PER_REQUEST = 2  # Based on rate limits

# def summarize_conversation(conversation):
#     conversation_text = "\n".join([f"{msg['sender'].title()}: {msg['text']}" for msg in conversation])
    
#     prompt = f"""
# You are an assistant summarizing client-agent conversations.

# Return a structured JSON with:
# 1. detailed summary of the conversation
# 2. sentiment_overall (positive/neutral/negative)
# 3. sentiment_details (client & agent sentiment)
# 4. concerned_departments (choose from: Support, Sales, Logistics, Finance)

# Conversation:
# {conversation_text}

# Respond strictly in this JSON format, with no comments or extra text:
# {{
#   "summary": "...",
#   "sentiment_overall": "...",
#   "sentiment_details": {{
#     "client": "...",
#     "agent": "..."
#   }},
#   "concerned_departments": ["..."]
# }}
# """

#     time.sleep(SECONDS_PER_REQUEST)
#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.7
#     )

#     raw_output = response.choices[0].message.content

#     match = re.search(r'\{.*\}', raw_output, re.DOTALL)
#     if not match:
#         raise ValueError("Invalid JSON format returned.")
    
#     return json.loads(match.group())


# def summarize_opportunities(filepath: str):
#     df = read_csv_file(filepath)
#     df = clean_text_column(df)

#     grouped = df.groupby("opportunity_id")
#     results = {}

#     for opp_id, group in grouped:
#         group = group.sort_values("date")
#         conversation = []

#         for _, row in group.iterrows():
#             if isinstance(row["text"], str) and row["text"].strip():
#                 sender = "client" if row["user_id"] is not None else "agent"
#                 conversation.append({"sender": sender, "text": row["text"]})

#         if conversation:
#             try:
#                 summary = summarize_conversation(conversation)
#                 results[opp_id] = summary
#             except Exception as e:
#                 results[opp_id] = {"error": str(e)}


#     save_json_file(f"summaries/{os.path.basename(filepath)}_summaries.json", results)
#     return results





