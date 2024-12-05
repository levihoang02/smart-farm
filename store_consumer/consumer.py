from kafka import KafkaConsumer
from utils.config import Config
import json
from services.compression import TimeSeriesCompressor
from datetime import datetime, timedelta

config = Config()

compressor = TimeSeriesCompressor('data.csv', 'omp')

class StoreConsumer:
    def __init__(self, interval = timedelta(hours=12)):
        self.consumer = KafkaConsumer(
            config.KAFKA_TOPIC,
            bootstrap_servers=config.KAFKA_BROKERS_EXTERNAL,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id=config.KAFKA_GROUP_ID,
            enable_auto_commit=True
        )
        self.temp_batch = []
        self.humid_batch = []
        self.timestamp_batch = []
        self.interval = interval
        self.last_run = datetime.now()
        
    def consumer_message(self):
        try:
            print("Starting to consume messages...")
            while True:
                for message in self.consumer:
                    data = message.value
                    if(datetime.now() - self.last_run < self.interval):
                        self.patch.append(data)
                        continue
                    else:
                        
                        continue
                     
        except Exception as e:
            print(f"Error processing message: {e}")
            raise e
    def stop_consuming(self) -> None:
        self.consumer.close()
        print("Stream consumer stopped")
            
if __name__ == "__main__":
    mse, ratio = compressor.run_compression()
    print("MSE: ", mse)
    print("Ratio: ", ratio)