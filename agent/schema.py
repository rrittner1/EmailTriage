from pydantic import BaseModel
from datetime import datetime

class EmailMetadata(BaseModel):
    sender: str
    subject: str
    date_sent: datetime
    current_date: datetime

class EvaluationResult(BaseModel):
    importance: int
    urgency: int