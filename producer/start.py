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
def generate_sensor_data():
    temperature = random.uniform(19, 21)
    humidity = random.uniform(31, 32)
    data = f'Temperature: {temperature}, Humidity: {humidity}, timestamp: {datetime.now()}'
    return data

# Function to send data to Kafka
def send_data(producer, topic, data):
    try:
        producer.produce(topic, value=data.encode('utf-8'))
        producer.flush()  # Ensure the message is sent
        print(f"Sent: {data}")
    except Exception as e:
        print(f"Failed to send message: {e}")

# Simulate data generation
def simulate_sensor_data():
    while True:
        data = generate_sensor_data()
        send_data(producer, config.KAFKA_TOPIC, data)
        time.sleep(5)

# Main entry point
if __name__ == "__main__":
    print("Starting sensor data simulation...")
    try:
        simulate_sensor_data()
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        producer.flush()