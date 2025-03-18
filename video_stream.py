from ipSearch import find_valid_rtsp_ip
from flask import Flask, Response
import cv2

app = Flask(__name__)

def generate_frames():
    cap = cv2.VideoCapture(0)  # Capture depuis la webcam
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Renvoie le flux vidéo en local."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    ip = find_valid_rtsp_ip()
    rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/101" 
    app.run(host="127.0.0.1", port=5000, debug=True)  # Local seulement
