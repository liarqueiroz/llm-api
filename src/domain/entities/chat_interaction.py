from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatInteraction(BaseModel):
    id: Optional[str] = None
    userId: str
    prompt: str
    response: str
    model: str
    timestamp: datetime
