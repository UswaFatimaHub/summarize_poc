from app.services.processing import process_conversation_task
from app.config import get_settings
settings = get_settings()

def summarize_conversation(conversation: list) -> dict:
    return process_conversation_task(
        prompt_template_path=settings.summary_template_path,
        conversation=conversation,
        track_tokens=True
    )
