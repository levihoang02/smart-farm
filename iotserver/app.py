from flask import Flask
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/<temperature>/<humidity>')
def send_data(temperature, humidity):
    producer = KafkaProducer(bootstrap_servers='kafka-1:19092,kafka-2:19093,kafka-3:19094')
    data = f'Temperature: {temperature}, Humidity: {humidity}, timestamp: {datetime.now()}'
    producer.send('iot-sensor', data.encode('utf-8'))
    return f'Temperature: {temperature}, Humidity: {humidity}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)