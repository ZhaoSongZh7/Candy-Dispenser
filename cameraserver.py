from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
import math
import time

app = Flask(__name__)

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)
cap = cv2.VideoCapture(0)  # Open USB camera

# Set camera resolution (e.g., 640x480 for less computational load)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Function to calculate Euclidean distance
def euclidean_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.z - point2.z) ** 2)

# Function to generate processed video frames
def generate_frames():
    prev_time = time.time()  # Store the previous time to calculate FPS

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

                fingertips = [
                    hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                    hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                    hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                    hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
                    hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                ]

                distances = [euclidean_distance(wrist, tip) for tip in fingertips]
                avg_distance = sum(distances) / len(distances)

                # Debugging output
                print(f"Middle Finger X: {middle_finger_mcp.x}")
                print(f"Index Finger X: {index_finger_mcp.x}")
                print(f"Abs Value X Distance: {abs(middle_finger_mcp.x - index_finger_mcp.x)}")

                # Display text based on hand position
                if abs(middle_finger_mcp.x - index_finger_mcp.x) < 0.04:
                    cv2.putText(frame, 'Get Closer', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                elif avg_distance < 0.3:
                    cv2.putText(frame, 'Closed Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, 'Open Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        # Display FPS on the frame
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Flask routes
@app.route('/')
def index():
   return '''
    <html>
        <head><title>Hand Tracking Stream</title></head>
        <body>
            <h1>Hand Tracking Live Stream</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
