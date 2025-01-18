import streamlit as st
from streamlit.components.v1 import iframe
import threading
from flask import Flask
from flask_socketio import SocketIO

# Flask-SocketIO server setup
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(flask_app, cors_allowed_origins="*")

# Launch Flask-SocketIO in a separate thread
def run_flask():
    socketio.run(flask_app, host="0.0.0.0", port=5000)

# Start the Flask server in a thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Streamlit Interface
st.title("Streamlit Video Conferencing")
st.markdown(
    "This is a video conferencing app deployed using **Streamlit** and **Flask-SocketIO**."
)

st.subheader("Video Conferencing UI")
st.write("The UI is served using an embedded iframe. Use the buttons below for actions.")

iframe("http://localhost:5000", height=800, scrolling=True)
