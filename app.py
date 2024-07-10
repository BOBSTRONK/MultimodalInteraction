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
import os
import re
import subprocess
import tempfile
import wave
import sounddevice as sd

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import subprocess
from PIL import Image, ImageTk
from pynput import mouse

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

keywords_next = [
        "switch to the next slide",
        "go to the next slide",
        "next slide",
        "change to the next slide",
        "move to the next slide",
        "switch to the next page",
        "go to the next page",
        "next page",
        "change to the next page",
        "move to the next page",
        "next slide please",
        "next page please",
        "go on to the next slide",
        "go on to the next page",
        "go on",
        "go next",
    ]

keywords_previous = [
        "switch to the previous slide",
        "go to the previous slide",
        "previous slide",
        "change to the previous slide",
        "move to the previous slide",
        "switch to the previous page",
        "go to the previous page",
        "previous page",
        "change to the previous page",
        "move to the previous page",
        "previous slide please",
        "previous page please",
        "go back to the previous slide",
        "go back to the previous page",
        "go back",
        "go previous",
    ]

def check_for_keywords(sentence):
    sentence = sentence.lower().strip()
    for keyword in keywords_next:
        if sentence == keyword:
            os.system(
                        'osascript -e \'display notification "Switch to Next slide" with title "Voice recognition"\''
                    )
            subprocess.run(["osascript", "-e", script_next])

    for keyword in keywords_previous:
        if sentence == keyword:
            os.system(
                        'osascript -e \'display notification "Switch to Previous slide" with title "Voice recognition"\''
                    )
            subprocess.run(["osascript", "-e", script_previous])

# input_filename: file paths for the input audio
# output_filename: output text file
def transcribe_to_txt(input_filename: str, output_filename: str):
    print("Running whisper transcription...")
    # Compose the command of all components
    # necessary command-line arguments to run the transcription tool
    command = [
        # executable
        "whisper.cpp/main",
        "-m",
        "whisper.cpp/models/ggml-medium.en.bin",
        "-f",
        input_filename,
        "-otxt",
        "-of",
        output_filename,
        "-np",
    ]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)
    # Print the output and error messages for debugging


