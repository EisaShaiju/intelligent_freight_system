import json
import requests
from kafka import KafkaConsumer
from core.config import settings

consumer = KafkaConsumer(
    settings.kafka_topic_anomalies,
    bootstrap_servers=[settings.kafka_broker_url],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

TRIGGER_URL = f"http://localhost:{settings.port}/api/v1/orchestrator/trigger"

print(f"Consumer monitoring topic: {settings.kafka_topic_anomalies}...")

for message in consumer:
    event_data = message.value
    metrics = event_data["telemetry"]
    
    anomaly_type = None
    if metrics["temperature_c"] > 35.0:
        anomaly_type = "CRITICAL_THERMAL_EXCURSION"
    elif metrics["vibration_g"] > 4.5:
        anomaly_type = "EXCESSIVE_MECHANICAL_SHOCK"
        
    if anomaly_type:
        print(f"\n ANOMALY DETECTED: {anomaly_type}. Routing context to LangGraph Orchestrator...")
        
        api_payload = {
            "package_id": event_data["package_id"],
            "current_location": event_data["current_location"],
            "anomaly_type": anomaly_type
        }
        
        try:
            response = requests.post(TRIGGER_URL, json=api_payload)
            if response.status_code == 200:
                print(f" LangGraph Action Plan: {response.json().get('final_action_taken')}")
        except Exception as e:
            print(f" Failed to reach orchestrator node: {e}")