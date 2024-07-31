import cv2
import numpy as np
import screen_brightness_control as sbc
import os
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image
import pystray
import threading
import webbrowser
import sys

# Global flag to indicate whether the application is running
running = True

def exit_program(icon=None):
    global running
    running = False
    if icon:
        icon.stop()
    root.quit()
    root.destroy()
    sys.exit()  # Ensure the script exits

def hide_to_tray():
    root.withdraw()
    create_tray_icon()

def restore_from_tray(icon):
    logging.info("Restoring window from tray")
    root.deiconify()
    icon.stop()  # Stop the icon when restoring

def default_function(icon):
    logging.info("Default function triggered")
    restore_from_tray(icon)

def on_exit(icon):
    exit_program(icon)

def create_tray_icon():
    image = Image.open("icon.ico")  # Ensure this path is correct
    icon = pystray.Icon(
        name="Adaptive Brightness Control",
        icon=image,
        title="Adaptive Brightness Control",
        menu=pystray.Menu(
            pystray.MenuItem(text="Launch App", action=default_function, default=True)
        )
    )
    
    # Override the left-click behavior to trigger the default function
    icon.on_left_click = lambda: default_function(icon, None)
    
    # Start the tray icon on a separate thread
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.start()
    return icon_thread

def main():
    global root, cap

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


    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")

    root = ThemedTk(theme="black")
    root.title("Adaptive Brightness Control Calibration")

    window_width = 400
    window_height = 250
    root.geometry(f"{window_width}x{window_height}")  # Set the initial size
    center_window(root, window_width, window_height)  # Center the window

    # Set window icon
    root.iconbitmap("icon.ico")

    # Disable the maximize button
    root.resizable(False, False)  # Disable resizing in both directions

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), padding=10)

    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    calibrate_button = ttk.Button(frame, text="Start Calibration", command=start_calibration)
    calibrate_button.pack(pady=10, fill=tk.X)

    hide_button = ttk.Button(frame, text="Hide to Tray", command=hide_to_tray)
    hide_button.pack(pady=10, fill=tk.X)

    exit_button = ttk.Button(frame, text="Exit", command=lambda: exit_program(None))
    exit_button.pack(pady=10, fill=tk.X)

    def open_github_link(event):
        webbrowser.open("https://github.com/MrAyushBajpai/auto-brightness-windows")

    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    footer_label = tk.Label(bottom_frame, text="Designed with love by Ayush Bajpai. ", fg="white", bg="#424242")
    footer_label.pack(anchor=tk.CENTER)

    github_link = tk.Label(bottom_frame, text="GitHub", fg="#0096FF", bg="#424242", cursor="hand2")
    github_link.pack(anchor=tk.CENTER)
    github_link.bind("<Button-1>", open_github_link)

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
            try:
                sbc.set_brightness(screen_brightness)
            except sbc.ScreenBrightnessError as e:
                logging.error("Failed to set screen brightness: %s", str(e))
            
            root.after(100, main_loop)

    root.after(100, main_loop)

    # Override the close button to minimize to tray
    root.protocol("WM_DELETE_WINDOW", hide_to_tray)

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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        input("Press Enter to exit...")
        sys.exit()
