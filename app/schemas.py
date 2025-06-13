from pydantic import BaseModel
from typing import List, Optional, Dict

class Message(BaseModel):
    sender: str
    text: str

class SummaryResponse(BaseModel):
    summary: str
    sentiment_overall: str
    sentiment_details: Dict[str, str]
    concerned_departments: List[str]
