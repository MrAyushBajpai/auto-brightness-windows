import cv2
import numpy as np
import screen_brightness_control as sbc
import os
import logging
from datetime import datetime

# Set up logging
log_file = "log.txt"
logging.basicConfig(
    filename=log_file, level=logging.INFO, format="[%(asctime)s]: %(message)s"
)

def clear_large_log_file(log_path, max_size_in_bytes):
    """Clear the log file if its size exceeds the specified limit."""
    try:
        log_size = os.path.getsize(log_path)
        if log_size > max_size_in_bytes:
            open(log_path, "w").close()
            logging.info("Log file cleared due to large size")
    except Exception as e:
        logging.error("Error while clearing log file: %s", str(e))

# Clear log file if its size is larger than 1 MB
clear_large_log_file(log_file, 1024 * 1024)

# Log program start
logging.info("Program started")

# Initialize the camera
cap = cv2.VideoCapture(0)

# Calibration settings
calibration_file = "brightness_calibration.txt"
default_low_brightness = 50  # default minimum brightness value
default_high_brightness = 255  # default maximum brightness value
calibration_data_updated = False  # To track if calibration data is updated

try:
    # Create a default calibration file if it doesn't exist
    if not os.path.exists(calibration_file):
        with open(calibration_file, "w") as f:
            f.write("# Calibration data for Adaptive Brightness Control\n")
            f.write(f"low_brightness = {default_low_brightness}\n")
            f.write(f"high_brightness = {default_high_brightness}\n")
        logging.info("Default calibration data saved.")

    # Load saved calibration data
    with open(calibration_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("low_brightness"):
                low_brightness = float(line.split("=")[1].strip())
            elif line.startswith("high_brightness"):
                high_brightness = float(line.split("=")[1].strip())
        logging.info("Calibration data loaded.")

    # Ask the user if they want to use the previous data or recalibrate
    use_previous = (
        input("Do you want to use previous / default calibration data? (y/n): ")
        .strip()
        .lower()
        == "y"
    )

    if not use_previous:
        # Perform low brightness calibration
        print(
            "Please aim the camera at a low-light environment and press ENTER to calibrate."
        )
        input()
        _, low_frame = cap.read()
        low_gray = cv2.cvtColor(low_frame, cv2.COLOR_BGR2GRAY)
        low_brightness = np.mean(low_gray)
        logging.info("Low brightness calibrated to: %f", low_brightness)
        calibration_data_updated = True

        # Perform high brightness calibration
        print(
            "Please aim the camera at a well-lit environment and press ENTER to calibrate."
        )
        input()
        _, high_frame = cap.read()
        high_gray = cv2.cvtColor(high_frame, cv2.COLOR_BGR2GRAY)
        high_brightness = np.mean(high_gray)
        logging.info("High brightness calibrated to: %f", high_brightness)
        calibration_data_updated = True

        # Save calibration data
        with open(calibration_file, "w") as f:
            f.write("# Calibration data for Adaptive Brightness Control\n")
            f.write(f"low_brightness = {low_brightness}\n")
            f.write(f"high_brightness = {high_brightness}\n")
        logging.info("Calibration data saved.")

    while True:
        # Read the camera frame
        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture frame from camera")
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate the average brightness of the frame
        avg_brightness = np.mean(gray)

        # Map the brightness range to the screen brightness range
        brightness_range = high_brightness - low_brightness
        brightness_offset = low_brightness
        screen_brightness = int(
            ((avg_brightness - brightness_offset) / brightness_range) * 100
        )

        # Adjust the screen brightness within the valid range (0-100)
        screen_brightness = max(min(screen_brightness, 100), 0)
        sbc.set_brightness(screen_brightness)

        # Display the current screen brightness
        cv2.putText(
            frame,
            f"Screen Brightness: {screen_brightness}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

        # Display the 'Press q to exit' instruction
        cv2.putText(
            frame,
            "Press q to exit",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

        # Display the camera frame
        cv2.imshow("frame", frame)

        # Exit if the 'q' key is pressed
        if cv2.waitKey(1) == ord("q"):
            break

except Exception as e:
    error_message = str(e)
    logging.error(error_message)
    print(f"An error occurred: {error_message}")

finally:
    # Log whether default, previous, or new data was used
    if use_previous:
        logging.info("Using previous calibration data")
    elif not use_previous and calibration_data_updated:
        logging.info("Using new calibration data")

    # Log program end
    logging.info("Program ended")

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()
