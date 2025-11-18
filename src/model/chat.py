from datetime import datetime
from typing import Optional
from beanie import Document

class Recent(Document):
    categories: dict
    main_purpose: str = ""
    people: Optional[str] = None
    day: Optional[str] = None
    options: Optional[list] = []
    created_at: datetime = datetime.now()

    class Settings:
        name = "recents"