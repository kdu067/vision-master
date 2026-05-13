from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = []

class EventResponse(BaseModel):
    id: int
    event_time: str
    label: str
    confidence: float
    image_path: Optional[str] = None

class AgentStatusResponse(BaseModel):
    name: str
    role: str
    goal: str
    events_in_context: int
    context_preview: str
