import cv2
import time

cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)
time.sleep(1)

# warm-up reads
for _ in range(5):
    cap.read()

while True:
    success, frame = cap.read()
    if not success:
        continue

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()