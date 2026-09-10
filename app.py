import cv2
import numpy as np
from flask import Flask, render_template, Response

app = Flask(__name__)

# Load OpenCV pre-trained Face Detection Cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.py'
)

def detect_mask(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    for (x, y, w, h) in faces:
        # Extract the Lower Half of the Face (where a mask would be)
        lower_face_roi = frame[y + int(h * 0.5): y + h, x: x + w]
        
        # Convert ROI to HSV color space to estimate mask presence
        # Masks usually cover skin color or introduce uniform color blocks/textures
        hsv_roi = cv2.cvtColor(lower_face_roi, cv2.COLOR_BGR2HSV)
        
        # Calculate skin color mask in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv_roi, lower_skin, upper_skin)
        
        # Ratio of detected skin area in lower face
        skin_ratio = np.sum(skin_mask > 0) / (lower_face_roi.shape[0] * lower_face_roi.shape[1] + 1e-5)

        # Heuristic detection: if skin ratio on lower face is low, a mask is likely present
        if skin_ratio < 0.35:
            label = "Mask Detected"
            color = (0, 255, 0)  # Green
        else:
            label = "No Mask Detected"
            color = (0, 0, 255)  # Red

        # Draw rectangle and label around the detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return frame

def generate_frames():
    # Capture webcam video (0 is default camera)
    camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Apply Mask Detection
            processed_frame = detect_mask(frame)
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()

            # Yield frame in byte format for HTTP streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)