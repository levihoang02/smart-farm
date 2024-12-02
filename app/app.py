from flask import Flask
from flask_socketio import SocketIO, emit
from gevent import monkey
monkey.patch_all()

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
