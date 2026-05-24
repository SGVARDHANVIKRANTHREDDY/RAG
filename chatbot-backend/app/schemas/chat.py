from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"
    space_id: Optional[str] = "general"

class ChatResponse(BaseModel):
    id: int
    user_id: int
    title: str
    space_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    role: str
    content: str
    sources: Optional[List[dict]] = None

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    sources: Optional[List[dict]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
