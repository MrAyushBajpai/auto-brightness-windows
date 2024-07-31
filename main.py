import cv2
import numpy as np
import screen_brightness_control as sbc
import os
import logging
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading

# Set up logging
log_file = "log.txt"
logging.basicConfig(
    filename=log_file, level=logging.INFO, format="[%(asctime)s]: %(message)s"
)

def clear_large_log_file(log_path, max_size_in_bytes):
    """Clear the log file if its size exceeds the specified limit."""
    try:
        log_size = os.path.getsize(log_path)
        if (log_size > max_size_in_bytes):
            open(log_path, "w").close()
            logging.info("Log file cleared due to large size")
    except Exception as e:
        logging.error("Error while clearing log file: %s", str(e))

def calibrate_low_brightness():
    global low_brightness, calibration_data_updated
    messagebox.showinfo("Calibration", "Please aim the camera at a low-light environment and press OK to calibrate.")
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture frame for low brightness calibration")
        messagebox.showerror("Error", "Failed to capture frame for low brightness calibration")
        return
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    low_brightness = np.mean(gray)
    logging.info("Low brightness calibrated to: %f", low_brightness)
    calibration_data_updated = True
    messagebox.showinfo("Calibration", f"Low brightness calibrated to: {low_brightness:.2f}")

def calibrate_high_brightness():
    global high_brightness, calibration_data_updated
    messagebox.showinfo("Calibration", "Please aim the camera at a well-lit environment and press OK to calibrate.")
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture frame for high brightness calibration")
        messagebox.showerror("Error", "Failed to capture frame for high brightness calibration")
        return
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    high_brightness = np.mean(gray)
    logging.info("High brightness calibrated to: %f", high_brightness)
    calibration_data_updated = True
    messagebox.showinfo("Calibration", f"High brightness calibrated to: {high_brightness:.2f}")

def save_calibration_data():
    with open(calibration_file, "w") as f:
        f.write("# Calibration data for Adaptive Brightness Control\n")
        f.write(f"low_brightness = {low_brightness}\n")
        f.write(f"high_brightness = {high_brightness}\n")
    logging.info("Calibration data saved.")
    messagebox.showinfo("Calibration", "Calibration data saved.")

def start_calibration():
    calibrate_low_brightness()
    calibrate_high_brightness()
    save_calibration_data()

def exit_program():
    global running
    running = False
    root.destroy()

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

# Load or create calibration data
low_brightness = default_low_brightness
high_brightness = default_high_brightness

if not os.path.exists(calibration_file):
    with open(calibration_file, "w") as f:
        f.write("# Calibration data for Adaptive Brightness Control\n")
        f.write(f"low_brightness = {default_low_brightness}\n")
        f.write(f"high_brightness = {default_high_brightness}\n")
    logging.info("Default calibration data saved.")
else:
    with open(calibration_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("low_brightness"):
                low_brightness = float(line.split("=")[1].strip())
            elif line.startswith("high_brightness"):
                high_brightness = float(line.split("=")[1].strip())
    logging.info("Calibration data loaded.")

# Create the Tkinter GUI
root = tk.Tk()
root.title("Adaptive Brightness Control Calibration")

calibrate_button = tk.Button(root, text="Start Calibration", command=start_calibration)
calibrate_button.pack(pady=20)

exit_button = tk.Button(root, text="Exit", command=exit_program)
exit_button.pack(pady=20)

running = True
def main_loop():
    if running:
        # Read the camera frame
        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture frame from camera")
            root.after(100, main_loop)
            return

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

        root.after(100, main_loop)

root.after(100, main_loop)

# Function to minimize to tray
def minimize_to_tray():
    root.withdraw()
    create_tray_icon()

def restore_from_tray(icon, item):
    icon.stop()
    root.deiconify()

def on_exit(icon, item):
    icon.stop()
    exit_program()

def create_tray_icon():
    image = Image.open("icon.png")
    menu = (item('Calibrate', restore_from_tray), item('Exit', on_exit))
    icon = pystray.Icon("name", image, "Adaptive Brightness Control", menu)
    threading.Thread(target=icon.run).start()

# Override the close button to minimize to tray
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

root.mainloop()

# Log whether default, previous, or new data was used
if calibration_data_updated:
    logging.info("Using new calibration data")
else:
    logging.info("Using previous calibration data")

# Log program end
logging.info("Program ended")

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
