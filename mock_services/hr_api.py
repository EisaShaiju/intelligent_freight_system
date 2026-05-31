import random

def get_available_staff(location: str) -> dict:
    """
    Simulates querying the HR/Roster API for active ground staff in a specific location.
    """
    staff_pool = [
        {"name": "Sarah Connor", "role": "Ground Operations Specialist", "status": "Available", "current_zone": "Terminal 2"},
        {"name": "John Smith", "role": "Baggage Handler", "status": "On Break", "current_zone": "Terminal 1"},
        {"name": "Amit Patel", "role": "Logistics Supervisor", "status": "Available", "current_zone": "Cargo Bay A"},
        {"name": "Elena Rodriguez", "role": "Compliance Officer", "status": "Available", "current_zone": location}
    ]
    
    # Filter for staff who are currently available
    available_staff = [staff for staff in staff_pool if staff["status"] == "Available"]
    
    if available_staff:
        # Simulate picking the most relevant staff member based on location/availability
        selected = random.choice(available_staff)
        return {
            "status": 200,
            "message": "Staff member located successfully.",
            "data": selected
        }
        
    return {
        "status": 404,
        "message": "No available staff found in the requested zone.",
        "data": None
    }