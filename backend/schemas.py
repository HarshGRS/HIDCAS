from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_size: int | None
    file_type: str | None
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True