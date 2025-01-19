from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import random

def compress_frame(frame):
    height, width = frame.shape[:2]
    max_width = 640
    if width > max_width:
        ratio = max_width / width
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    return buffer

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
    rooms[room_id] = {'host': request.sid, 'participants': {request.sid: name}}
    join_room(room_id)
    emit('room_created', {'room_id': room_id})

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    name = data['name']
    if room_id not in rooms:
        emit('error', {'message': 'Room does not exist.'})
        return
    join_room(room_id)
    rooms[room_id]['participants'][request.sid] = name
    # Envoyer un événement de confirmation
    emit('joined_room', {'room_id': room_id, 'name': name})

    # Envoyer les messages existants à l'utilisateur qui rejoint
    previous_messages = rooms[room_id].get('messages', [])
    emit('joined_room', {'room_id': room_id, 'name': name})
    emit('participant_joined', {'name': name}, to=room_id)
    emit('previous_messages', previous_messages, room=request.sid)

@socketio.on('video_frame')
def handle_video_frame(data):
    room_id = data['room_id']
    if request.sid == rooms[room_id]['host']:
        emit('video_frame', {'frame': data['frame']}, to=room_id, include_self=False)

@socketio.on('send_message')
def handle_send_message(data):
    room_id = data['room_id']
    message = data['message']
    name = rooms[room_id]['participants'].get(request.sid, 'Anonymous')
    # Enregistrer le message dans la liste des messages de la salle
    rooms[room_id].setdefault('messages', []).append({'name': name, 'message': message})
    emit('receive_message', {'name': name, 'message': message}, to=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    for room_id, room in rooms.items():
        if request.sid in room['participants']:
            name = room['participants'].pop(request.sid, None)
            emit('participant_left', {'name': name}, to=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
