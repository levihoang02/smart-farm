import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    KAFKA_TOPIC = os.getenv("KAFKA-TOPIC")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID")
    SOCKET_URL = os.getenv('SOCKET_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    TOKEN = os.getenv('TOKEN')
    