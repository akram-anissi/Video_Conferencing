import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

const VideoConference = () => {
  const [roomId, setRoomId] = useState('');
  const [messages, setMessages] = useState([]);
  const [localStream, setLocalStream] = useState(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isMicOn, setIsMicOn] = useState(false);
  const videoRef = useRef(null);
  const socket = useRef(io('http://localhost:5000'));

  useEffect(() => {
    socket.current.on('video_frame', (data) => {
      if (videoRef.current) {
        const img = new Image();
        const ctx = videoRef.current.getContext('2d');
        img.onload = () => ctx.drawImage(img, 0, 0, videoRef.current.width, videoRef.current.height);
        img.src = data.frame;
      }
    });

    socket.current.on('chat_message', (data) => {
      setMessages((prevMessages) => [...prevMessages, data]);
    });

    return () => socket.current.disconnect();
  }, []);

  const createRoom = () => {
    socket.current.emit('create_room', { room_id: roomId });
  };

  const joinRoom = () => {
    socket.current.emit('join_room', { room_id: roomId });
  };

  const toggleCamera = async () => {
    if (!localStream) {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setLocalStream(stream);
      setIsCameraOn(true);
    } else {
      const videoTrack = localStream.getVideoTracks()[0];
      videoTrack.enabled = !videoTrack.enabled;
      setIsCameraOn(videoTrack.enabled);
    }
  };

  const toggleMicrophone = async () => {
    if (!localStream) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setLocalStream(stream);
      setIsMicOn(true);
    } else {
      const audioTrack = localStream.getAudioTracks()[0];
      audioTrack.enabled = !audioTrack.enabled;
      setIsMicOn(audioTrack.enabled);
    }
  };

  const sendMessage = (message) => {
    socket.current.emit('chat_message', { room_id: roomId, message });
  };

  return (
    <div className="video-conference">
      <input
        type="text"
        placeholder="Enter Room ID"
        value={roomId}
        onChange={(e) => setRoomId(e.target.value)}
      />
      <button onClick={createRoom}>Create Room</button>
      <button onClick={joinRoom}>Join Room</button>

      <div className="controls">
        <button onClick={toggleCamera}>{isCameraOn ? 'Turn Off Camera' : 'Turn On Camera'}</button>
        <button onClick={toggleMicrophone}>{isMicOn ? 'Mute' : 'Unmute'}</button>
      </div>

      <canvas ref={videoRef} width={640} height={480}></canvas>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index}><strong>{msg.sid}:</strong> {msg.message}</div>
        ))}
        <input
          type="text"
          placeholder="Type a message..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') sendMessage(e.target.value);
          }}
        />
      </div>
    </div>
  );
};

export default VideoConference;
