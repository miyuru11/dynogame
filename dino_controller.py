import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

print("="*50)
print("   CHROME DINO GAME - PALM CONTROLLER")
print("="*50)

# Initialize MediaPipe (New API for latest version)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# If the above fails, use the older version
try:
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    print("✓ MediaPipe initialized (standard API)")
except AttributeError:
    # Fallback for newer MediaPipe
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    detector = vision.HandLandmarker.create_from_options(options)
    print("✓ MediaPipe initialized (new API)")

print("\n🔥 How to play:")
print("   1. Open Chrome and go to: chrome://dino")
print("   2. Press SPACE to start the game")
print("   3. Make sure Chrome window is ACTIVE")
print("   4. Show your OPEN PALM to the camera")
print("   5. Dino jumps when palm is detected!")

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("ERROR: Camera not found!")
    exit()

# Game control variables
last_jump_time = 0
jump_cooldown = 0.5

def is_palm_open(hand_landmarks):
    """Check if hand is showing open palm (all fingers extended)"""
    
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    
    index_tip = hand_landmarks.landmark[8]
    index_mcp = hand_landmarks.landmark[5]
    
    middle_tip = hand_landmarks.landmark[12]
    middle_mcp = hand_landmarks.landmark[9]
    
    ring_tip = hand_landmarks.landmark[16]
    ring_mcp = hand_landmarks.landmark[13]
    
    pinky_tip = hand_landmarks.landmark[20]
    pinky_mcp = hand_landmarks.landmark[17]
    
    index_up = index_tip.y < index_mcp.y
    middle_up = middle_tip.y < middle_mcp.y
    ring_up = ring_tip.y < ring_mcp.y
    pinky_up = pinky_tip.y < pinky_mcp.y
    thumb_up = thumb_tip.y < thumb_ip.y
    
    return thumb_up and index_up and middle_up and ring_up and pinky_up

print("\n✅ Ready! Open Chrome Dino game now!")
print("   Press SPACE to start the game\n")
time.sleep(2)

print("🎮 GAME CONTROL ACTIVE!")
print("   Show your palm to make the dino jump!")
print("   Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect hands
    try:
        results = hands.process(rgb_frame)
        detected = results.multi_hand_landmarks
    except:
        # For newer API fallback
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)
        detected = detection_result.hand_landmarks
    
    display_text = "🤚 No hand detected"
    text_color = (100, 100, 100)
    palm_open = False
    
    if detected:
        for hand_landmarks in detected:
            # Draw landmarks
            try:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
            except:
                # Simple drawing fallback
                for landmark in hand_landmarks:
                    h, w = frame.shape[:2]
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
            
            palm_open = is_palm_open(hand_landmarks)
            
            if palm_open:
                display_text = "🖐️ PALM DETECTED! JUMPING!"
                text_color = (0, 255, 0)
                
                current_time = time.time()
                if current_time - last_jump_time > jump_cooldown:
                    pyautogui.press('space')
                    last_jump_time = current_time
                    print("🦘 DINO JUMPED!")
            else:
                display_text = "✋ Show OPEN PALM to jump!"
                text_color = (0, 165, 255)
    else:
        display_text = "🤚 Show your hand to the camera!"
        text_color = (100, 100, 100)
    
    # Display overlay
    cv2.rectangle(frame, (10, 10), (500, 120), (0, 0, 0), -1)
    cv2.putText(frame, display_text, (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
    cv2.putText(frame, "Chrome Dino Controller", (20, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(frame, "Press 'q' to quit", (frame.shape[1]-150, frame.shape[0]-20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    
    if palm_open:
        cv2.putText(frame, "🦘 JUMPING!", (frame.shape[1]-200, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Chrome Dino - Palm Controller', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✅ Game controller closed!")