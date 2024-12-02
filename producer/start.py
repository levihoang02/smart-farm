import json
import random
import time
from datetime import datetime
from confluent_kafka import Producer
from utils.config import Config

config = Config()

# Initialize Kafka Producer
producer = Producer({'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL})

# Function to generate random sensor data
def generate_sensor_data(sensor_id):
    return {
        "sensor_id": sensor_id,
        "type": random.choice(["temperature", "humidity"]),
        "value": round(random.uniform(10.0, 100.0), 2),
        "timestamp": datetime.now().isoformat()
    }

# Function to send data to Kafka
def send_data(producer, topic, data):
    try:
        producer.produce(topic, key=str(data["sensor_id"]), value=json.dumps(data))
        producer.flush()  # Ensure the message is sent
        print(f"Sent: {data}")
    except Exception as e:
        print(f"Failed to send message: {e}")

# Simulate data generation
def simulate_sensor_data():
    sensor_ids = [f"sensor_{i}" for i in range(1, 101)]  # 100 sensors
    while True:
        sensor_id = random.choice(sensor_ids)  # Pick a random sensor
        sensor_data = generate_sensor_data(sensor_id)
        send_data(producer, config.KAFKA_TOPIC, sensor_data)
        time.sleep(5)  # Delay to simulate real-time data generation

# Main entry point
if __name__ == "__main__":
    print("Starting sensor data simulation...")
    try:
        simulate_sensor_data()
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        producer.flush()