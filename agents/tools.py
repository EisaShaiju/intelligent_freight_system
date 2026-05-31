from langchain_core.tools import tool

@tool
def search_alternative_flights(current_location: str, destination: str) -> str:
    """Tool to find the next available cargo space for delayed routing."""
    # In a real app, this would make an HTTP request to your flight API
    return f"Found flight BA123 leaving {current_location} with available cargo capacity."

@tool
def check_baggage_guidelines(anomaly_type: str) -> str:
    """Tool to get compliance and safety rules for damaged packaging."""
    return "Protocol 42A: Require heavy-duty reinforced tape and supervisor sign-off."

@tool
def find_nearest_staff(location: str) -> str:
    """Tool to query the HR/Roster API for available ground staff."""
    return f"Agent Sarah is currently on active shift near {location}."