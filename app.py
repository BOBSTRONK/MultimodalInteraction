# root = tk.Tk()
# root.title("MPPTC")

# app_description = tk.Label(root, text="Multimodal PPT controller")
# app_description.pack()
# open_button = tk.Button(root, text="Open PowerPoint", command=open_file_dialog)
# open_button.pack(padx=20, pady=20)
# selected_file_label = tk.Label(root, text="No PowerPoint is selected:")

# selected_file_label.pack()
# root.mainloop()

from functools import partial
import Models.click_keyPress_detection as click_keyPress_detection
import Models.gesture_detection as gesture_detection
import Models.voice_recognition as voice_recognition
import collections
import threading
import cv2
import time

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
from PIL import Image, ImageTk

is_on = False
filePath = ""
# Move to the next slide
script_next = """
tell application "Microsoft PowerPoint"
	go to next slide slide show view of slide show window 1
end tell
"""

script_previous = """
tell application "Microsoft PowerPoint"
	go to previous slide slide show view of slide show window 1
end tell
"""


def process_presentation():
    global is_on
    click_detector = click_keyPress_detection.ClickKeyPressDetector()
    voice_recognizer = voice_recognition.VoiceRecognizer()
    gesture_detector = gesture_detection.GestureRecognizer(use_gpu=False)
    # open the power point
    open_ppt(filePath)
    gesture_for_next_slide = default_next_gesture_value.get()
    gesture_for_previous_slide = default_previous_gesture_value.get()

    Options_next_correspondence = {
        "Left/Right Hand Index Point": "next1",
        "Left/Right Hand Thumb Toward": "next2",
    }

    Options_previous_correspondence = {
        "Left/Right Hand Index Point": "previous1",
        "Left/Right Hand Thumb Toward": "previous2",
    }
    gestureToDetectForNext = Options_next_correspondence[gesture_for_next_slide]
    gestureToDetectForPrevious = Options_previous_correspondence[
        gesture_for_previous_slide
    ]

    frame_queue = collections.deque(
        maxlen=1
    )  # Use deque with maxlen to keep only the latest frame

    # Start listening for clicks in a separate thread
    # daemon thread. Daemon threads run in the background and do not block the program from exiting.
    # If all non-daemon threads have finished, the program can exit even if daemon threads are still running.
    # This is useful for background tasks that should not prevent the program from terminating.
    threading.Thread(target=click_detector.start_listening, daemon=True).start()
    # if user choice to use voice contro, then it will start to listening
    if is_on:
        threading.Thread(target=voice_recognizer.microphone, daemon=True).start()

    def capture_frames():
        cap = cv2.VideoCapture(0)  # need to change 0 or 1
        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame_queue.append(frame)  # Add frame to deque

    # Start frame capture in a separate thread
    threading.Thread(target=capture_frames, daemon=True).start()

    while True:
        # Process frames on the main thread
        if frame_queue:
            frame = frame_queue.pop()
            frame = gesture_detector.process_frame(
                frame,
                gestureToDetectForNext,
                gestureToDetectForPrevious,
            )
            # cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # priority
        detected_value = None
        if voice_recognizer.value:
            detected_value = voice_recognizer.value
            voice_recognizer.value = None
        elif click_detector.value:
            # detected_value = click_detector.value
            click_detector.value = None
        elif gesture_detector.value:
            detected_value = gesture_detector.value
            gesture_detector.value = None

        if detected_value == "previous":
            subprocess.run(["osascript", "-e", script_previous])
            print(detected_value)
        elif detected_value == "next":
            subprocess.run(["osascript", "-e", script_next])
            print(detected_value)

        time.sleep(0.01)  # Small sleep to prevent CPU overuse

    cv2.destroyAllWindows()


def start_process_presentation():
    threading.Thread(target=process_presentation, daemon=True).start()


def voice_control_switch():
    global is_on

    if is_on:
        voice_control_button.config(image=toggle_off_img)
        is_on = False
    else:
        voice_control_button.config(image=toggle_on_img)
        is_on = True


# AppleScript commands to control PowerPoint
def open_ppt(presentationPath):
    open_script = f"""
    tell application "Microsoft PowerPoint"
        activate
        open "{presentationPath}"
        set slideShowSettings to slide show settings of active presentation
        set starting slide of slideShowSettings to 4
        set ending slide of slideShowSettings to 4
        run slide show slideShowSettings
    end tell
    """
    subprocess.run(["osascript", "-e", open_script])


