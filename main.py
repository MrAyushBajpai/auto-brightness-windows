import cv2
import numpy as np
import screen_brightness_control as sbc

# Initialize the camera
cap = cv2.VideoCapture(0)

# Calibration settings
low_brightness = 50  # minimum brightness value
high_brightness = 255  # maximum brightness value

# Perform low brightness calibration
print('Please aim the camera at a low-light environment and press ENTER to calibrate.')
input()
_, low_frame = cap.read()
low_gray = cv2.cvtColor(low_frame, cv2.COLOR_BGR2GRAY)
low_brightness = np.mean(low_gray)
print('Low brightness calibrated to:', low_brightness)

# Perform high brightness calibration
print('Please aim the camera at a well-lit environment and press ENTER to calibrate.')
input()
_, high_frame = cap.read()
high_gray = cv2.cvtColor(high_frame, cv2.COLOR_BGR2GRAY)
high_brightness = np.mean(high_gray)
print('High brightness calibrated to:', high_brightness)

while True:
    # Read the camera frame
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate the average brightness of the frame
    avg_brightness = np.mean(gray)

    # Map the brightness range to the screen brightness range
    brightness_range = high_brightness - low_brightness
    brightness_offset = low_brightness
    screen_brightness = int(((avg_brightness - brightness_offset) / brightness_range) * 60 + 20)

    # Adjust the screen brightness within the valid range (0-100)
    screen_brightness = max(min(screen_brightness, 100), 0)
    sbc.set_brightness(screen_brightness)

    # Display the current screen brightness
    cv2.putText(frame, f'Screen Brightness: {screen_brightness}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Display the camera frame
    cv2.imshow('frame', frame)

    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
