import time
import json
import random
import uuid
import requests
import math
from datetime import datetime, timezone
from kafka import KafkaProducer
from core.config import settings
from core.db import supabase

# 1. Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=[settings.kafka_broker_url],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3,5,0)
)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in km between two GPS coordinates (Haversine formula)."""
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_live_flights(icao24_list=None):
    """Fetches flight data from OpenSky. If icao24_list is provided, filters for those flights."""
    url = "https://opensky-network.org/api/states/all"
    if icao24_list:
        # Append filter parameters to only ask for our specific 20 flights
        url += "?" + "&".join([f"icao24={icao}" for icao in icao24_list])
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("states", [])
    except Exception as e:
        print(f"OpenSky API Warning: {e}")
    return []

def start_telemetry_batch():
    """Manages the 10-minute lifecycle of 20 tracked packages."""
    print(f" Initializing Stateful Producer Pipeline...")
    
    while True:
        print("\n---  STARTING NEW 10-MINUTE BATCH ---")
        # Step 1: Initialization - Grab up to 20 active flights
        states = get_live_flights()
        if not states:
            print(" OpenSky API rate limited. Retrying in 30 seconds...")
            time.sleep(30)
            continue
            
        active_packages = {}
        
        # Pick the top 20 active flights that have valid lat/lon coordinates
        valid_flights = [f for f in states if f[5] is not None and f[6] is not None][:20]
        
        for flight in valid_flights:
            pkg_id = f"PKG-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:6].upper()}"
            active_packages[flight[0]] = { # Keyed by icao24 address
                "package_id": pkg_id,
                "callsign": flight[1].strip() if flight[1] else "UNKNOWN",
                "start_lat": flight[6],
                "start_lon": flight[5],
                "last_lat": flight[6],
                "last_lon": flight[5],
                "distance_km": 0.0
            }
            
            # Write the initial state to Supabase
            try:
                supabase.table("tracked_packages").upsert({
                    "package_id": pkg_id,
                    "flight_icao24": flight[0],
                    "latitude": flight[6],
                    "longitude": flight[5],
                    "altitude": flight[7] or 10000.0,
                    "anomaly_detected": False,
                    "resolution_summary": "IN_TRANSIT"
                }).execute()
            except Exception as e:
                print(f"Supabase write error on init: {e}")

        print(f" Registered {len(active_packages)} packages in Supabase. Streaming telemetry...")

        # Step 2: Streaming Phase (Loop for 10 minutes -> 20 iterations of 30 seconds)
        icao24_targets = list(active_packages.keys())
        
        for iteration in range(20):
            print(f" Tick {iteration + 1}/20 - Polling flight telemetry...")
            live_updates = get_live_flights(icao24_targets)
            
            for flight in live_updates:
                icao = flight[0]
                if icao in active_packages:
                    pkg = active_packages[icao]
                    
                    # Ensure coordinates are valid
                    current_lon, current_lat = flight[5], flight[6]
                    if current_lon is None or current_lat is None:
                        current_lon, current_lat = pkg["last_lon"], pkg["last_lat"]
                    
                    # Update distance mathematically
                    segment_dist = calculate_distance(pkg["last_lat"], pkg["last_lon"], current_lat, current_lon)
                    pkg["distance_km"] += segment_dist
                    pkg["last_lat"] = current_lat
                    pkg["last_lon"] = current_lon
                    
                    # Simulate thermal or vibration anomalies (2% chance per tick)
                    is_anomaly = random.random() < 0.02
                    
                    payload = {
                        "package_id": pkg["package_id"],
                        "flight_icao24": icao,
                        "current_location": f"LAT:{current_lat}, LON:{current_lon}",
                        "distance_km": round(pkg["distance_km"], 2),
                        "telemetry": {
                            "latitude": current_lat,
                            "longitude": current_lon,
                            "altitude_m": flight[7] or 10000.0,
                            "velocity_ms": flight[9] or 240.0,
                            "temperature_c": round(random.uniform(40.0, 45.0) if is_anomaly else random.uniform(18.0, 22.0), 1),
                            "vibration_g": round(random.uniform(5.0, 7.5) if is_anomaly else 1.0, 2)
                        }
                    }
                    
                    # Push to Kafka Topic
                    producer.send(settings.kafka_topic_anomalies, payload)
            
            # Wait 30 seconds before next API pull to respect rate limits
            time.sleep(30)

        # Step 3: Rotation Phase (10 minutes elapsed)
        print(" 10-Minute cycle complete. Archiving batch...")
        for pkg in active_packages.values():
            try:
                # We only overwrite it if an anomaly hasn't already been detected by LangGraph
                supabase.table("tracked_packages").update({
                    "resolution_summary": "COMPLETED - Safely Arrived"
                }).eq("package_id", pkg["package_id"]).eq("anomaly_detected", False).execute()
            except Exception:
                pass

if __name__ == "__main__":
    start_telemetry_batch()