from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
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
        token = request.cookies.get('token')
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return f(*args, **kwargs)
        except:
            return jsonify({"message": "Token is invalid"}), 401
    return decorated

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "expose_headers": ["Content-Type", "Authorization"]
     }})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5500')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
        token = jwt.encode(
            {'user': data['username']}, 
            SECRET_KEY, 
            algorithm="HS256"
        )
        response = jsonify({'status': 'success', 'message': 'Login successful', 'token': token})
        return response, 200
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    response = jsonify({'status': 'success', 'message': 'Logged out successfully'})
    response.delete_cookie('token')
    return response, 200

@socketio.on('connect')
def handle_connect():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print("No token found")
        return False
    
    token = auth_header.split(' ')[1]
    try:
        # Verify token and join authenticated room
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        socketio.server.enter_room(request.sid, 'authenticated_users')
        return True
    except:
        return False

# Event to receive Kafka data and broadcast to clients
@socketio.on('kafka_data')
def handle_kafka_data(json_data):
    print(f"Broadcasting data: {json_data}")
    socketio.emit('sensor_data', json_data)  # Send to front end

# Start the Flask server with Socket.IO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
