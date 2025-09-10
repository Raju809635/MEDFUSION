import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def detect_gesture():
    """
    Opens webcam and checks for raised hand.
    Returns gesture name if detected.
    """
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands()

    gesture_name = "None"

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            gesture_name = "Emergency Gesture (Hand Raised)"
            # Draw landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.imshow("Gesture Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            break  # Stop after first detection for demo

        cv2.imshow("Gesture Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return gesture_name