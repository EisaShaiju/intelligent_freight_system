from typing import Literal
from pydantic import BaseModel
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from agents.state import LogisticsState
from agents.sub_agents import logistics_node, compliance_node, dispatch_node

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# The Pydantic model forces the LLM to output a valid routing decision
class Router(BaseModel):
    next: Literal["logistics", "compliance", "dispatch", "FINISH"]

SUPERVISOR_PROMPT = """
You are the master orchestrator for an airline logistics platform.
Analyze the package anomaly and the conversation history, then route to the correct specialist.
- Routing or delay issue -> 'logistics'.
- Packaging or safety issue -> 'compliance'.
- Once a solution is planned by a specialist, ALWAYS use 'dispatch' to assign a human to execute it.
- Reply 'FINISH' only when a staff member has been successfully dispatched.
"""

def supervisor_node(state: LogisticsState) -> Command[Literal["logistics", "compliance", "dispatch", "__end__"]]:
    # Use structured output to guarantee we get a valid literal back
    response = llm.with_structured_output(Router).invoke(
        [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]
    )
    
    if response.next == "FINISH":
        return Command(goto=END)
    
    return Command(goto=response.next)

# --- Compile the Graph ---
builder = StateGraph(LogisticsState)

# Add all nodes
builder.add_node("supervisor", supervisor_node)
builder.add_node("logistics", logistics_node)
builder.add_node("compliance", compliance_node)
builder.add_node("dispatch", dispatch_node)

# The workflow always begins with the supervisor evaluating the anomaly
builder.add_edge(START, "supervisor")

# Compile into a runnable application
orchestrator_app = builder.compile()