import math
import cv2
import mediapipe as mp
from gpiozero import AngularServo
from time import sleep

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)
cap = cv2.VideoCapture(0)
servo = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
lastAngle = 0
currentAngle = 0
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 300)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)

def set_angle(angle):
    servo.angle = angle
  

def euclidean_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.z - point2.z) ** 2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Camera Error")
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            pinkie_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

            fingertips = [
                hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            ]

            distances = [euclidean_distance(wrist, tip) for tip in fingertips]

            avg_distance = sum(distances) / len(distances)
            # Distance check for "Get Closer"
            print("Middle Finger X: " + str(middle_finger_mcp.x))
            print("Index Finger X: " + str(index_finger_mcp.x))
            print("Abs Value X Distance: " + str(abs(middle_finger_mcp.x - index_finger_mcp.x)))
            print("Abs Value Y Distance: " + str(abs(fingertips[4].y - pinkie_finger_mcp.y)))
            if abs(fingertips[4].y - pinkie_finger_mcp.y) >= 0.14:
                currentAngle = 180
                cv2.putText(frame, 'Open Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if abs(middle_finger_mcp.x - index_finger_mcp.x) < 0.04:  # Adjust this threshold based on your camera setup
                cv2.putText(frame, 'Get Closer', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                currentAngle = 0
            elif abs(fingertips[4].y - pinkie_finger_mcp.y) < 0.14:  # Adjust this threshold if needed
                currentAngle = 0
                cv2.putText(frame, 'Closed Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                currentAngle = 0
                #currentAngle = 180
                #cv2.putText(frame, 'Open Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)   

    sleep(0.1)
    cv2.imshow("Candy Dispenser Hand Camera", frame)
    
    if (lastAngle != currentAngle):
        set_angle(currentAngle)
       
        lastAngle = currentAngle
    #currentAngle = 0
    #set_angle(currentAngle)

    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
