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


class MessageRecords(BaseModel):
    id: int
    user_group: Optional[float]
    date: str  # You may change this to datetime if parsing is required
    opportunity_id: Optional[float]
    text: Optional[str]
    user_id: Optional[float]
    status: Optional[float]
    class_: str  # "class" is a reserved keyword in Python
    subject: Optional[str]
    source: Optional[float]
    threadid: Optional[str]
    client_id: Optional[float]