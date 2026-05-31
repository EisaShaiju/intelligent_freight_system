import random
from datetime import datetime, timedelta

def get_alternative_flights(current_location: str, destination: str = "Any") -> dict:
    """
    Simulates querying an airline's flight schedule database for alternative routing.
    Returns a structured dictionary mocking a JSON API response.
    """
    # Generate mock departure times based on the current time
    now = datetime.now()
    
    mock_flights = [
        {
            "flight_number": f"FL-{random.randint(1000, 9999)}",
            "departure": current_location,
            "destination": destination if destination != "Any" else "LHR",
            "departure_time": (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "available_cargo_kg": random.choice([50, 500, 1200]),
            "status": "On Time"
        },
        {
            "flight_number": f"FL-{random.randint(1000, 9999)}",
            "departure": current_location,
            "destination": "DXB",
            "departure_time": (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "available_cargo_kg": random.choice([0, 200, 800]),
            "status": "Delayed"
        }
    ]
    
    return {
        "status": 200,
        "source": "Mock Airline Scheduling System",
        "data": mock_flights
    }