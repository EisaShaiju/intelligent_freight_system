# mock_services/flight_api.py
import requests

def fetch_live_route_telemetry(flight_callsign: str = "AAL123") -> dict:
    """
    Fetches real aviation tracking arrays or provides high-fidelity route vectors.
    """
    try:
        # Example using the free OpenSky Network public API
        # Target bounding box covering active commercial corridors
        url = "https://opensky-network.org/api/states/all"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            states = response.json().get("states", [])
            # Search for a live plane or fall back to an active flight vector
            for flight in states[:10]:  # Scan top aircraft vectors
                return {
                    "callsign": flight[1].strip(),
                    "longitude": flight[5],
                    "latitude": flight[6],
                    "altitude_m": flight[7] or 10000.0,
                    "velocity_ms": flight[9] or 240.0
                }
    except Exception:
        pass

    # Fallback sector matrix for Mongolia to USA routing profiles
    return {
        "callsign": flight_callsign,
        "longitude": 106.9173,  # Regional sector coordinate
        "latitude": 47.9188,
        "altitude_m": 10668.0,
        "velocity_ms": 245.5
    }