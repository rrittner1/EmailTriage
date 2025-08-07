from langchain.tools import BaseTool
from schema import EmailMetadata, EvaluationResult

class EmailEvaluatorTool(BaseTool):
    name = "email_evaluator"
    description = "Grades email importance and urgency from metadata"

    def _run(self, sender: str, subject: str, date_sent: str, current_date: str):
        import datetime
        # Basic rules (can be enhanced later)
        importance = 50
        urgency = 50

        # Priority keywords
        if any(k in subject.lower() for k in ["urgent", "asap", "action required"]):
            urgency += 30
        if "manager" in sender.lower() or "ceo" in sender.lower():
            importance += 25
        try:
            sent_date = datetime.datetime.fromisoformat(date_sent)
            curr_date = datetime.datetime.fromisoformat(current_date)
            delta = (curr_date - sent_date).days
            if delta > 7:
                urgency -= 30
        except Exception:
            pass

        # Clamp scores
        urgency = max(0, min(100, urgency))
        importance = max(0, min(100, importance))

        return EvaluationResult(importance=importance, urgency=urgency).dict()

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
