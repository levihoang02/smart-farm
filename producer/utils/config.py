import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    KAFKA_TOPIC_TEMPERATURE = os.getenv("KAFKA-TOPIC_TEMPERATURE")
    KAFKA_TOPIC_HUMIDITY = os.getenv("KAFKA-TOPIC_HUMIDITY")
    