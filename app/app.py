from flask import Flask
from flask_socketio import SocketIO, emit
from gevent import monkey
monkey.patch_all()

from services.decompression import TimeSeriesDecompressor
from pyspark.sql import SparkSession
from datetime import datetime

spark = SparkSession.builder \
    .appName("TimeSeriesAnalysis") \
    .getOrCreate()

def calculate_average_with_spark(data):
    # Convert data to Spark DataFrame
    df = spark.createDataFrame(data, ["temperature", "humidity"])
    
    # Calculate average
    avg_df = df.groupBy().avg("temperature", "humidity").collect()
    
    # Extract results
    avg_temp = avg_df[0]["avg(temperature)"]
    avg_humid = avg_df[0]["avg(humidity)"]

    return {"average_temperature": avg_temp, "average_humidity": avg_humid}

def decompress_data(data):
    decompressor = TimeSeriesDecompressor()
    decompressed_data = decompressor.decompress(data)
    return decompressed_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, 
                    cors_allowed_origins="*",
                    async_mode='gevent',  # Specify async mode
                    logger=True,  # Enable logging
                    engineio_logger=True)

# Route to check if server is running
@app.route('/')
def index():
    return "Flask server is running."

# Event to receive Kafka data and broadcast to clients
@socketio.on('kafka_data')
def handle_kafka_data(json_data):
    print(f"Broadcasting data: {json_data}")
    socketio.emit('sensor_data', json_data)  # Send to front end

# Start the Flask server with Socket.IO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
