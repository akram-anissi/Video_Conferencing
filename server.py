from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import base64
import numpy as np
import zlib
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def handle_create_room(data):
    room_id = str(random.randint(1000, 9999))
    name = data['name']
    rooms[room_id] = {'participants': {request.sid: name}}
    join_room(room_id)
    emit('room_created', {'room_id': room_id})
    emit('joined_room', {'room_id': room_id, 'name': name})

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    name = data['name']
    if room_id not in rooms:
        emit('error', {'message': 'Room does not exist.'})
        return
    join_room(room_id)
    rooms[room_id]['participants'][request.sid] = name
    emit('joined_room', {'room_id': room_id, 'name': name})
    emit('participant_joined', {'name': name}, to=room_id)

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data['room_id']
    leave_room(room_id)
    if room_id in rooms:
        name = rooms[room_id]['participants'].pop(request.sid, None)
        emit('participant_left', {'name': name}, to=room_id)

@socketio.on('video_frame')
def handle_video_frame(data):
    room_id = data['room_id']
    frame_data = zlib.decompress(base64.b64decode(data['frame']))
    emit('video_frame', {'frame': frame_data}, to=room_id, include_self=False)

@socketio.on('audio_frame')
def handle_audio_frame(data):
    room_id = data['room_id']
    emit('audio_frame', data, to=room_id, include_self=False)

@socketio.on('chat_message')
def handle_chat_message(data):
    room_id = data['room_id']
    name = rooms[room_id]['participants'].get(request.sid, 'Unknown')
    message = data['message']
    emit('chat_message', {'name': name, 'message': message}, to=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    for room_id, room in rooms.items():
        if request.sid in room['participants']:
            name = room['participants'].pop(request.sid, None)
            emit('participant_left', {'name': name}, to=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
