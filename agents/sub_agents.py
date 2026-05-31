from typing import Literal
from langchain_openai import ChatOpenAI # Or ChatGoogleGenerativeAI if using Gemini
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from agents.state import LogisticsState
from agents.tools import search_alternative_flights, check_baggage_guidelines, find_nearest_staff

# Initialize your LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Define the Agents ---
logistics_agent = create_react_agent(
    llm, 
    tools=[search_alternative_flights],
    prompt="You are a logistics routing expert. Analyze delays and find alternative flight schedules."
)

compliance_agent = create_react_agent(
    llm, 
    tools=[check_baggage_guidelines],
    prompt="You handle damaged or non-compliant packaging protocols. Provide exact instructions for repackaging."
)

dispatch_agent = create_react_agent(
    llm, 
    tools=[find_nearest_staff],
    prompt="You are HR dispatch. Find available ground staff and generate a clear dispatch instruction based on the solution."
)

# --- Define the Node Functions ---
# Notice how every node returns Command(goto="supervisor") to hand control back

def logistics_node(state: LogisticsState) -> Command[Literal["supervisor"]]:
    result = logistics_agent.invoke(state)
    return Command(
        update={"messages": [result["messages"][-1]]},
        goto="supervisor"
    )

def compliance_node(state: LogisticsState) -> Command[Literal["supervisor"]]:
    result = compliance_agent.invoke(state)
    return Command(
        update={"messages": [result["messages"][-1]]},
        goto="supervisor"
    )

def dispatch_node(state: LogisticsState) -> Command[Literal["supervisor"]]:
    result = dispatch_agent.invoke(state)
    return Command(
        update={"messages": [result["messages"][-1]]},
        update={"resolution_status": "staff_dispatched"}, # Update custom state fields too!
        goto="supervisor"
    )