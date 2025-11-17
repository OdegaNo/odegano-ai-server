from datetime import datetime
from typing import Optional
from beanie import Document

class Chat(Document):

    name: str
    description: Optional[str] = None
    price: float
    created_at: datetime = datetime.now()

    class Settings:
        name = "chats"