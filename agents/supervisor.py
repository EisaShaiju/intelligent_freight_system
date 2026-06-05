from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.types import Command

from agents.state import LogisticsState
from core import settings

# FIX: Import node functions FROM subagents.py — don't redefine them here.
# The original code had the entire agent setup copy-pasted into both files,
# meaning 6 separate LLM agent objects were being instantiated, doubling
# token consumption and making the codebase impossible to maintain.
from agents.sub_agents import logistics_node, compliance_node, dispatch_node

# --- Supervisor LLM ---
# The supervisor only routes — it does NOT need tools, so it uses fewer tokens.
supervisor_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=settings.groq_api_key
)

SUPERVISOR_SYSTEM_PROMPT = """You are the Master Supervisor of a logistics anomaly resolution system.
You will receive a package anomaly report and decide which specialist agent to invoke next.

Your available agents are:
- "compliance"  : Checks whether the package contents or damage type violates regulations.
- "logistics"   : Finds an alternative transport route for the package.
- "dispatch"    : Finds and briefs the nearest ground staff to physically resolve the issue.
- "FINISH"      : All agents have completed their work. Resolution is ready.

Rules:
1. Always run "compliance" first for any anomaly involving damage or dangerous goods.
2. Run "logistics" after compliance if rerouting is needed.
3. Run "dispatch" last to assign human staff once the plan is complete.
4. Respond with ONLY the next agent name — one of: compliance, logistics, dispatch, FINISH.
   Do not explain your reasoning. Just output the single word."""


def supervisor_node(state: LogisticsState) -> Command[Literal["compliance", "logistics", "dispatch", "__end__"]]:
    """
    The supervisor reads the conversation so far and decides which
    sub-agent node to route to next, or whether the workflow is complete.
    """
    messages = [SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT)] + state["messages"]
    response = supervisor_llm.invoke(messages)

    # Parse the supervisor's routing decision
    decision = response.content.strip().lower()

    route_map = {
        "compliance": "compliance",
        "logistics": "logistics",
        "dispatch": "dispatch",
        "finish": "__end__",
    }

    next_node = route_map.get(decision, "__end__")
    return Command(goto=next_node)


# --- Build the LangGraph ---
def build_graph() -> StateGraph:
    builder = StateGraph(LogisticsState)

    # Register all nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("compliance", compliance_node)
    builder.add_node("logistics", logistics_node)
    builder.add_node("dispatch", dispatch_node)

    # Entry point is always the supervisor
    builder.set_entry_point("supervisor")

    return builder.compile()


# Compiled graph — imported by the FastAPI router
orchestration_graph = build_graph()