from pydantic import BaseModel
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FileListResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True
