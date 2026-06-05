import time
import json
import random
from kafka import KafkaProducer
from core.config import settings
from mock_services.flight_api import fetch_live_route_telemetry

producer = KafkaProducer(
    bootstrap_servers=[settings.kafka_broker_url],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def start_telemetry_stream():
    print(f"Pumping sensor arrays to Kafka broker at {settings.kafka_broker_url}...")
    package_id = "PKG-MONGOLIA-USA-2026"
    
    while True:
        # 1. Capture real aircraft positional telemetry
        flight_data = fetch_live_route_telemetry()
        
        # 2. Simulate package-level environment metrics
        # Introduce a 5% chance of an unexpected anomaly trip point
        is_anomaly = random.random() < 0.05
        
        payload = {
            "package_id": package_id,
            "current_location": f"LAT:{flight_data['latitude']}, LON:{flight_data['longitude']}",
            "flight_meta": {
                "callsign": flight_data["callsign"],
                "velocity_knots": round(flight_data["velocity_ms"] * 1.94384, 1)
            },
            "telemetry": {
                "temperature_c": round(random.uniform(40.0, 45.0) if is_anomaly else random.uniform(18.0, 22.0), 1),
                "vibration_g": round(random.uniform(5.0, 7.5) if is_anomaly and random.random() > 0.5 else 1.0, 2)
            }
        }
        
        producer.send(settings.kafka_topic_anomalies, payload)
        print(f"Streamed telemetry context for: {package_id}")
        time.sleep(3)

if __name__ == "__main__":
    start_telemetry_stream()