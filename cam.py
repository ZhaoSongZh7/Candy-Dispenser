import math
import cv2
import mediapipe as mp
from gpiozero import AngularServo
from time import sleep

servo = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

def set_angle(angle):
    servo.angle = angle
    sleep(1)


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)
cap = cv2.VideoCapture(0)

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


            if abs(middle_finger_mcp.x - index_finger_mcp.x) < 0.04:  # Adjust this threshold based on your camera setup
                cv2.putText(frame, 'Get Closer', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                set_angle(0)
            elif avg_distance < 0.3:  # Adjust this threshold if needed
                set_angle(0)
                cv2.putText(frame, 'Closed Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(frame, 'Open Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                set_angle(180)

    cv2.imshow("Candy Dispenser Hand Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
