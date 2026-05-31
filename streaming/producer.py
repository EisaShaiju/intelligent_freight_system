import json
import argparse
from confluent_kafka import Producer
from core import settings, logger

def delivery_report(err, msg):
    """Callback triggered by Kafka to confirm message delivery."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_anomaly_event(package_id: str, anomaly_type: str, location: str):
    """Constructs and sends an anomaly event to the Kafka topic."""
    producer_config = {
        'bootstrap.servers': settings.kafka_broker_url
    }
    
    producer = Producer(producer_config)
    
    # Construct the payload matching our API schemas and Agent State
    event_payload = {
        "package_id": package_id,
        "anomaly_type": anomaly_type,
        "current_location": location
    }
    
    logger.info(f"Producing event: {event_payload}")
    
    # Send the message to Kafka
    producer.produce(
        topic=settings.kafka_topic_anomalies,
        key=package_id.encode('utf-8'),
        value=json.dumps(event_payload).encode('utf-8'),
        callback=delivery_report
    )
    
    # Wait for any outstanding messages to be delivered
    producer.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a logistics anomaly scan.")
    parser.add_argument("--package_id", type=str, required=True, help="ID of the package (e.g., PKG-123)")
    parser.add_argument("--type", type=str, required=True, help="Type of anomaly (e.g., missed_connection, damaged)")
    parser.add_argument("--location", type=str, default="LHR-Terminal-5", help="Current scan location")
    
    args = parser.parse_args()
    produce_anomaly_event(args.package_id, args.type, args.location)