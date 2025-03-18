import gpiod
import time
import cv2
import mediapipe as mp

# Setup GPIO for PWM (Assuming PWM chip 0, line 0)
PWM_CHIP = 0  # Might need to change based on your system
PWM_LINE = 0  # Corresponds to /sys/class/pwm/pwmchip0/pwm0

# Initialize GPIO PWM
chip = gpiod.Chip(f'/dev/gpiochip{PWM_CHIP}')
line = chip.get_line(PWM_LINE)
line.request(consumer="servo", type=gpiod.LINE_REQ_DIR_OUT)

# Function to move servo
def move_servo(angle):
    min_pulse = 1000000  # 1.0ms (0 degrees)
    max_pulse = 2000000  # 2.0ms (180 degrees)
    pulse_width = min_pulse + (angle / 180.0) * (max_pulse - min_pulse)
    with open(f"/sys/class/pwm/pwmchip{PWM_CHIP}/pwm{PWM_LINE}/duty_cycle", "w") as f:
        f.write(str(int(pulse_width)))

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)

cap = cv2.VideoCapture(0)

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
            fingertips = [
                hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            ]

            avg_distance = sum([(wrist.x - tip.x) ** 2 + (wrist.y - tip.y) ** 2 for tip in fingertips]) ** 0.5

            if avg_distance > 0.3:  # Open Palm
                cv2.putText(frame, 'Open Palm - Dispensing Candy', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                move_servo(90)  # Move servo to dispense
                time.sleep(1)  # Hold position for 1s
                move_servo(0)   # Return to original position

            else:
                cv2.putText(frame, 'Closed Palm - No Candy', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Candy Dispenser Hand Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
