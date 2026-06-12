# streaming/consumer.py
import json
import requests
from kafka import KafkaConsumer
from core.config import settings
from core.db import supabase

def start_consumer():
    consumer = KafkaConsumer(
        settings.kafka_topic_anomalies,
        bootstrap_servers=[settings.kafka_broker_url],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        api_version=(3,5,0)
    )

    TRIGGER_URL = f"http://localhost:{settings.port}/api/v1/orchestrator/trigger"

    print(f" Consumer active. Syncing topic '{settings.kafka_topic_anomalies}' to Supabase...")

    for message in consumer:
        event = message.value
        pkg_id = event["package_id"]
        telemetry = event["telemetry"]
        
        # 1. SYNC REAL-TIME TELEMETRY TO DATABASE
        # This powers your frontend/status endpoint to show the plane moving
        try:
            supabase.table("tracked_packages").update({
                "latitude": telemetry["latitude"],
                "longitude": telemetry["longitude"],
                "altitude": telemetry["altitude_m"],
                "distance_traveled_km": event["distance_km"]
            }).eq("package_id", pkg_id).execute()
        except Exception as e:
            print(f" Failed to sync DB for {pkg_id}: {e}")

        # 2. EVALUATE PHYSICAL THRESHOLDS
        anomaly_type = None
        if telemetry["temperature_c"] > 35.0:
            anomaly_type = "CRITICAL_THERMAL_EXCURSION"
        elif telemetry["vibration_g"] > 4.5:
            anomaly_type = "EXCESSIVE_MECHANICAL_SHOCK"

        # 3. TRIGGER LANGGRAPH (IF NEW ANOMALY)
        if anomaly_type:
            try:
                # GUARD CHECK: Have we already dispatched AI for this specific package?
                db_check = supabase.table("tracked_packages").select("anomaly_detected").eq("package_id", pkg_id).execute()
                if db_check.data and db_check.data[0].get("anomaly_detected") is True:
                    continue  # The AI is already handling this. Skip duplicate triggers.
                
                print(f"\n ANOMALY DETECTED [{pkg_id}]: {anomaly_type}")
                print("Routing context to LangGraph Orchestrator...")
                
                # Lock the package immediately so future stream ticks don't re-trigger it
                supabase.table("tracked_packages").update({
                    "anomaly_detected": True,
                    "resolution_summary": "LangGraph Agents Dispatched..."
                }).eq("package_id", pkg_id).execute()

                # Call the FastAPI Endpoint
                api_payload = {
                    "package_id": pkg_id,
                    "current_location": event["current_location"],
                    "anomaly_type": anomaly_type
                }
                
                res = requests.post(TRIGGER_URL, json=api_payload, timeout=30)
                
                # 4. SAVE AI RESOLUTION TO DATABASE
                if res.status_code == 200:
                    plan = res.json().get('final_action_taken')
                    print(f" AI Resolution Plan Drafted! Saving to DB.")
                    
                    supabase.table("tracked_packages").update({
                        "resolution_summary": plan
                    }).eq("package_id", pkg_id).execute()
                else:
                    print(f" API Error {res.status_code}: {res.text}")
                    
            except Exception as e:
                print(f" Failed to reach LangGraph orchestrator: {e}")

if __name__ == "__main__":
    start_consumer()