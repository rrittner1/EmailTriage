from typing import TypedDict
from datetime import datetime

class EmailState(TypedDict):
    sender: str
    subject: str
    body: str
    email_date: datetime
    current_date: datetime
    importance: int
    urgency: int
    justification: str