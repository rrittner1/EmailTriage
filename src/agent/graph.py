from langgraph.graph import StateGraph, END
from schema import EmailMetadata
from agent import create_agent

def build_graph():
    agent = create_agent()

    def invoke_agent(state):
        result = agent.run(f"Evaluate this email:\nSender: {state.sender}\nSubject: {state.subject}\nSent: {state.date_sent}\nNow: {state.current_date}")
        return {"result": result}

    workflow = StateGraph(EmailMetadata)
    workflow.add_node("evaluate", invoke_agent)
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", END)

    app = workflow.compile()
    return app