from typing import TypedDict
from datetime import datetime

class EmailState(TypedDict):
    sender: str
    user_email: str
    subject: str
    body: str
    email_date: datetime
    current_date: datetime
    user_profile: dict
    importance: int
    urgency: int
    justification: str