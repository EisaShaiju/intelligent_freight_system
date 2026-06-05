from typing import Literal
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.types import Command
from langchain_core.messages import HumanMessage

from agents.state import LogisticsState
from agents.tools import search_alternative_flights, query_compliance_manual, find_nearest_staff
from core import settings

# --- Rate Limit Handling ---
# FIX: The original code only caught InternalServerError (500).
# Groq's TPM rate limit throws RateLimitError (429), which was never retried.
# We now import and catch BOTH error types.
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from groq import InternalServerError, RateLimitError


def _is_retryable(exception: BaseException) -> bool:
    """Returns True for both 500 server errors and 429 rate limit errors."""
    return isinstance(exception, (InternalServerError, RateLimitError))


@retry(
    stop=stop_after_attempt(5),
    # FIX: Increased min wait to 8 seconds.
    # Groq's error message says "Please try again in 7.5s".
    # The original min=2 was too short and retries would fail again immediately.
    wait=wait_exponential(multiplier=2, min=8, max=60),
    retry=retry_if_exception_type((InternalServerError, RateLimitError)),
    reraise=True
)
def invoke_with_backoff(agent, state):
    """
    Executes the agent and automatically spaces out retries if Groq is
    over capacity (500) OR if the TPM rate limit is hit (429).
    """
    return agent.invoke(state)


# --- LLM Initialization ---
# NOTE: llama-3.1-8b-instant has a 6,000 TPM limit on the free tier.
# If you are hitting this frequently, consider:
#   1. Upgrading to Groq Dev Tier for higher limits
#   2. Switching to "llama3-70b-8192" which has a separate quota pool
#   3. Adding a top-level rate limiter before the agents are called
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=settings.groq_api_key
)


# --- Sub-Agent Definitions ---
# FIX: These were duplicated in supervisor.py. Sub-agents should ONLY live here.
# supervisor.py should import these node functions, not redefine the agents.

logistics_agent = create_agent(
    model=llm,
    tools=[search_alternative_flights],
    system_prompt=(
        "You are the Senior Logistics Router. Find transport for packages. "
        "WARNING: If Compliance bans Air Freight, you MUST NOT suggest a flight. "
        "You must state that Ground Transport is required."
    )
)

compliance_agent = create_agent(
    model=llm,
    tools=[query_compliance_manual],
    system_prompt=(
        "You are the Chief Compliance Officer. Whenever a package is damaged, "
        "you MUST use the query_compliance_manual tool. Analyze the manual against "
        "the package contents. Write a clear directive explaining exactly what must "
        "be done to comply with regulations."
    )
)

dispatch_agent = create_agent(
    model=llm,
    tools=[find_nearest_staff],
    system_prompt=(
        "You are Ground Dispatch. Read the solutions proposed by Logistics and Compliance. "
        "Use your tool to find personnel, and generate a final execution order detailing "
        "exactly who is doing what, and what safety equipment they need."
    )
)


# --- Node Functions (called by the LangGraph supervisor graph) ---

def logistics_node(state: LogisticsState) -> Command[Literal["supervisor"]]:
    result = invoke_with_backoff(logistics_agent, state)
    return Command(
        update={"messages": [result["messages"][-1]]},
        goto="supervisor"
    )


def compliance_node(state: LogisticsState) -> Command[Literal["supervisor"]]:
    result = invoke_with_backoff(compliance_agent, state)
    return Command(
        update={"messages": [result["messages"][-1]]},
        goto="supervisor"
    )


def dispatch_node(state: LogisticsState) -> Command[Literal["supervisor"]]:
    # FIX: Removed the duplicate assignment `result = result = ...`
    result = invoke_with_backoff(dispatch_agent, state)
    return Command(
        update={
            "messages": [result["messages"][-1]],
            "resolution_status": "staff_dispatched"
        },
        goto="supervisor"
    )