def open_file_dialog():
    global filePath
    # open a dialog for selecting a file
    file_path = filedialog.askopenfilename(
        # title of the dialog window
        title="Select a File",
        # types of files to filter in the dialog
        filetypes=[
            ("PowerPoint files", "*.pptx"),
        ],
    )
    # if a file path is selected
    if file_path:
        # display the path of the selected file
        selected_file_label.config(text="Selected File: " + file_path)
        filePath = file_path


def image_processing(image_path):
    image = Image.open(image_path)
    resize_image = image.resize((150, 150))
    img = ImageTk.PhotoImage(resize_image)
    return img


# Function to update the image when the selection changes
def update_image_next(*args):
    selected_gesture = default_next_gesture_value.get()
    next_gesture_image_label.config(image=gesture_images_next[selected_gesture])


def update_image_previous(*args):
    selected_gesture = default_previous_gesture_value.get()
    previous_gesture_image_label.config(image=gesture_images_previous[selected_gesture])


# Initialize the main application window
root = tk.Tk()
root.title("MPPTC")

# Set the window size and make it non-resizable
root.geometry("860x700")
root.resizable(True, False)

# Define colors
# white
background_color = "#ffffff"
# celeste
left_panel_color = "#4285F4"
button_color = "#4285F4"
button_text_color = "#000308"

# Create a frame for the left panel
# Frame is like a container
left_frame = tk.Frame(root, bg=left_panel_color, width=300, height=400)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

# Add text to the left panel
welcome_label = tk.Label(
    left_frame,
    text="Welcome to Multimodal PPT controller ",
    font=("Helvetica", 20, "bold"),
    bg=left_panel_color,
    fg="white",
)
welcome_label.pack(padx=20, pady=20, anchor="w")

description_label = tk.Label(
    left_frame,
    text=(
        "- This is an application that allows you to control your PowerPoint presentation using gestures or voice.\n\n"
        "- Press the start button, the application will start to recognize your gesture and voice. \n"
        "- You can choose the gesture to control the application and make sure that when you perform the gesture, you can be captured by your computer's camera. "
    ),
    font=("Helvetica", 16),
    bg=left_panel_color,
    fg="white",
    justify=tk.LEFT,
    wraplength=260,
)
description_label.pack(padx=20, pady=10, anchor="w")

# Create a frame for the right panel
right_frame = tk.Frame(root, width=300, height=400)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a label to the right panel34
details_label = tk.Label(
    right_frame,
    text="Choose the Gesture",
    font=("Helvetica", 15, "bold"),
    fg="white",
)
details_label.pack(padx=20, pady=20, anchor="nw")

# Create a frame to hold the "gesture for next" label and button
gesture_next_select_frame = tk.Frame(right_frame)
gesture_next_select_frame.pack(pady=5, padx=40, anchor="w")

# Add input fields to the right panel
entry_style = ttk.Style()
entry_style.configure("Custom.TEntry", fieldbackground="white", borderwidth=0)

next_1_left = image_processing("/Users/weidongcai/Downloads/next1_left.png")
next_1_right = image_processing("/Users/weidongcai/Downloads/next1_right.png")
next_2_left = image_processing("/Users/weidongcai/Downloads/next2_left.png")
next_2_right = image_processing("/Users/weidongcai/Downloads/next2_right.png")


gesture_images_next = {
    "Left/Right Hand Index Point": next_1_left,
    "Left/Right Hand Thumb Toward": next_2_right,
}
Options_next = [
    "Left/Right Hand Index Point",
    "Left/Right Hand Thumb Toward",
]

# to get the value of the OptionMenu
default_next_gesture_value = tk.StringVar()
# default value for select gesture menu
default_next_gesture_value.set(Options_next[0])
default_next_gesture_value.trace_add("write", update_image_next)
select_next_gesture_menu = tk.OptionMenu(
    gesture_next_select_frame, default_next_gesture_value, *Options_next
)
select_next_gesture_label = tk.Label(
    # parent widget
    gesture_next_select_frame,
    text="Select the 'Next' Gesture",
    font=(
        "Helvetica",
        15,
    ),
    fg="white",
)
select_next_gesture_label.pack(side=tk.LEFT)
select_next_gesture_menu.pack(side=tk.LEFT)

next_gesture_image_label = tk.Label(right_frame, image=next_1_left)
next_gesture_image_label.pack()

# Create a frame to hold the "gesture for next" label and button
gesture_previous_select_frame = tk.Frame(right_frame)
gesture_previous_select_frame.pack(pady=5, padx=40, anchor="w")

