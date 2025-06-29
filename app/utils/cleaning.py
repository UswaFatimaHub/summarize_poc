from app.utils.token_estimation import estimate_tokens
from bs4 import BeautifulSoup
import pandas as pd
import json
import re

def clean_html_text(html):
    if not isinstance(html, str):
        return ""
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(separator="\n")
    clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return "\n".join(clean_lines)

def clean_text_column(df):
    mask = df["class"].isin(["traction.communication.MailMessage", "traction.communication.FormClientData"])
    df.loc[mask, "text"] = df.loc[mask, "text"].apply(clean_html_text)
    return df

def truncate_conversation(conversation: list, max_tokens_for_convo: int) -> str:
    """Constructs conversation text from the end, keeping within max_tokens_for_convo."""
    reversed_conv = reversed(conversation)
    accumulated = []
    total_tokens = 0

    for msg in reversed_conv:
        sender = "Client" if msg["sender"] == "client" else "Agent"
        line = f"{sender}: {msg['text']}\n"
        line_tokens = estimate_tokens(line)

        if total_tokens + line_tokens > max_tokens_for_convo:
            break
        accumulated.append(line)
        total_tokens += line_tokens

    return ''.join(reversed(accumulated))

def clean_json_response(content: str) -> str:
    # Check if there's a JSON object in the content
    if "{" in content and "}" in content:
        # Remove everything before the first '{'
        return re.sub(r'^.*?{', '{', content, flags=re.DOTALL)
    return content

def safe_parse_json(text):
    cleaned_text = clean_json_response(text)
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Try extracting { ... } block manually
        match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
        if match:
            json_block = match.group()
            # Remove inline comments
            json_block = re.sub(r'//.*', '', json_block)
            try:
                return json.loads(json_block)
            except json.JSONDecodeError:
                pass  # Fall through to return original
        # Return raw text
        return text