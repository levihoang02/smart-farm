from kafka import KafkaConsumer
from utils.config import Config
import json
from socket_service import SocketService
from utils.converting import convert_to_json
config = Config()

socket_service = SocketService(Config.SOCKET_URL, headers={'Authorization': f'Bearer {Config.TOKEN}'})

class StreamConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            config.KAFKA_TOPIC,
            bootstrap_servers=config.KAFKA_BROKERS_EXTERNAL,
            # value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id=config.KAFKA_GROUP_ID,
            enable_auto_commit=True
        )
    def stream_messages(self):
        try:
            print("Starting to consume messages...")
            while True:
                for message in self.consumer:
                    data = message.value
                    print(type(data))
                    json_string = data.decode('utf-8')
                    value = convert_to_json(json_string)
                    # json_object = json.loads(json_string)
                    socket_service.emit_data('kafka_data', {'data': value})
                    
        except Exception as e:
            print(f"Error processing message: {e}")
            raise e
    def stop_consuming(self) -> None:
        self.consumer.close()
        socket_service.close_connection()
        print("Stream consumer stopped")
            
if __name__ == "__main__":
    print("Starting stream consumer...")
    try:
        stream_consumer = StreamConsumer()
        # Convert the generator to a list to actually consume messages
        stream_consumer.stream_messages()
    except Exception as e:
        print(f"Error in stream consumer: {e}")
        stream_consumer.stop_consuming()
        raise e