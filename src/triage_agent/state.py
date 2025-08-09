from typing import TypedDict
from datetime import datetime

class EmailState(TypedDict):
    sender: str
    subject: str
    email_date: datetime
    current_date: datetime
    importance: int
    urgency: int