# indata: the audiodata
# frames: The number of frames in the audio data
# time: timing information
# status: the status of audio stream
def callback(indata, frames, time, status):
    # Raise for status if required
    if status:
        print(status)
    
    # Create a tempfile to save the audio to, with autodeletion
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav', prefix='audio_', dir='.') as tmpfile:
        # Save the 5 second audio to a .wav file
        with wave.open(tmpfile.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(16000)  # Sample rate
            wav_file.writeframes(indata)
        
        # Prepare the output filename
        output_filename = tmpfile.name.replace('.wav', '')
        
        # Transcribe the audio to text using our whisper.cpp wrapper
        transcribe_to_txt(tmpfile.name, output_filename)

        # Print the transcribed text
        with open(output_filename + '.txt', 'r') as file:
            text_content = file.read().lower()
            print(text_content)  # Print the transcribed text content
            sentences = re.split(r'[.!?]', text_content)  # Split text into sentences
            
            for sentence in sentences:
                check_for_keywords(sentence)
                
        # Clean up temporary files
    os.remove(output_filename + '.txt')

def on_click(x, y, button, pressed):
    if pressed:
        if button == mouse.Button.left:
            os.system(
                'osascript -e \'display notification "Switch to Next slide" with title "Mouse click"\''
            )
        elif button == mouse.Button.right:
            os.system(
                'osascript -e \'display notification "Switch to Previous slide" with title "Mouse click"\''
            )

def start_mouse_listener():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

def presentation_check():
    if filePath == "":
        os.system(
                'osascript -e  \'display alert "File should not be empty" message "Please select a file"\''
            )
    else:
        process_presentation()

def process_presentation():
    global is_on
    #click_detector = click_keyPress_detection.ClickKeyPressDetector()
    #voice_recognizer = voice_recognition.VoiceRecognizer()
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
    print(gestureToDetectForNext)

    gestureToDetectForPrevious = Options_previous_correspondence[
        gesture_for_previous_slide
    ]
    print(gestureToDetectForPrevious)

    frame_queue = collections.deque(
        maxlen=1
    )  # Use deque with maxlen to keep only the latest frame

    # Start listening for clicks in a separate thread
    # daemon thread. Daemon threads run in the background and do not block the program from exiting.
    # If all non-daemon threads have finished, the program can exit even if daemon threads are still running.
    # This is useful for background tasks that should not prevent the program from terminating.
    #threading.Thread(target=click_detector.start_listening, daemon=True).start()
    # if user choice to use voice contro, then it will start to listening
    # print(is_on)
    # if is_on:
    #     threading.Thread(target=voice_recognizer.microphone, daemon=True).start()
    # print("not voice's problem")

    def capture_frames():
        cap = cv2.VideoCapture(1)  # need to change 0 or 1
        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame_queue.append(frame)  # Add frame to deque

    # Start frame capture in a separate thread
    threading.Thread(target=capture_frames, daemon=True).start()
    threading.Thread(target=start_mouse_listener, daemon=True).start()

    if is_on:
        def record():
            try:
        # Start recording with a rolling 5-second buffer
                with sd.InputStream(
                    callback=callback,
                    dtype="int16",
                    channels=1,
                    samplerate=16000,
                    blocksize=16000 * 3,
                ):
                    print("Recording... Press Ctrl+C to stop.")
                    while True:
                        pass
            except KeyboardInterrupt:
                print("Recording stopped.")
        threading.Thread(target=record, daemon=True).start()

    def update():
        #Process frames on the main thread
        if frame_queue:
            frame = frame_queue.pop()
            frame = gesture_detector.process_frame(
                frame,
                gestureToDetectForNext,
                gestureToDetectForPrevious,
            )
        
        # priority
        detected_value = None
        if gesture_detector.value:
            detected_value = gesture_detector.value
            gesture_detector.value = None

        if detected_value == "previous":
            subprocess.run(["osascript", "-e", script_previous])
            print(detected_value)
        elif detected_value == "next":
            subprocess.run(["osascript", "-e", script_next])
            print(detected_value)

        #time.sleep(0.01)  # Small sleep to prevent CPU overuse
        root.after(1, update)
    update()


def voice_control_switch():
    global is_on

    if is_on:
        is_on = False
    else:
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
        selected_file_label.configure(text=file_path)
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
root = ctk.CTk()
root.title("MPPTC")

# Set the window size and make it non-resizable
root.geometry("860x700")
root.resizable(True, False)

# Define colors
# white
white = "#ffffff"
# celeste
left_panel_color = "#81aef7"
button_color = "#4285F4"
button_text_color = "#000308"

# Create a frame for the left panel
# Frame is like a container
left_frame = ctk.CTkFrame(root, fg_color=left_panel_color, width=300, height=400)
left_frame.pack(side="left", fill="y")

# Add elements to the left frame
welcome_label = ctk.CTkLabel(
    left_frame,
    text="   Hands-Free Presentation   ",
    font=("Helvetica", 26, "bold"),
    text_color=white,
    justify=tk.LEFT,
)
welcome_label.pack(padx=12, pady=30)

description_label = ctk.CTkLabel(
    left_frame,
    text="  Integrating Gesture and Voice Control with PowerPoint\n",
    font=("Helvetica", 20),
    text_color=white,
    wraplength=300,
)
description_label.pack(padx=(40,15), anchor="w")

description_label = ctk.CTkLabel(
    left_frame,
    text=(
        "- This is an application that allows you to control your PowerPoint presentation using gestures or voice.\n\n"
        "- You can choose the gesture to control the application and make sure that when you perform the gesture, you can be captured by camera.\n\n"
        "- You can activate or disable speech recognition.\n\n"  # fix
        "- Press the start button, the application will start to recognize your gesture and voice."
    ),
    font=("Helvetica", 16),
    justify=tk.LEFT,
    text_color=white,
    wraplength=320,
)
description_label.pack(padx=20, pady=10, anchor="w")

# Create a frame for the right panel
right_frame = ctk.CTkFrame(root, width=560, height=400)
right_frame.pack(side="right", fill="both", expand=True)

# Add a label to the right panel34
details_label = ctk.CTkLabel(
    right_frame,
    text="Choose the Gesture",
    font=("Helvetica", 18, "bold"),
)
details_label.pack(padx=40, pady=(30, 2), anchor="nw")


# Function to update the image based on the selected gesture
def update_image_next(*args):
    selected_gesture = default_next_gesture_value.get()
    next_gesture_image_label.configure(image=gesture_images_next[selected_gesture])
    next_gesture_image_label.image = gesture_images_next[
        selected_gesture
    ]  # Keep a reference to the image to prevent garbage collection


# Create a frame to hold the "gesture for next" label and button
gesture_next_select_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
gesture_next_select_frame.pack(pady=10, padx=40, anchor="w")

next_1_left = image_processing("images/next1_left.png")
next_2_right = image_processing("images/next2_right.png")


gesture_images_next = {
    "Left/Right Hand Index Point": next_1_left,
    "Left/Right Hand Thumb Toward": next_2_right,
}
Options_next = [
    "Left/Right Hand Index Point",
    "Left/Right Hand Thumb Toward",
]

# to get the value of the OptionMenu
default_next_gesture_value = ctk.StringVar()
# default value for select gesture menu
default_next_gesture_value.set(Options_next[0])
default_next_gesture_value.trace_add("write", update_image_next)
# Create the label
select_next_gesture_label = ctk.CTkLabel(
    gesture_next_select_frame,
    text="Select the 'Next' Gesture",
    font=("Helvetica", 15),
    fg_color="transparent",
)
# Create the option menu
select_next_gesture_menu = ctk.CTkOptionMenu(
    gesture_next_select_frame,
    variable=default_next_gesture_value,
    values=Options_next,
)
# Pack the widgets
select_next_gesture_label.pack(
    side=ctk.LEFT, padx=(0, 15)
)  # Add space between label and menu
select_next_gesture_menu.pack(side=ctk.LEFT)

next_gesture_image_label = ctk.CTkLabel(right_frame, image=next_1_left, text="")
next_gesture_image_label.pack()
update_image_next()


# Create a frame to hold the "gesture for previous" label and button
def update_image_previous(*args):
    selected_gesture = default_previous_gesture_value.get()
    previous_gesture_image_label.configure(
        image=gesture_images_previous[selected_gesture]
    )
    previous_gesture_image_label.image = gesture_images_previous[
        selected_gesture
    ]  # Keep a reference to the image to prevent garbage collection


gesture_previous_select_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
gesture_previous_select_frame.pack(pady=(20,10), padx=25, anchor="w")

previous_1_right = image_processing("images/previous1_right.png")
previous_2_left = image_processing("images/previous2_left.png")

gesture_images_previous = {
    "Left/Right Hand Index Point": previous_1_right,
    "Left/Right Hand Thumb Toward": previous_2_left,
}
Options_previous = [
    "Left/Right Hand Index Point",
    "Left/Right Hand Thumb Toward",
]

default_previous_gesture_value = ctk.StringVar()
default_previous_gesture_value.set(Options_previous[0])
default_previous_gesture_value.trace_add("write", update_image_previous)
# Create the label
select_previous_gesture_label = ctk.CTkLabel(
    gesture_previous_select_frame,
    text="Select the 'Previous' Gesture",
    font=("Helvetica", 15),
    fg_color="transparent",
)
# Create the option menu
select_previous_gesture_menu = ctk.CTkOptionMenu(
    gesture_previous_select_frame,
    variable=default_previous_gesture_value,
    values=Options_previous,
)
# Pack the widgets
select_previous_gesture_label.pack(
    side=ctk.LEFT, padx=(0, 10)
)  # Add space between label and menu
select_previous_gesture_menu.pack(side=ctk.LEFT)

previous_gesture_image_label = ctk.CTkLabel(
    right_frame, image=previous_1_right, text=""
)
previous_gesture_image_label.pack()
update_image_previous()

# create a container for Voice recognition
voice_recognition_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
voice_recognition_frame.pack(pady=(10, 0), padx=40, anchor="w")

use_voice_recognition_label = ctk.CTkLabel(
    # parent widget
    voice_recognition_frame,
    text="Use Speech Recognition:  ",
    font=("Helvetica", 15, "bold"),
)
use_voice_recognition_label.pack(side=ctk.LEFT, pady=10)


switch_var = ctk.StringVar(value="false")

my_switch = ctk.CTkSwitch(
    voice_recognition_frame,
    text="",
    command=voice_control_switch,
    variable=switch_var,
    onvalue="on",
    offvalue="off",
    switch_width=46,
    switch_height=23,
)
my_switch.pack(side=ctk.LEFT, padx=5)

file_select_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
file_select_frame.pack(pady=5, padx=40, anchor="w")

select_file_label = ctk.CTkLabel(
    # parent widget
    file_select_frame,
    text="Select the PowerPoint ",
    font=("Helvetica", 15, "bold"),
)
select_file_label.pack(side=ctk.LEFT, pady=5)
select_file_button = ctk.CTkButton(
    master=file_select_frame,
    text="📂",
    font=(
        "Helvetica",
        25,
    ),
    command=open_file_dialog,
    width=8,
    fg_color="white",
)
select_file_button.pack(side=ctk.LEFT, padx=1)

selected_file_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
selected_file_frame.pack(pady=0, padx=40, anchor="w")
selected_file_label = ctk.CTkLabel(selected_file_frame, text="Select File Path: ")
selected_file_label.pack(side=ctk.LEFT, pady=0)

start_detection_button = ctk.CTkButton(
    right_frame,
    text="Start Detection",
    fg_color="white",
    text_color="black",
    font=("Helvetica", 18, "bold"),
    command=presentation_check,
)
start_detection_button.pack(pady=20)

root.mainloop()
