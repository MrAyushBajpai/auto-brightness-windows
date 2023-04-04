import cv2
import numpy as np
import screen_brightness_control as sbc

# Initialize the camera
cap = cv2.VideoCapture(0)

while True:
    # Read the camera frame
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate the average brightness of the frame
    avg_brightness = np.mean(gray)

    # Adjust the screen brightness accordingly
    sbc.set_brightness(int(avg_brightness))

    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
