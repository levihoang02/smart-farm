import socketio

class SocketService:
    def __init__(self, server_url):
        # Initialize a Socket.IO client
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        # Connect to the Flask server
        self.sio.connect(server_url)
        print("Connected to the server.")

    def emit_data(self, event_name, data):
        # Emit data to the Flask server
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        self.sio.emit(event_name, data)
        print(f"Emitted data: {data}")

    def close_connection(self):
        # Disconnect the Socket.IO client
        self.sio.disconnect()
        print("Disconnected from the server.")