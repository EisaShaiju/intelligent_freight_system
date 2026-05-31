import json
import sys
from confluent_kafka import Consumer, KafkaError, KafkaException
from core import settings, logger

# Import the LangGraph workflow
from agents.supervisor import orchestrator_app

def start_consumer():
    """Starts the Kafka consumer to listen for anomalies and trigger agents."""
    consumer_config = {
        'bootstrap.servers': settings.kafka_broker_url,
        'group.id': 'orchestrator-worker-group',
        'auto.offset.reset': 'earliest' # Start reading from the earliest unread message
    }
    
    consumer = Consumer(consumer_config)
    consumer.subscribe([settings.kafka_topic_anomalies])
    
    logger.info(f"Started Kafka consumer. Listening on topic: {settings.kafka_topic_anomalies}")
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    logger.debug(f"{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Successfully received a message
                raw_data = msg.value().decode('utf-8')
                logger.info(f"Received anomaly event: {raw_data}")
                
                # Parse the JSON payload
                event_data = json.loads(raw_data)
                
                # Construct the initial state for the LangGraph agents
                initial_state = {
                    "package_id": event_data["package_id"],
                    "current_location": event_data["current_location"],
                    "anomaly_type": event_data["anomaly_type"],
                    "resolution_status": "pending",
                    "messages": [("user", f"Anomaly detected: {event_data['anomaly_type']} for package {event_data['package_id']} at {event_data['current_location']}. Please resolve.")]
                }
                
                # Trigger the multi-agent workflow
                logger.info(f"Triggering LangGraph orchestration for {event_data['package_id']}...")
                
                # Stream the agent thoughts in real-time to the console
                for chunk in orchestrator_app.stream(initial_state, stream_mode="updates"):
                    logger.debug(f"Agent Update: {chunk}")
                    
                logger.info(f"Resolution complete for {event_data['package_id']}.")
                
    except KeyboardInterrupt:
        logger.info("Consumer shutdown requested by user.")
    except Exception as e:
        logger.error(f"Consumer encountered a fatal error: {str(e)}")
    finally:
        # Close down consumer to commit final offsets
        consumer.close()
        logger.info("Kafka consumer closed.")

if __name__ == "__main__":
    start_consumer()