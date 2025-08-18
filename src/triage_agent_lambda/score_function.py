# Function to determine ranking of emails based on importance and urgency
def score_function(importance: int, urgency: int) -> int:
    return importance + urgency