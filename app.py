import socket
import streamlit as st
from streamlit.components.v1 import iframe
import threading
from flask import Flask
from flask_socketio import SocketIO

# Flask-SocketIO server setup
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(flask_app, cors_allowed_origins="*")


# Function to get the local IP address dynamically
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public DNS server to get the local IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip


# Launch Flask-SocketIO in a separate thread
def run_flask():
    socketio.run(flask_app, host="0.0.0.0", port=5000)


# Start the Flask server in a thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Dynamically embed the Flask app in Streamlit
server_ip = get_local_ip()
iframe(f"http://{server_ip}:5000", height=800, scrolling=True)