previous_1_left = image_processing("/Users/weidongcai/Downloads/previous1_left.png")
previous_1_right = image_processing("/Users/weidongcai/Downloads/previous1_right.png")
previous_2_left = image_processing("/Users/weidongcai/Downloads/previous2_left.png")
previous_2_right = image_processing("/Users/weidongcai/Downloads/previous2_right.png")

gesture_images_previous = {
    "Left/Right Hand Index Point": previous_1_right,
    "Left/Right Hand Thumb Toward": previous_2_left,
}
Options_previous = [
    "Left/Right Hand Index Point",
    "Left/Right Hand Thumb Toward",
]


default_previous_gesture_value = tk.StringVar()
# default value for select gesture menu
default_previous_gesture_value.set(Options_previous[0])
default_previous_gesture_value.trace_add("write", update_image_previous)
select_previous_gesture_menu = tk.OptionMenu(
    gesture_previous_select_frame, default_previous_gesture_value, *Options_previous
)
select_previous_gesture_label = tk.Label(
    # parent widget
    gesture_previous_select_frame,
    text="Select the 'Previous' Gesture",
    font=(
        "Helvetica",
        15,
    ),
    fg="white",
)
select_previous_gesture_label.pack(side=tk.LEFT)
select_previous_gesture_menu.pack(side=tk.LEFT)

previous_gesture_image_label = tk.Label(right_frame, image=previous_1_left)
previous_gesture_image_label.pack(pady=(0, 10))

# create a container for Voice recognition
voice_recognition_frame = tk.Frame(right_frame, bd=0, highlightthickness=0)
voice_recognition_frame.pack(pady=5, padx=40, anchor="w")

use_voice_recognition_label = tk.Label(
    # parent widget
    voice_recognition_frame,
    text="Use Voice Recognition:  ",
    font=(
        "Helvetica",
        15,
    ),
    fg="white",
)
use_voice_recognition_label.pack(side=tk.LEFT)


toggle_on_image = Image.open(
    "/Users/weidongcai/Downloads/green-button-on-21528-Photoroom.png"
)
toggle_off_image = Image.open(
    "/Users/weidongcai/Downloads/button-off-red-switch-toggle-21532-Photoroom (1).png",
)


toggle_off_image_resize_image = toggle_off_image.resize((64, 34))
toggle_off_img = ImageTk.PhotoImage(toggle_off_image_resize_image)
toggle_on_image_resize_image = toggle_on_image.resize((64, 34))
toggle_on_img = ImageTk.PhotoImage(toggle_on_image_resize_image)
voice_control_button = tk.Button(
    voice_recognition_frame,
    image=toggle_off_img,
    # text="Off",
    # font=(
    #     "Helvatica",
    #     15,
    # ),
    bd=0,
    borderwidth=0,
    highlightthickness=0,
    relief=tk.FLAT,
    command=voice_control_switch,
)
voice_control_button.pack(pady=10)


# Create a frame to hold the label and button
file_select_frame = tk.Frame(right_frame)
file_select_frame.pack(pady=(10, 10), padx=40, anchor="w")


select_next_gesture_label = tk.Label(
    # parent widget
    file_select_frame,
    text="Select the PowerPoint",
    font=(
        "Helvetica",
        15,
    ),
    fg="white",
)

select_next_gesture_label.pack(side=tk.LEFT)
# Add a button with an icon to the right panel (icon represented as text here)
select_file_button = tk.Button(
    file_select_frame,
    text="📂",
    width=2,
    bg="white",
    command=open_file_dialog,
)
select_file_button.pack(side=tk.LEFT, padx=5)
# select_file_label.grid(row=0,column=0)

selected_file_label = tk.Label(
    right_frame,
    text="Selected File:",
    font=(
        "Helvetica",
        12,
    ),
    fg="white",
)
selected_file_label.pack()

# Add a button to the right panel for start detection
start_detection_button = tk.Button(
    right_frame,
    text="Start Detection",
    bg="white",
    fg="black",
    font=("Helvetica", 12, "bold"),
    relief=tk.FLAT,
    command=start_process_presentation,
)
start_detection_button.pack(pady=20)

# image = Image.open("/Users/weidongcai/Downloads/WechatIMG208501.png")
# resize_image = image.resize((100, 100))
# img = ImageTk.PhotoImage(resize_image)
# image_label = tk.Label(right_frame, image=img)
# image_label.pack()

# Run the application
root.mainloop()
