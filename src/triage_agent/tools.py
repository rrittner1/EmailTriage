import datetime
from langchain.tools import BaseTool
from triage_agent.agent_schema import EvaluationResult
from typing import ClassVar

class EmailEvaluatorTool(BaseTool):
    name: ClassVar[str] = "email_evaluator"
    description: ClassVar[str] = "Grades email importance and urgency from metadata"

    def _run(self, sender: str, subject: str, date_sent: datetime, current_date: datetime):
        importance = 50
        urgency = 50

        if any(k in subject.lower() for k in ["urgent", "asap", "action required"]):
            urgency += 30
        if "manager" in sender.lower() or "ceo" in sender.lower():
            importance += 25

        try:
            delta = (current_date - date_sent).days
            if delta > 7:
                urgency -= 30
        except Exception:
            pass

        urgency = max(0, min(100, urgency))
        importance = max(0, min(100, importance))

        return EvaluationResult(importance=importance, urgency=urgency).dict()

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")