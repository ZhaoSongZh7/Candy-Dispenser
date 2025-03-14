import math
import cv2
import mediapipe as mp
import time
# variable is now module
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)

# open cam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Camera Error")

    # makes into rgb
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detects the hand movement
    results = hands.process(frame_rgb)

    # this draws the hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            thumb_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            
            middletip_y = middle_finger_tip.y
            indextip_y = index_finger_tip.y
            ringtip_y = ring_finger_tip.y
            pinkytip_y = pinky_finger_tip.y
            thumbtip_y = thumb_finger_tip.y
            

            middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            ring_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
            pinky_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
            thumb_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]


            middlemcp_y = middle_finger_mcp.y
            indexmcp_y = index_finger_mcp.y
            ringmcp_y = ring_finger_mcp.y
            pinkymcp_y = pinky_finger_mcp.y
            thumbmcp_y = thumb_finger_mcp.y

            mdistance = middletip_y - middlemcp_y
            idistance = indextip_y - indexmcp_y
            rdistance = ringtip_y - ringmcp_y
            pdistance = pinkytip_y - pinkymcp_y
            tdistance = thumbtip_y - thumbmcp_y

            total = mdistance + idistance + rdistance + pdistance + tdistance

            if total > 0:
                cv2.putText(frame, 'Closed Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(frame, 'Open Palm', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            

    # Display the frame the string is the title
    cv2.imshow("Candy Dispenser Hand Camera", frame)

    # press space to exit
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break
cap.release()
cv2.destroyAllWindows()
