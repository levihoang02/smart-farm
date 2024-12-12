from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from gevent import monkey
monkey.patch_all()
import jwt
from datetime import datetime, timedelta
import dotenv
import os
from functools import wraps
dotenv.load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return f(*args, **kwargs)
        except:
            return jsonify({"message": "Token is invalid"}), 401
    return decorated

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, 
                    cors_allowed_origins="*",
                    async_mode='gevent',  # Specify async mode
                    logger=True,  # Enable logging
                    engineio_logger=True)

# Route to check if server is running
@app.route('/')
def index():
    return "Flask server is running."

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data and data.get('username') == 'admin' and data.get('password') == 'password':
        token = jwt.encode({'user': data['username'], 'exp': datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# Event to receive Kafka data and broadcast to clients
@socketio.on('kafka_data')
def handle_kafka_data(json_data):
    print(f"Broadcasting data: {json_data}")
    socketio.emit('sensor_data', json_data)  # Send to front end

# Start the Flask server with Socket.IO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
