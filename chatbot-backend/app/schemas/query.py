from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    chat_id: Optional[int] = None
    file_ids: Optional[List[int]] = None
    stream: bool = False

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    chat_id: int
    message_id: int
