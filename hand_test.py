import cv2 #handles camera + image display
import mediapipe as mp #hand detection AI
import time
import serial

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

def distance(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5 #distance between two points

def count_fingers(hand):
    tips = [8, 12, 16, 20]
    joints = [6, 10, 14, 18]

    count = 0 
    for tip, joint in zip(tips, joints):
        if hand[tip].y < hand[joint].y: # if fingertip is above the joint then finger is up
            count += 1

    #thumb
    if distance(hand[4], hand[17]) > distance(hand[3], hand[17]): # if thumb tip far from pinky base then thumb is up
        count += 1

    return count

options = HandLandmarkerOptions(
    base_options = BaseOptions(model_asset_path = 'hand_landmarker.task', delegate = BaseOptions.Delegate.CPU), # work on CPU not GPU
    running_mode = VisionRunningMode.VIDEO, 
    num_hands = 1
)
landmarker = HandLandmarker.create_from_options(options) # finds the hand in the video 

arduino = serial.Serial('/dev/tty.usbmodem11101', 9600) 
time.sleep(2)  # give Arduino time to reset after the connection opens

cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)
time.sleep(1)
for _ in range(5):
    cap.read()

frame_index = 0
last_sent = -1  

# loop until 'q' is pressed
while True:
    success, frame = cap.read() #grab frame from camera
    if not success:
        continue

    frame = cv2.flip(frame, 1) # mirror image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert BGR to RGB
    mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data = rgb_frame) # convert to mediapipe image format

    timestamp_ms = int(frame_index * (1000 / 30))
    result = landmarker.detect_for_video(mp_image, timestamp_ms) #detect hands in frame
    frame_index += 1

    if result.hand_landmarks: #if hands are found
        for hand in result.hand_landmarks:
            for lm in hand:
                x = int(lm.x * frame.shape[1])
                y = int(lm.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1) #draw the circles on the marks

            finger_count = count_fingers(hand) #run counting function
            if finger_count != last_sent:
                arduino.write(f"{finger_count}\n".encode())
                last_sent = finger_count
            cv2.putText(frame, str(finger_count), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0, 0), 5) # draw the finger count

    cv2.imshow("Hand Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()